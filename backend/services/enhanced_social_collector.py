"""
Enhanced Social Media Signal Collector with Rate Limiting, Caching, and Deep Analysis
MVP 3.0 - Cross-Platform Signal Enhancement
"""

import asyncio
from typing import List, Dict, Optional, Tuple
from datetime import datetime, timedelta
from collections import Counter
import re
import json
import hashlib
from functools import wraps
import time
import numpy as np

# Redis for caching (optional but recommended)
try:
    import redis
    REDIS_AVAILABLE = True
except ImportError:
    REDIS_AVAILABLE = False
    print("⚠️ Redis not available. Install: pip install redis")

# Twitter API
try:
    import tweepy
    TWITTER_AVAILABLE = True
except ImportError:
    TWITTER_AVAILABLE = False

# Reddit API
try:
    import praw
    REDDIT_AVAILABLE = True
except ImportError:
    REDDIT_AVAILABLE = False

# Google Trends
try:
    from pytrends.request import TrendReq
    GOOGLE_TRENDS_AVAILABLE = True
except ImportError:
    GOOGLE_TRENDS_AVAILABLE = False
    print("⚠️ Pytrends not available")

# SerpAPI
try:
    from serpapi import GoogleSearch
    SERPAPI_AVAILABLE = True
except ImportError:
    SERPAPI_AVAILABLE = False
    print("⚠️ SerpAPI not available. Install: pip install google-search-results")


class RateLimiter:
    """
    智能速率限制器 - 自动调节请求频率
    """
    def __init__(self, max_calls: int, time_window: int):
        self.max_calls = max_calls
        self.time_window = time_window  # seconds
        self.calls = []
    
    def __call__(self, func):
        @wraps(func)
        async def wrapper(*args, **kwargs):
            now = time.time()
            
            # 清理过期的调用记录
            self.calls = [call_time for call_time in self.calls 
                         if now - call_time < self.time_window]
            
            # 检查是否超过限制
            if len(self.calls) >= self.max_calls:
                wait_time = self.time_window - (now - self.calls[0])
                if wait_time > 0:
                    print(f"⏳ Rate limit reached, waiting {wait_time:.1f}s...")
                    await asyncio.sleep(wait_time + 1)
                    self.calls = []
            
            # 记录本次调用
            self.calls.append(time.time())
            return await func(*args, **kwargs)
        
        return wrapper


class CacheManager:
    """
    缓存管理器 - 减少API调用，提升响应速度
    """
    def __init__(self, redis_url: Optional[str] = None, ttl: int = 3600):
        """
        初始化缓存管理器
        
        Args:
            redis_url: Redis 连接 URL (例如: redis://localhost:6379)
            ttl: 缓存过期时间（秒），默认 1 小时
        """
        self.ttl = ttl  # Time to live in seconds
        self.redis_client = None
        self.local_cache = {}  # Fallback to memory cache
        
        if REDIS_AVAILABLE and redis_url:
            try:
                self.redis_client = redis.from_url(redis_url)
                self.redis_client.ping()
                print("✅ Redis cache connected")
            except Exception as e:
                print(f"⚠️ Redis connection failed: {e}, using local cache")
    
    def _generate_key(self, prefix: str, params: dict) -> str:
        """生成缓存键"""
        params_str = json.dumps(params, sort_keys=True)
        hash_key = hashlib.md5(params_str.encode()).hexdigest()
        return f"{prefix}:{hash_key}"
    
    async def get(self, key: str) -> Optional[dict]:
        """获取缓存"""
        if self.redis_client:
            try:
                data = self.redis_client.get(key)
                if data:
                    return json.loads(data)
            except Exception as e:
                print(f"Cache get error: {e}")
        
        # Fallback to local cache
        if key in self.local_cache:
            item = self.local_cache[key]
            if time.time() - item['timestamp'] < self.ttl:
                return item['data']
            else:
                del self.local_cache[key]
        
        return None
    
    async def set(self, key: str, data: dict):
        """设置缓存"""
        if self.redis_client:
            try:
                self.redis_client.setex(
                    key, 
                    self.ttl, 
                    json.dumps(data)
                )
                return
            except Exception as e:
                print(f"Cache set error: {e}")
        
        # Fallback to local cache
        self.local_cache[key] = {
            'data': data,
            'timestamp': time.time()
        }


class EnhancedTwitterCollector:
    """
    增强版 Twitter 收集器 - 支持速率限制、缓存、深度分析
    """
    def __init__(self, bearer_token: Optional[str] = None, cache_manager: Optional[CacheManager] = None):
        self.bearer_token = bearer_token
        self.client = None
        self.cache = cache_manager or CacheManager()
        
        if TWITTER_AVAILABLE and bearer_token:
            try:
                self.client = tweepy.Client(
                    bearer_token=bearer_token,
                    wait_on_rate_limit=False  # 快速失败，不等待速率限制
                )
                print("✅ Twitter API initialized (fast-fail mode)")
            except Exception as e:
                print(f"⚠️ Twitter API initialization failed: {e}")
    
    @RateLimiter(max_calls=15, time_window=900)  # 15 calls per 15 minutes
    async def get_trending_topics(self, keywords: List[str], limit: int = 100) -> List[Dict]:
        """
        收集 Twitter 趋势数据（带缓存和速率限制）
        """
        trending_topics = []
        
        for keyword in keywords[:5]:  # Limit keywords to avoid overload
            # 检查缓存
            cache_key = self.cache._generate_key('twitter', {'keyword': keyword, 'limit': limit})
            cached_data = await self.cache.get(cache_key)
            
            if cached_data:
                print(f"📦 Using cached Twitter data for '{keyword}'")
                trending_topics.append(cached_data)
                continue
            
            # 如果没有客户端，跳过（不使用模拟数据）
            if not self.client:
                print(f"⚠️ Twitter API not available for '{keyword}'")
                continue
            
            try:
                # 搜索推文
                tweets = self.client.search_recent_tweets(
                    query=f"{keyword} -is:retweet -is:reply lang:en",
                    max_results=min(limit, 100),
                    tweet_fields=['public_metrics', 'created_at', 'entities'],
                    expansions=['author_id']
                )
                
                if not tweets.data:
                    print(f"ℹ️ No Twitter data found for '{keyword}'")
                    continue
                
                # 深度分析
                analysis = self._deep_analyze_tweets(tweets.data, keyword)
                
                trend_data = {
                    'keyword': keyword,
                    'source': 'twitter',
                    'engagement_score': analysis['engagement_score'],
                    'tweet_count': len(tweets.data),
                    'related_hashtags': analysis['top_hashtags'],
                    'sentiment': analysis['sentiment'],
                    'velocity': analysis['velocity'],  # 新增：趋势速度
                    'influencer_ratio': analysis['influencer_ratio'],  # 新增：影响力比例
                    'trend_score': self._calculate_twitter_trend_score(analysis),
                    'timestamp': datetime.utcnow().isoformat()
                }
                
                # 缓存结果（1小时）
                await self.cache.set(cache_key, trend_data)
                trending_topics.append(trend_data)
                
                # 避免速率限制
                await asyncio.sleep(1)
                
            except tweepy.errors.TooManyRequests as e:
                print(f"⚠️ Twitter rate limit hit for '{keyword}', skipping (fast-fail)")
                # 返回空数据，不等待
                continue
            except tweepy.errors.TweepyException as e:
                # 检查是否是速率限制相关的错误
                error_str = str(e).lower()
                if "429" in str(e) or "rate limit" in error_str or "too many requests" in error_str:
                    print(f"⚠️ Twitter rate limit detected for '{keyword}', skipping (fast-fail)")
                    continue
                print(f"❌ Twitter error for '{keyword}': {type(e).__name__} - {e}")
                continue
            except Exception as e:
                print(f"❌ Twitter error for '{keyword}': {type(e).__name__} - {e}")
                continue
        
        return trending_topics
    
    def _deep_analyze_tweets(self, tweets: List, keyword: str) -> Dict:
        """
        深度分析推文数据
        """
        if not tweets:
            return self._empty_analysis()
        
        # 1. 计算参与度
        total_engagement = 0
        high_engagement_count = 0
        
        for tweet in tweets:
            metrics = tweet.public_metrics
            engagement = (
                metrics['like_count'] + 
                metrics['retweet_count'] * 2 + 
                metrics['reply_count'] * 1.5
            )
            total_engagement += engagement
            
            # 高参与度推文（超过100互动）
            if engagement > 100:
                high_engagement_count += 1
        
        avg_engagement = total_engagement / len(tweets)
        
        # 2. 提取标签
        hashtags = []
        for tweet in tweets:
            if hasattr(tweet, 'entities') and tweet.entities:
                if 'hashtags' in tweet.entities:
                    hashtags.extend([h['tag'].lower() for h in tweet.entities['hashtags']])
        
        top_hashtags = [tag for tag, count in Counter(hashtags).most_common(10)]
        
        # 3. 情感分析（简化版）
        sentiment = self._analyze_sentiment(tweets)
        
        # 4. 趋势速度（最近推文的时间分布）
        velocity = self._calculate_velocity(tweets)
        
        # 5. 影响力比例（高参与度推文占比）
        influencer_ratio = (high_engagement_count / len(tweets)) * 100
        
        return {
            'engagement_score': avg_engagement,
            'top_hashtags': top_hashtags,
            'sentiment': sentiment,
            'velocity': velocity,
            'influencer_ratio': influencer_ratio
        }
    
    def _analyze_sentiment(self, tweets: List) -> str:
        """简化的情感分析"""
        positive_words = {'great', 'amazing', 'awesome', 'excellent', 'best', 'love', 'perfect', 'excited'}
        negative_words = {'bad', 'worst', 'terrible', 'awful', 'hate', 'horrible', 'disappointing', 'issue'}
        
        pos_count = 0
        neg_count = 0
        
        for tweet in tweets:
            text = tweet.text.lower()
            pos_count += sum(1 for word in positive_words if word in text)
            neg_count += sum(1 for word in negative_words if word in text)
        
        if pos_count > neg_count * 1.5:
            return 'positive'
        elif neg_count > pos_count * 1.5:
            return 'negative'
        else:
            return 'neutral'
    
    def _calculate_velocity(self, tweets: List) -> float:
        """
        计算趋势速度（推文时间分布）
        返回：每小时平均推文数
        """
        if not tweets:
            return 0.0
        
        try:
            timestamps = [tweet.created_at for tweet in tweets if hasattr(tweet, 'created_at')]
            if not timestamps:
                return 0.0
            
            oldest = min(timestamps)
            newest = max(timestamps)
            time_span = (newest - oldest).total_seconds() / 3600  # hours
            
            if time_span < 0.1:  # 避免除以0
                time_span = 0.1
            
            velocity = len(tweets) / time_span
            return round(velocity, 2)
        except:
            return 0.0
    
    def _calculate_twitter_trend_score(self, analysis: Dict) -> float:
        """
        综合计算趋势分数
        """
        # 参与度分数（0-40分）
        engagement_score = min(40, (analysis['engagement_score'] / 200) * 40)
        
        # 速度分数（0-30分）
        velocity_score = min(30, (analysis['velocity'] / 10) * 30)
        
        # 影响力分数（0-20分）
        influencer_score = min(20, (analysis['influencer_ratio'] / 20) * 20)
        
        # 情感加成（0-10分）
        sentiment_bonus = 10 if analysis['sentiment'] == 'positive' else 0
        
        total_score = engagement_score + velocity_score + influencer_score + sentiment_bonus
        return round(total_score, 2)
    
    def _empty_analysis(self) -> Dict:
        return {
            'engagement_score': 0,
            'top_hashtags': [],
            'sentiment': 'neutral',
            'velocity': 0,
            'influencer_ratio': 0
        }


class EnhancedRedditCollector:
    """
    增强版 Reddit 收集器
    """
    def __init__(self, client_id: Optional[str] = None, 
                 client_secret: Optional[str] = None,
                 user_agent: str = "TrendForge/3.0",
                 cache_manager: Optional[CacheManager] = None):
        self.reddit = None
        self.cache = cache_manager or CacheManager()
        
        if REDDIT_AVAILABLE and client_id and client_secret:
            try:
                self.reddit = praw.Reddit(
                    client_id=client_id,
                    client_secret=client_secret,
                    user_agent=user_agent
                )
                print("✅ Reddit API initialized")
            except Exception as e:
                print(f"⚠️ Reddit API initialization failed: {e}")
    
    @RateLimiter(max_calls=60, time_window=60)  # 60 calls per minute
    async def get_trending_topics(self, keywords: List[str]) -> List[Dict]:
        """
        收集 Reddit 趋势数据（增强版）
        """
        trending_topics = []
        
        for keyword in keywords[:5]:
            # 检查缓存
            cache_key = self.cache._generate_key('reddit', {'keyword': keyword})
            cached_data = await self.cache.get(cache_key)
            
            if cached_data:
                print(f"📦 Using cached Reddit data for '{keyword}'")
                trending_topics.append(cached_data)
                continue
            
            if not self.reddit:
                print(f"⚠️ Reddit API not available for '{keyword}'")
                continue
            
            try:
                # 搜索帖子
                search_results = self.reddit.subreddit('all').search(
                    keyword,
                    limit=100,
                    time_filter='week',
                    sort='hot'
                )
                
                posts = list(search_results)
                
                if not posts:
                    print(f"ℹ️ No Reddit data found for '{keyword}'")
                    continue
                
                # 深度分析
                analysis = self._deep_analyze_posts(posts, keyword)
                
                trend_data = {
                    'keyword': keyword,
                    'source': 'reddit',
                    'upvote_score': analysis['avg_upvotes'],
                    'comment_count': analysis['total_comments'],
                    'post_count': len(posts),
                    'top_subreddits': analysis['top_subreddits'],
                    'discussion_depth': analysis['discussion_depth'],  # 新增
                    'award_count': analysis['total_awards'],  # 新增
                    'trend_score': self._calculate_reddit_trend_score(analysis),
                    'timestamp': datetime.utcnow().isoformat()
                }
                
                # 缓存结果
                await self.cache.set(cache_key, trend_data)
                trending_topics.append(trend_data)
                
                await asyncio.sleep(1)
                
            except Exception as e:
                print(f"❌ Reddit error for '{keyword}': {e}")
                continue
        
        return trending_topics
    
    def _deep_analyze_posts(self, posts: List, keyword: str) -> Dict:
        """深度分析 Reddit 帖子"""
        if not posts:
            return self._empty_analysis()
        
        total_upvotes = sum(post.score for post in posts)
        total_comments = sum(post.num_comments for post in posts)
        total_awards = sum(
            post.total_awards_received if hasattr(post, 'total_awards_received') else 0
            for post in posts
        )
        
        # Subreddit 分布
        subreddit_counts = Counter([post.subreddit.display_name for post in posts])
        top_subreddits = [s[0] for s in subreddit_counts.most_common(5)]
        
        # 讨论深度（平均评论数）
        discussion_depth = total_comments / len(posts) if posts else 0
        
        return {
            'avg_upvotes': total_upvotes / len(posts),
            'total_comments': total_comments,
            'total_awards': total_awards,
            'top_subreddits': top_subreddits,
            'discussion_depth': discussion_depth
        }
    
    def _calculate_reddit_trend_score(self, analysis: Dict) -> float:
        """计算 Reddit 趋势分数"""
        upvote_score = min(40, (analysis['avg_upvotes'] / 1000) * 40)
        comment_score = min(30, (analysis['discussion_depth'] / 50) * 30)
        award_score = min(30, (analysis['total_awards'] / 10) * 30)
        
        return round(upvote_score + comment_score + award_score, 2)
    
    def _empty_analysis(self) -> Dict:
        return {
            'avg_upvotes': 0,
            'total_comments': 0,
            'total_awards': 0,
            'top_subreddits': [],
            'discussion_depth': 0
        }


class EnhancedSerpAPICollector:
    """
    SerpAPI 收集器 - 从 Google、Twitter 和 Reddit 获取趋势数据
    作为其他 API 的替代方案
    """
    def __init__(self, api_key: Optional[str] = None, cache_manager: Optional[CacheManager] = None):
        self.api_key = api_key
        self.cache = cache_manager or CacheManager()
        self.available = SERPAPI_AVAILABLE and api_key is not None
        
        if not SERPAPI_AVAILABLE:
            print("⚠️ SerpAPI library not installed")
        elif not api_key:
            print("⚠️ SerpAPI key not provided")
        else:
            print("✅ SerpAPI collector initialized")
    
    async def get_trending_topics(self, keywords: List[str], geo: str = 'US') -> List[Dict]:
        """
        从 SerpAPI 获取趋势数据（Google、Twitter、Reddit）
        """
        if not self.available:
            return []
        
        trending_topics = []
        
        for keyword in keywords[:5]:  # 限制关键词数量
            # 检查缓存
            cache_key = self.cache._generate_key('serpapi', {'keyword': keyword, 'geo': geo})
            cached_data = await self.cache.get(cache_key)
            
            if cached_data:
                print(f"📦 Using cached SerpAPI data for '{keyword}'")
                trending_topics.append(cached_data)
                continue
            
            try:
                # 搜索 Google（包含 Twitter 和 Reddit 结果）
                results = await asyncio.to_thread(
                    self._search_google, keyword, geo
                )
                
                if not results:
                    print(f"ℹ️ No SerpAPI data found for '{keyword}'")
                    continue
                
                # 分析结果
                trend_data = self._analyze_serpapi_results(results, keyword)
                
                # 缓存结果
                await self.cache.set(cache_key, trend_data)
                trending_topics.append(trend_data)
                
                await asyncio.sleep(1)  # 避免速率限制
                
            except Exception as e:
                print(f"❌ SerpAPI error for '{keyword}': {e}")
                continue
        
        return trending_topics
    
    def _search_google(self, keyword: str, geo: str = 'US') -> Dict:
        """
        使用 SerpAPI 搜索 Google（包含 Twitter 和 Reddit 结果）
        """
        try:
            params = {
                "q": keyword,
                "api_key": self.api_key,
                "engine": "google",
                "location": geo,
                "num": 50,  # 获取更多结果
                "tbm": "nws"  # 新闻搜索，包含社交媒体结果
            }
            
            search = GoogleSearch(params)
            results = search.get_dict()
            
            return results
        except Exception as e:
            print(f"❌ SerpAPI Google search error: {e}")
            return {}
    
    def _analyze_serpapi_results(self, results: Dict, keyword: str) -> Dict:
        """
        分析 SerpAPI 结果，提取 Google、Twitter 和 Reddit 信号
        """
        # 提取 Google 搜索结果
        organic_results = results.get('organic_results', [])
        news_results = results.get('news_results', [])
        
        # 提取 Twitter 结果（从搜索结果中查找）
        twitter_mentions = 0
        twitter_engagement = 0
        twitter_hashtags = []
        
        # 提取 Reddit 结果
        reddit_mentions = 0
        reddit_score = 0
        reddit_subreddits = []
        
        # 分析所有结果
        all_text = ""
        for result in organic_results + news_results:
            title = result.get('title', '')
            snippet = result.get('snippet', '')
            link = result.get('link', '')
            all_text += f"{title} {snippet} "
            
            # 检测 Twitter 链接
            if 'twitter.com' in link or 'x.com' in link:
                twitter_mentions += 1
                # 尝试提取点赞数等信息（如果可用）
                if 'position' in result:
                    twitter_engagement += (51 - result.get('position', 50)) * 10
            
            # 检测 Reddit 链接
            if 'reddit.com' in link:
                reddit_mentions += 1
                # 提取 subreddit
                if '/r/' in link:
                    subreddit = link.split('/r/')[1].split('/')[0]
                    if subreddit not in reddit_subreddits:
                        reddit_subreddits.append(subreddit)
                # 位置分数
                if 'position' in result:
                    reddit_score += (51 - result.get('position', 50)) * 10
        
        # 提取 hashtags
        hashtags = re.findall(r'#\w+', all_text)
        twitter_hashtags = list(set(hashtags[:10]))
        
        # 计算趋势分数
        google_score = min(100, len(organic_results) * 5 + len(news_results) * 3)
        twitter_score = min(100, twitter_mentions * 15 + twitter_engagement * 0.1)
        reddit_score = min(100, reddit_mentions * 20 + reddit_score * 0.1)
        
        # 综合分数（SerpAPI 作为替代方案，权重较高）
        composite_score = (
            google_score * 0.5 +  # Google 50%
            twitter_score * 0.25 +  # Twitter 25%
            reddit_score * 0.25  # Reddit 25%
        )
        
        return {
            'keyword': keyword,
            'source': 'serpapi',
            'google_score': round(google_score, 2),
            'twitter_score': round(twitter_score, 2),
            'reddit_score': round(reddit_score, 2),
            'composite_score': round(composite_score, 2),
            'google_results_count': len(organic_results) + len(news_results),
            'twitter_mentions': twitter_mentions,
            'reddit_mentions': reddit_mentions,
            'twitter_hashtags': twitter_hashtags,
            'reddit_subreddits': reddit_subreddits[:5],
            'trend_score': round(composite_score, 2),
            'timestamp': datetime.utcnow().isoformat()
        }


class EnhancedGoogleTrendsCollector:
    """
    增强版 Google Trends 收集器 - 支持历史数据
    """
    def __init__(self, cache_manager: Optional[CacheManager] = None):
        self.pytrends = None
        self.cache = cache_manager or CacheManager()
        
        if GOOGLE_TRENDS_AVAILABLE:
            try:
                self.pytrends = TrendReq(hl='en-US', tz=360, timeout=(10, 25), retries=3)
                print("✅ Google Trends initialized")
            except Exception as e:
                print(f"⚠️ Google Trends initialization failed: {e}")
    
    async def get_trending_topics(self, keywords: List[str], geo: str = 'US', 
                                   timeframe: str = 'now 7-d') -> List[Dict]:
        """
        收集 Google Trends 数据（支持自定义时间范围）
        """
        trending_topics = []
        
        if not self.pytrends:
            print("⚠️ Google Trends not available")
            return trending_topics
        
        for keyword in keywords[:5]:
            cache_key = self.cache._generate_key('google_trends', {
                'keyword': keyword, 
                'geo': geo, 
                'timeframe': timeframe
            })
            cached_data = await self.cache.get(cache_key)
            
            if cached_data:
                print(f"📦 Using cached Google Trends data for '{keyword}'")
                trending_topics.append(cached_data)
                continue
            
            try:
                # Build payload
                self.pytrends.build_payload([keyword], timeframe=timeframe, geo=geo)
                
                # Interest over time
                interest_df = self.pytrends.interest_over_time()
                
                if interest_df.empty or keyword not in interest_df.columns:
                    continue
                
                values = interest_df[keyword].values
                
                # 计算增长率
                growth_rate = self._calculate_growth_rate(values)
                
                # 获取相关查询
                related_queries = self.pytrends.related_queries()
                rising_queries = []
                top_queries = []
                
                if keyword in related_queries:
                    if related_queries[keyword]['rising'] is not None:
                        rising_queries = related_queries[keyword]['rising']['query'].head(10).tolist()
                    if related_queries[keyword]['top'] is not None:
                        top_queries = related_queries[keyword]['top']['query'].head(10).tolist()
                
                # 当前兴趣度
                current_interest = int(values[-1])
                
                # 趋势方向
                trend_direction = self._determine_trend_direction(values)
                
                trend_data = {
                    'keyword': keyword,
                    'source': 'google_trends',
                    'current_interest': current_interest,
                    'growth_rate': round(growth_rate, 2),
                    'trend_direction': trend_direction,  # 新增：上升/下降/稳定
                    'volatility': self._calculate_volatility(values),  # 新增：波动性
                    'rising_queries': rising_queries,
                    'top_queries': top_queries,
                    'trend_score': self._calculate_trends_score(current_interest, growth_rate, values),
                    'historical_data': values.tolist()[-30:] if len(values) > 30 else values.tolist(),  # 保存最近30天数据
                    'timestamp': datetime.utcnow().isoformat()
                }
                
                await self.cache.set(cache_key, trend_data)
                trending_topics.append(trend_data)
                
                await asyncio.sleep(2)
                
            except Exception as e:
                print(f"❌ Google Trends error for '{keyword}': {e}")
                continue
        
        return trending_topics
    
    def _calculate_growth_rate(self, values) -> float:
        """计算增长率"""
        if len(values) < 7:
            return 0.0
        
        recent_avg = values[-3:].mean()
        past_avg = values[:3].mean()
        
        if past_avg == 0:
            return 0.0
        
        growth_rate = ((recent_avg - past_avg) / past_avg) * 100
        return growth_rate
    
    def _determine_trend_direction(self, values) -> str:
        """判断趋势方向"""
        if len(values) < 3:
            return 'stable'
        
        recent_trend = values[-3:].mean()
        past_trend = values[-7:-3].mean() if len(values) >= 7 else values[:-3].mean()
        
        diff_ratio = (recent_trend - past_trend) / max(past_trend, 1)
        
        if diff_ratio > 0.2:
            return 'rising'
        elif diff_ratio < -0.2:
            return 'falling'
        else:
            return 'stable'
    
    def _calculate_volatility(self, values) -> float:
        """计算波动性（标准差）"""
        if len(values) < 2:
            return 0.0
        return round(float(np.std(values)), 2)
    
    def _calculate_trends_score(self, interest: int, growth_rate: float, values) -> float:
        """计算综合趋势分数"""
        # 兴趣度分数（0-40分）
        interest_score = interest * 0.4
        
        # 增长率分数（0-40分）
        growth_score = min(40, max(0, growth_rate) * 0.4)
        
        # 稳定性分数（0-20分）
        volatility = self._calculate_volatility(values)
        stability_score = max(0, 20 - volatility * 0.5)
        
        return round(interest_score + growth_score + stability_score, 2)


class CrossPlatformSignalAggregator:
    """
    跨平台信号聚合器 - 深度关联分析
    """
    def __init__(self, cache_manager: Optional[CacheManager] = None):
        self.cache = cache_manager or CacheManager()
    
    def aggregate_signals(self, twitter: List[Dict], reddit: List[Dict], 
                         google: List[Dict], serpapi: List[Dict] = None) -> List[Dict]:
        """
        深度聚合和关联分析（包含 SerpAPI 作为替代方案）
        """
        signal_map = {}
        
        # 处理 Twitter 信号
        for trend in twitter:
            keyword = trend['keyword']
            signal_map[keyword] = {
                'keyword': keyword,
                'twitter': self._extract_twitter_signals(trend),
                'reddit': {},
                'google': {},
                'serpapi': {},
                'sources': ['twitter']
            }
        
        # 处理 Reddit 信号
        for trend in reddit:
            keyword = trend['keyword']
            if keyword in signal_map:
                signal_map[keyword]['reddit'] = self._extract_reddit_signals(trend)
                signal_map[keyword]['sources'].append('reddit')
            else:
                signal_map[keyword] = {
                    'keyword': keyword,
                    'twitter': {},
                    'reddit': self._extract_reddit_signals(trend),
                    'google': {},
                    'serpapi': {},
                    'sources': ['reddit']
                }
        
        # 处理 Google Trends 信号
        for trend in google:
            keyword = trend['keyword']
            if keyword in signal_map:
                signal_map[keyword]['google'] = self._extract_google_signals(trend)
                signal_map[keyword]['sources'].append('google_trends')
            else:
                signal_map[keyword] = {
                    'keyword': keyword,
                    'twitter': {},
                    'reddit': {},
                    'google': self._extract_google_signals(trend),
                    'serpapi': {},
                    'sources': ['google_trends']
                }
        
        # 处理 SerpAPI 信号（作为替代方案）
        if serpapi:
            for trend in serpapi:
                keyword = trend['keyword']
                serpapi_signals = {
                    'score': trend.get('composite_score', 0),
                    'google_score': trend.get('google_score', 0),
                    'twitter_score': trend.get('twitter_score', 0),
                    'reddit_score': trend.get('reddit_score', 0),
                    'google_results': trend.get('google_results_count', 0),
                    'twitter_mentions': trend.get('twitter_mentions', 0),
                    'reddit_mentions': trend.get('reddit_mentions', 0),
                    'hashtags': trend.get('twitter_hashtags', []),
                    'subreddits': trend.get('reddit_subreddits', [])
                }
                
                if keyword in signal_map:
                    # 如果已有信号，使用 SerpAPI 补充或替代
                    signal_map[keyword]['serpapi'] = serpapi_signals
                    # 如果其他源失败，使用 SerpAPI 数据
                    if not signal_map[keyword]['twitter'] and trend.get('twitter_score', 0) > 0:
                        signal_map[keyword]['twitter'] = {
                            'score': trend.get('twitter_score', 0),
                            'hashtags': trend.get('twitter_hashtags', [])
                        }
                    if not signal_map[keyword]['reddit'] and trend.get('reddit_score', 0) > 0:
                        signal_map[keyword]['reddit'] = {
                            'score': trend.get('reddit_score', 0),
                            'subreddits': trend.get('reddit_subreddits', [])
                        }
                    if not signal_map[keyword]['google'] and trend.get('google_score', 0) > 0:
                        signal_map[keyword]['google'] = {
                            'score': trend.get('google_score', 0)
                        }
                    if 'serpapi' not in signal_map[keyword]['sources']:
                        signal_map[keyword]['sources'].append('serpapi')
                else:
                    # 如果完全没有信号，使用 SerpAPI 作为主要源
                    signal_map[keyword] = {
                        'keyword': keyword,
                        'twitter': {
                            'score': trend.get('twitter_score', 0),
                            'hashtags': trend.get('twitter_hashtags', [])
                        } if trend.get('twitter_score', 0) > 0 else {},
                        'reddit': {
                            'score': trend.get('reddit_score', 0),
                            'subreddits': trend.get('reddit_subreddits', [])
                        } if trend.get('reddit_score', 0) > 0 else {},
                        'google': {
                            'score': trend.get('google_score', 0)
                        } if trend.get('google_score', 0) > 0 else {},
                        'serpapi': serpapi_signals,
                        'sources': ['serpapi']
                    }
        
        # 计算综合信号
        merged_signals = []
        for keyword, signals in signal_map.items():
            composite = self._calculate_composite_signal(signals)
            composite['keyword'] = keyword
            composite['sources'] = signals['sources']
            composite['source_count'] = len(signals['sources'])
            merged_signals.append(composite)
        
        # 按综合分数排序
        merged_signals.sort(key=lambda x: x['composite_score'], reverse=True)
        
        return merged_signals
    
    def _extract_twitter_signals(self, trend: Dict) -> Dict:
        """提取 Twitter 关键信号"""
        return {
            'score': trend.get('trend_score', 0),
            'engagement': trend.get('engagement_score', 0),
            'velocity': trend.get('velocity', 0),
            'sentiment': trend.get('sentiment', 'neutral'),
            'hashtags': trend.get('related_hashtags', [])
        }
    
    def _extract_reddit_signals(self, trend: Dict) -> Dict:
        """提取 Reddit 关键信号"""
        return {
            'score': trend.get('trend_score', 0),
            'discussion_depth': trend.get('discussion_depth', 0),
            'subreddits': trend.get('top_subreddits', [])
        }
    
    def _extract_google_signals(self, trend: Dict) -> Dict:
        """提取 Google Trends 关键信号"""
        return {
            'score': trend.get('trend_score', 0),
            'interest': trend.get('current_interest', 0),
            'growth_rate': trend.get('growth_rate', 0),
            'direction': trend.get('trend_direction', 'stable'),
            'rising_queries': trend.get('rising_queries', [])
        }
    
    def _calculate_composite_signal(self, signals: Dict) -> Dict:
        """
        计算综合信号分数（包含 SerpAPI 作为替代方案）
        
        新算法（使用 SerpAPI 时）：
        - Twitter: 25% (社交讨论热度)
        - Reddit: 25% (社区深度讨论)
        - Google: 30% (搜索需求)
        - SerpAPI: 20% (综合替代方案，当其他源失败时权重更高)
        - 跨平台加成: +15分 (4个平台都有) 或 +10分 (3个平台)
        """
        # 检查是否有 SerpAPI 数据
        has_serpapi = signals.get('serpapi', {}).get('score', 0) > 0
        use_serpapi_as_primary = (
            has_serpapi and 
            (signals['twitter'].get('score', 0) == 0 or 
             signals['reddit'].get('score', 0) == 0 or 
             signals['google'].get('score', 0) == 0)
        )
        
        if use_serpapi_as_primary:
            # 使用 SerpAPI 作为主要数据源（替代方案）
            serpapi_data = signals['serpapi']
            twitter_score = max(
                signals['twitter'].get('score', 0),
                serpapi_data.get('twitter_score', 0)
            ) * 0.25
            reddit_score = max(
                signals['reddit'].get('score', 0),
                serpapi_data.get('reddit_score', 0)
            ) * 0.25
            google_score = max(
                signals['google'].get('score', 0),
                serpapi_data.get('google_score', 0)
            ) * 0.30
            serpapi_score = serpapi_data.get('score', 0) * 0.20
            
            base_score = twitter_score + reddit_score + google_score + serpapi_score
        else:
            # 标准算法（SerpAPI 作为补充）
            twitter_score = signals['twitter'].get('score', 0) * 0.25
            reddit_score = signals['reddit'].get('score', 0) * 0.25
            google_score = signals['google'].get('score', 0) * 0.30
            serpapi_score = signals.get('serpapi', {}).get('score', 0) * 0.20
            
            base_score = twitter_score + reddit_score + google_score + serpapi_score
        
        # 跨平台加成
        source_bonus = 0
        source_count = len(signals['sources'])
        if source_count >= 4:
            source_bonus = 15  # 4个平台都有，强烈信号
        elif source_count == 3:
            source_bonus = 10  # 3个平台，中等信号
        elif source_count == 2:
            source_bonus = 5   # 2个平台，基础信号
        
        # 趋势方向加成
        direction_bonus = 0
        if signals['google'].get('direction') == 'rising':
            direction_bonus = 5
        
        # 情感加成
        sentiment_bonus = 0
        if signals['twitter'].get('sentiment') == 'positive':
            sentiment_bonus = 3
        
        # SerpAPI 替代加成（当其他源失败时）
        serpapi_bonus = 0
        if use_serpapi_as_primary:
            serpapi_bonus = 8  # 使用 SerpAPI 作为替代方案时的额外加成
        
        composite_score = min(100, base_score + source_bonus + direction_bonus + sentiment_bonus + serpapi_bonus)
        
        return {
            'composite_score': round(composite_score, 2),
            'twitter_score': round(twitter_score / 0.25, 2) if twitter_score > 0 else 0,
            'reddit_score': round(reddit_score / 0.25, 2) if reddit_score > 0 else 0,
            'google_score': round(google_score / 0.30, 2) if google_score > 0 else 0,
            'serpapi_score': round(serpapi_score / 0.20, 2) if serpapi_score > 0 else 0,
            'growth_rate': signals['google'].get('growth_rate', 0),
            'viral_potential': self._calculate_viral_potential(signals),
            'related_info': {
                'twitter_hashtags': signals['twitter'].get('hashtags', []) or signals.get('serpapi', {}).get('hashtags', []),
                'reddit_subreddits': signals['reddit'].get('subreddits', []) or signals.get('serpapi', {}).get('subreddits', []),
                'rising_queries': signals['google'].get('rising_queries', []),
                'serpapi_used': use_serpapi_as_primary
            }
        }
    
    def _calculate_viral_potential(self, signals: Dict) -> float:
        """
        计算病毒式传播潜力
        基于跨平台信号强度
        """
        # Twitter 速度
        twitter_velocity = signals['twitter'].get('velocity', 0)
        
        # Google 增长率
        google_growth = signals['google'].get('growth_rate', 0)
        
        # Reddit 讨论深度
        reddit_depth = signals['reddit'].get('discussion_depth', 0)
        
        # 综合计算
        viral_score = (
            min(40, twitter_velocity / 10 * 40) +
            min(40, max(0, google_growth) * 0.4) +
            min(20, reddit_depth / 50 * 20)
        )
        
        return round(min(100, viral_score), 2)


# 兼容性包装器 - 保持与现有代码的兼容性
class EnhancedSocialMediaAggregator:
    """
    增强版社交媒体聚合器 - 兼容现有接口
    """
    def __init__(self, twitter_token: Optional[str] = None,
                 reddit_id: Optional[str] = None,
                 reddit_secret: Optional[str] = None,
                 serpapi_key: Optional[str] = None,
                 redis_url: Optional[str] = None):
        # 初始化缓存管理器
        cache_manager = CacheManager(redis_url=redis_url, ttl=3600)
        
        # 初始化收集器
        self.twitter = EnhancedTwitterCollector(twitter_token, cache_manager)
        self.reddit = EnhancedRedditCollector(reddit_id, reddit_secret, cache_manager=cache_manager)
        self.google_trends = EnhancedGoogleTrendsCollector(cache_manager)
        self.serpapi = EnhancedSerpAPICollector(serpapi_key, cache_manager)
        
        # 初始化聚合器
        self.signal_aggregator = CrossPlatformSignalAggregator(cache_manager)
    
    async def collect_all_trends(self, keywords: List[str], geo: str = 'US') -> Dict:
        """
        收集所有平台的趋势数据（兼容现有接口）
        每个平台单独设置超时，避免一个平台慢影响整体
        """
        # 为每个平台设置独立超时（15秒，减少等待时间）
        async def collect_with_timeout(task, platform_name, timeout=15.0):
            try:
                return await asyncio.wait_for(task, timeout=timeout)
            except asyncio.TimeoutError:
                print(f"⚠️ {platform_name} collection timeout ({timeout}s), skipping")
                return []
            except Exception as e:
                print(f"⚠️ {platform_name} collection failed: {e}")
                return []
        
        # 并行收集，每个都有独立超时
        twitter_task = collect_with_timeout(
            self.twitter.get_trending_topics(keywords),
            "Twitter",
            timeout=15.0  # 减少到15秒
        )
        reddit_task = collect_with_timeout(
            self.reddit.get_trending_topics(keywords),
            "Reddit",
            timeout=15.0  # 减少到15秒
        )
        google_task = collect_with_timeout(
            self.google_trends.get_trending_topics(keywords, geo),
            "Google Trends",
            timeout=15.0  # 减少到15秒
        )
        serpapi_task = collect_with_timeout(
            self.serpapi.get_trending_topics(keywords, geo),
            "SerpAPI",
            timeout=15.0  # 15秒超时
        )
        
        twitter_trends, reddit_trends, google_trends, serpapi_trends = await asyncio.gather(
            twitter_task, reddit_task, google_task, serpapi_task,
            return_exceptions=True
        )
        
        # 处理异常
        if isinstance(twitter_trends, Exception):
            print(f"Twitter collection failed: {twitter_trends}")
            twitter_trends = []
        if isinstance(reddit_trends, Exception):
            print(f"Reddit collection failed: {reddit_trends}")
            reddit_trends = []
        if isinstance(google_trends, Exception):
            print(f"Google Trends collection failed: {google_trends}")
            google_trends = []
        if isinstance(serpapi_trends, Exception):
            print(f"SerpAPI collection failed: {serpapi_trends}")
            serpapi_trends = []
        
        # 使用新的聚合器（包含 SerpAPI）
        merged_trends = self.signal_aggregator.aggregate_signals(
            twitter_trends, reddit_trends, google_trends, serpapi_trends
        )
        
        # 转换为兼容格式
        compatible_trends = []
        for trend in merged_trends:
            compatible_trend = {
                'keyword': trend['keyword'],
                'composite_score': trend['composite_score'],
                'growth_rate': trend.get('growth_rate', 0),
                'viral_potential': trend.get('viral_potential', 0),
                'sources': trend['sources'],
                'related_info': trend.get('related_info', {}),
                # 保持向后兼容
                'twitter_hashtags': trend.get('related_info', {}).get('twitter_hashtags', []),
                'reddit_subreddits': trend.get('related_info', {}).get('reddit_subreddits', []),
                'rising_queries': trend.get('related_info', {}).get('rising_queries', [])
            }
            compatible_trends.append(compatible_trend)
        
        return {
            'merged_trends': compatible_trends,
            'by_source': {
                'twitter': twitter_trends,
                'reddit': reddit_trends,
                'google_trends': google_trends,
                'serpapi': serpapi_trends if not isinstance(serpapi_trends, Exception) else []
            },
            'collected_at': datetime.utcnow().isoformat()
        }


# 全局实例（兼容现有代码）
enhanced_social_aggregator = EnhancedSocialMediaAggregator()
