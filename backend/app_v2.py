"""
TrendForge AI Backend - MVP 3.0
Deep content analysis with social media trends + Prophet time series prediction
"""

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List, Optional, Dict
import asyncio
from datetime import datetime
import os
import urllib.parse
from dotenv import load_dotenv

# Import our enhanced services
# Force reload to avoid cache issues
import importlib
import sys

# Clear any cached modules
modules_to_clear = [k for k in sys.modules.keys() if 'enhanced_youtube_analyzer' in k or 'analyzer' in k]
for mod in modules_to_clear:
    if mod in sys.modules:
        del sys.modules[mod]

# Ensure NLTK data is downloaded before importing analyzers
# Import and run NLTK setup module
try:
    from services.nltk_setup import download_nltk_data
    download_nltk_data()
except Exception as e:
    print(f"⚠️  NLTK setup failed: {e}")
    print("   Continuing anyway, will try to download on-demand...")

from services.enhanced_youtube_analyzer import (
    analyze_channel_deeply,
    content_analyzer,
    audience_analyzer
)

# Verify we're using the correct analyzer
print(f"✅ Using content_analyzer: {type(content_analyzer).__name__}")
print(f"✅ Using audience_analyzer: {type(audience_analyzer).__name__}")
print(f"✅ Analyzer has extract_topics_from_titles: {hasattr(content_analyzer, 'extract_topics_from_titles')}")
print(f"✅ Analyzer has _extract_proper_nouns: {hasattr(content_analyzer, '_extract_proper_nouns')}")
print(f"✅ Analyzer has _extract_proper_nouns_nltk: {hasattr(content_analyzer, '_extract_proper_nouns_nltk')} (should be False)")
# Try to use enhanced social collector (MVP 3.0), fallback to original
try:
    from services.enhanced_social_collector import EnhancedSocialMediaAggregator
    USE_ENHANCED_COLLECTOR = True
    print("✅ Using Enhanced Social Media Collector (MVP 3.0)")
except ImportError:
    from services.social_media_collector import SocialMediaAggregator
    USE_ENHANCED_COLLECTOR = False
    print("⚠️ Using original Social Media Collector")

# Try to use predictive recommendation engine (MVP 3.0), fallback to original
try:
    from services.predictive_recommender import PredictiveRecommendationEngine
    predictive_recommender = PredictiveRecommendationEngine()
    USE_PREDICTIVE_ENGINE = True
    print("✅ Using Predictive Recommendation Engine (MVP 3.0 with Prophet)")
    # Also import original engine for backtest analyzer compatibility
    from services.intelligent_recommender import (
        recommendation_engine,
        title_engine
    )
except ImportError:
    from services.intelligent_recommender import (
        recommendation_engine,
        title_engine
    )
    USE_PREDICTIVE_ENGINE = False
    predictive_recommender = None
    print("✅ Using Recommendation Engine (MVP 2.0)")

# Import Prophet predictor for MVP 3.0
try:
    from services.trend_predictor import trend_predictor, PROPHET_AVAILABLE
    if PROPHET_AVAILABLE:
        print("✅ Prophet Prediction Engine loaded (MVP 3.0)")
    else:
        print("⚠️ Prophet not installed, predictions will be disabled")
except ImportError:
    trend_predictor = None
    PROPHET_AVAILABLE = False
    print("⚠️ Prophet predictor not available")

# Load environment variables
load_dotenv()

# Decode URL-encoded Twitter Bearer Token if needed
twitter_token = os.getenv('TWITTER_BEARER_TOKEN')
if twitter_token:
    twitter_token = urllib.parse.unquote(twitter_token)

# Initialize social aggregator (enhanced or original)
if USE_ENHANCED_COLLECTOR:
    redis_url = os.getenv('REDIS_URL')  # Optional Redis cache
    serpapi_key = os.getenv('SERPAPI_KEY')  # SerpAPI key for alternative data source
    social_aggregator = EnhancedSocialMediaAggregator(
        twitter_token=twitter_token,
        reddit_id=os.getenv('REDDIT_CLIENT_ID'),
        reddit_secret=os.getenv('REDDIT_CLIENT_SECRET'),
        serpapi_key=serpapi_key,
        redis_url=redis_url
    )
else:
    from services.social_media_collector import SocialMediaAggregator
    social_aggregator = SocialMediaAggregator(
        twitter_token=twitter_token,
        reddit_id=os.getenv('REDDIT_CLIENT_ID'),
        reddit_secret=os.getenv('REDDIT_CLIENT_SECRET')
    )

# Initialize backtest analyzer (MVP 2.0 feature)
from services.backtest_analyzer import BacktestAnalyzer
backtest_analyzer = BacktestAnalyzer(recommendation_engine, social_aggregator)
print("✅ Backtest Analyzer loaded (MVP 2.0)")

# Initialize script generator (MVP 3.0 feature)
try:
    from services.script_generator import script_generator
    SCRIPT_GENERATOR_AVAILABLE = True
    print("✅ Script Generator loaded (MVP 3.0)")
except ImportError:
    script_generator = None
    SCRIPT_GENERATOR_AVAILABLE = False
    print("⚠️ Script Generator not available")

app = FastAPI(
    title="TrendForge AI Backend - MVP 3.1 (Prophet + LLM Script Generation)",
    version="3.1.0",
    description="Intelligent YouTube trend prediction with deep content analysis and AI-powered script generation"
)

# CORS
# 允许的源（包括本地和生产环境）
allowed_origins = [
    "http://localhost:3000",
    "https://*.vercel.app",
    "http://localhost:3001",  # 备用端口
]

# 从环境变量读取额外的允许源
import os
custom_origins = os.getenv("ALLOWED_ORIGINS", "").split(",")
allowed_origins.extend([origin.strip() for origin in custom_origins if origin.strip()])

app.add_middleware(
    CORSMiddleware,
    allow_origins=allowed_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# ==================== Request/Response Models ====================

class ChannelAnalysisRequest(BaseModel):
    videos: List[Dict]  # List of video data
    channel_data: Dict  # Channel metadata
    analyze_transcripts: bool = False  # Whether to analyze video transcripts


class TrendCollectionRequest(BaseModel):
    keywords: List[str]
    geo: str = "US"
    channel_context: Optional[Dict] = None


class RecommendationRequest(BaseModel):
    channel_analysis: Dict
    keywords: List[str]
    geo: str = "US"
    max_recommendations: int = 10


class TitleGenerationRequest(BaseModel):
    recommendation: Dict
    channel_analysis: Dict
    count: int = 3


# MVP 3.0: Prediction request models
class TrendPredictionRequest(BaseModel):
    """Request model for Prophet trend predictions"""
    keywords: List[str]
    forecast_days: int = 7


class StoreTrendDataRequest(BaseModel):
    """Request model for storing trend data"""
    keyword: str
    data: Dict


class FullAnalysisRequest(BaseModel):
    """
    Complete analysis request combining all steps (MVP 3.0)
    """
    videos: List[Dict]
    channel_data: Dict
    geo: str = "US"
    analyze_transcripts: bool = False
    max_recommendations: int = 10
    enable_backtest: bool = True  # 启用回测分析 (MVP 2.0)
    enable_predictions: bool = True  # 启用 Prophet 预测 (MVP 3.0)
    use_simple_mode: bool = False  # 简单模式：跳过社交趋势收集（默认关闭，使用完整分析）


class ScriptGenerationRequest(BaseModel):
    """
    Request model for video script generation (MVP 3.0)
    """
    user_prompt: str  # 用户输入的产品/服务描述
    channel_analysis: Dict  # 频道分析数据
    recommendations: List[Dict]  # AI 推荐的话题列表
    count: int = 3  # 生成脚本数量


# ==================== API Endpoints ====================

@app.get("/")
async def root():
    features = [
        "Deep content analysis with NLP",
        "Video transcript analysis",
        "Enhanced multi-platform social media trends",
        "Intelligent rate limiting and caching",
        "Cross-platform signal verification",
        "Intelligent topic recommendations",
        "AI-powered title generation",
        "Historical video backtest analysis"
    ]
    
    # Add MVP 3.0 features if Prophet is available
    if PROPHET_AVAILABLE:
        features.extend([
            "🔮 Prophet time series prediction (7-day forecast)",
            "🔮 Trend direction detection (rising/falling/stable)",
            "🔮 Peak timing identification",
            "🔮 Confidence intervals (95%)"
        ])
    
    # Add script generation feature if available
    if SCRIPT_GENERATOR_AVAILABLE:
        features.append("✍️ Intelligent video script generation")
    
    return {
        "service": "TrendForge AI Backend",
        "version": "3.1.0" if PROPHET_AVAILABLE else "2.0.1-quickfix",
        "features": features,
        "status": "running",
        "enhancements": {
            "rate_limiting": "✅ Automatic",
            "caching": "✅ Redis + Memory",
            "signal_analysis": "✅ Deep analysis",
            "cross_platform": "✅ Verified signals",
            "time_series_prediction": "✅ Prophet" if PROPHET_AVAILABLE else "❌ Not available"
        }
    }


@app.get("/debug/analyzer")
async def debug_analyzer():
    """检查分析器状态 - 调试端点"""
    from services.enhanced_youtube_analyzer import content_analyzer, audience_analyzer
    
    analyzer_class = type(content_analyzer).__name__
    audience_class = type(audience_analyzer).__name__
    
    # 检查方法是否存在
    has_extract_topics = hasattr(content_analyzer, 'extract_topics_from_titles')
    has_extract_proper_nouns = hasattr(content_analyzer, '_extract_proper_nouns')
    has_extract_proper_nouns_nltk = hasattr(content_analyzer, '_extract_proper_nouns_nltk')
    
    # 获取所有方法
    methods = [m for m in dir(content_analyzer) if not m.startswith('__')]
    
    return {
        "analyzer_class": analyzer_class,
        "audience_class": audience_class,
        "has_extract_topics": has_extract_topics,
        "has_extract_proper_nouns": has_extract_proper_nouns,
        "has_extract_proper_nouns_nltk": has_extract_proper_nouns_nltk,
        "expected_class": "LightweightContentAnalyzer",
        "is_correct": analyzer_class == "LightweightContentAnalyzer",
        "methods_count": len(methods),
        "sample_methods": methods[:10]
    }


@app.get("/debug/full-status")
async def debug_full_status():
    """完整系统状态诊断 - 用于对比 localhost 和生产环境"""
    from services.enhanced_youtube_analyzer import content_analyzer, audience_analyzer
    
    return {
        "backend_version": "3.1.0" if PROPHET_AVAILABLE else "2.0.1-quickfix",
        "prophet_available": PROPHET_AVAILABLE,
        "script_generator_available": SCRIPT_GENERATOR_AVAILABLE,
        "analyzer_type": type(content_analyzer).__name__,
        "audience_analyzer_type": type(audience_analyzer).__name__,
        "recommendation_engine": "PredictiveRecommendationEngine" if USE_PREDICTIVE_ENGINE else "TopicRecommendationEngine",
        "social_aggregator": "EnhancedSocialMediaAggregator" if USE_ENHANCED_COLLECTOR else "SocialMediaAggregator",
        "environment_vars": {
            "TWITTER_BEARER_TOKEN": bool(os.getenv('TWITTER_BEARER_TOKEN')),
            "REDDIT_CLIENT_ID": bool(os.getenv('REDDIT_CLIENT_ID')),
            "REDDIT_CLIENT_SECRET": bool(os.getenv('REDDIT_CLIENT_SECRET')),
            "SERPAPI_KEY": bool(os.getenv('SERPAPI_KEY')),
            "OPENAI_API_KEY": bool(os.getenv('OPENAI_API_KEY')),
            "YOUTUBE_API_KEY": bool(os.getenv('YOUTUBE_API_KEY')),
            "DATABASE_URL": bool(os.getenv('DATABASE_URL')),
            "REDIS_URL": bool(os.getenv('REDIS_URL')),
        },
        "features": {
            "lightweight_analyzer": type(content_analyzer).__name__ == "LightweightContentAnalyzer",
            "predictive_recommendations": USE_PREDICTIVE_ENGINE,
            "prophet_predictions": PROPHET_AVAILABLE,
            "llm_script_generation": SCRIPT_GENERATOR_AVAILABLE,
            "enhanced_social_collector": USE_ENHANCED_COLLECTOR,
        },
        "data_calculation": {
            "viral_potential_calculation": "enhanced_with_data_quality_bonus",
            "predicted_views_calculation": "multi_factor_dynamic",
            "mock_data_generation": "channel_performance_based",
        },
        "timestamp": datetime.utcnow().isoformat()
    }


@app.post("/api/v2/analyze-channel")
async def analyze_channel_endpoint(request: ChannelAnalysisRequest):
    """
    Perform deep channel analysis
    """
    try:
        print(f"📊 Analyzing channel with {len(request.videos)} videos...")
        
        # 强制禁用字幕分析以提速
        analysis = analyze_channel_deeply(
            request.videos,
            request.channel_data
        )
        
        print("✅ Channel analysis complete")
        
        return {
            "success": True,
            "analysis": analysis,
            "analyzed_at": datetime.utcnow().isoformat()
        }
    
    except Exception as e:
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=f"Analysis failed: {str(e)}")


@app.post("/api/v2/collect-social-trends")
async def collect_social_trends_quick(keywords: List[str], geo: str = "US"):
    """
    Quick social trends collection with timeout protection
    """
    try:
        print(f"🔍 Quick collecting trends for {len(keywords)} keywords...")
        
        # 设置超时保护
        try:
            results = await asyncio.wait_for(
                social_aggregator.collect_all_trends(keywords, geo),
                timeout=20.0  # 20秒超时
            )
        except asyncio.TimeoutError:
            print("⚠️ Social trends collection timeout, using partial data")
            # 返回部分数据而不是失败
            results = {
                'merged_trends': [],
                'by_source': {
                    'twitter': [],
                    'reddit': [],
                    'google_trends': []
                },
                'collected_at': datetime.utcnow().isoformat()
            }
        
        return {
            "success": True,
            "trends": results.get('merged_trends', []),
            "by_source": results.get('by_source', {}),
            "collected_at": results.get('collected_at', datetime.utcnow().isoformat()),
        }
    
    except Exception as e:
        print(f"❌ Trend collection error: {e}")
        # 返回空数据而不是报错
        return {
            "success": False,
            "trends": [],
            "by_source": {},
            "error": str(e)
        }


@app.post("/api/v2/generate-recommendations")
async def generate_recommendations(request: RecommendationRequest):
    """
    Generate intelligent topic recommendations
    
    Combines channel characteristics with social trends to recommend
    the best topics for the channel to cover
    """
    try:
        # First, collect social trends
        social_results = await social_aggregator.collect_all_trends(
            request.keywords,
            request.geo
        )
        
        # Generate recommendations
        recommendations = recommendation_engine.generate_recommendations(
            request.channel_analysis,
            social_results['merged_trends'],
            request.max_recommendations
        )
        
        # Generate titles for each recommendation
        for rec in recommendations:
            titles = title_engine.generate_titles(
                rec,
                request.channel_analysis,
                count=3
            )
            rec['suggested_titles'] = titles
        
        return {
            "success": True,
            "recommendations": recommendations,
            "total_count": len(recommendations),
            "generated_at": datetime.utcnow().isoformat()
        }
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Recommendation failed: {str(e)}")


@app.post("/api/v2/generate-titles")
async def generate_titles(request: TitleGenerationRequest):
    """
    Generate optimized title variants for a specific recommendation
    """
    try:
        titles = title_engine.generate_titles(
            request.recommendation,
            request.channel_analysis,
            request.count
        )
        
        return {
            "success": True,
            "titles": titles
        }
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Title generation failed: {str(e)}")


@app.post("/api/v2/full-analysis")
async def full_analysis(request: FullAnalysisRequest):
    """
    🚀 FAST ANALYSIS PIPELINE - Quick Fix Version
    
    Optimizations:
    - Disabled transcript analysis
    - Reduced social media timeout
    - Optional simple mode (skip social trends)
    - Disabled backtest by default
    """
    try:
        print("🔍 Starting FAST analysis pipeline...")
        start_time = datetime.utcnow()
        
        # Step 1: Deep channel analysis (Fast)
        print("📊 Step 1/5: Analyzing channel...")
        channel_analysis = analyze_channel_deeply(
            request.videos,
            request.channel_data
        )
        print(f"   ✅ Channel analyzed in {(datetime.utcnow() - start_time).total_seconds():.1f}s")
        
        # Extract keywords
        keywords = [t['topic'] for t in channel_analysis.get('topics', [])][:5]  # 减少到5个
        
        # Step 2: Collect social trends (with timeout)
        recommendations = []
        social_trends_data = {
            'merged_trends': [],
            'by_source': {},
        }
        
        if not request.use_simple_mode and keywords:
            print("🌐 Step 2/5: Collecting social media trends (quick mode)...")
            
            try:
                # 设置严格的超时
                social_results = await asyncio.wait_for(
                    social_aggregator.collect_all_trends(keywords, request.geo),
                    timeout=15.0  # 15秒超时
                )
                
                social_trends_data = {
                    'merged_trends': social_results.get('merged_trends', [])[:10],
                    'by_source': social_results.get('by_source', {})
                }
                
                print(f"   ✅ Trends collected in {(datetime.utcnow() - start_time).total_seconds():.1f}s")
                
            except asyncio.TimeoutError:
                print("   ⚠️ Social trends timeout, skipping...")
            except Exception as e:
                print(f"   ⚠️ Social trends error: {e}, skipping...")
        else:
            print("📊 Step 2/5: Skipping social trends (simple mode)...")
        
        # Step 3: Generate recommendations (即使没有社交媒体趋势也生成)
        print("💡 Step 3/5: Generating recommendations...")
        
        try:
            # 即使没有社交媒体趋势，也基于频道分析生成推荐
            if social_trends_data['merged_trends']:
                # Use predictive engine if available (MVP 3.0)
                if USE_PREDICTIVE_ENGINE:
                    recommendations = predictive_recommender.generate_recommendations(
                        channel_analysis,
                        social_trends_data['merged_trends'],
                        request.max_recommendations,
                        enable_predictions=request.enable_predictions and PROPHET_AVAILABLE
                    )
                else:
                    recommendations = recommendation_engine.generate_recommendations(
                        channel_analysis,
                        social_trends_data['merged_trends'],
                        request.max_recommendations
                    )
            else:
                # 如果没有社交媒体趋势，基于频道主题生成推荐
                # 使用 predictive_recommender 确保数据格式一致
                print("   ℹ️ No social trends, generating recommendations from channel topics...")
                channel_topics = channel_analysis.get('topics', [])[:request.max_recommendations]
                recommendations = []
                
                # 创建模拟的社交趋势数据，使用频道主题
                # 改进：基于频道主题分数和频道表现生成更合理的模拟数据
                mock_social_trends = []
                high_performers = channel_analysis.get('high_performers', {})
                avg_views = high_performers.get('avg_views', high_performers.get('median_views', 10000))
                
                for idx, topic_data in enumerate(channel_topics):
                    topic = topic_data.get('topic', '')
                    if topic:
                        topic_score = topic_data.get('score', 0.5)
                        
                        # 改进的模拟数据生成逻辑：
                        # 1. composite_score: 基于主题分数，但考虑频道表现和排名
                        #    高表现频道 + 高主题分数 + 排名 = 更高的热度
                        channel_performance_factor = min(1.2, avg_views / 50000)  # 频道表现系数
                        rank_factor = (len(channel_topics) - idx) / len(channel_topics)  # 排名因子（0-1）
                        base_composite = topic_score * 100
                        # 对于高表现频道和排名靠前的主题，给予更高的基础热度
                        # 添加排名因子确保不同话题有不同的 composite_score
                        composite_score = min(100, base_composite * (0.7 + channel_performance_factor * 0.2 + rank_factor * 0.1) + idx * 2)
                        
                        # 2. growth_rate: 基于主题分数和排名
                        #    排名越靠前，增长率越高（模拟新兴趋势）
                        rank_factor = (len(channel_topics) - idx) / len(channel_topics)  # 排名因子
                        # 为不同话题生成不同的增长率，确保差异化
                        growth_rate = topic_score * 30 + rank_factor * 20 + (idx % 10) * 2  # 30-70 范围，添加多样性
                        
                        # 3. 添加更多上下文信息
                        # 生成模拟的 hashtags 和 subreddits（基于主题关键词）
                        # 提取关键词的主要单词，生成相关的 hashtags
                        topic_words = topic.lower().split()
                        mock_hashtags = []
                        for word in topic_words[:3]:  # 最多3个单词
                            if len(word) > 3:  # 只处理长度>3的单词
                                # 生成相关 hashtag（移除空格，首字母大写）
                                hashtag = word.replace(' ', '').title()
                                mock_hashtags.append(hashtag)
                        
                        # 如果没有生成 hashtags，使用关键词本身
                        if not mock_hashtags:
                            mock_hashtags = [topic.replace(' ', '').title()[:20]]  # 限制长度
                        
                        # 生成模拟的 subreddits（基于主题类别）
                        # 根据主题内容推断可能的 subreddits
                        mock_subreddits = []
                        topic_lower = topic.lower()
                        # 常见 subreddits 映射
                        if any(word in topic_lower for word in ['trading', 'stock', 'invest', 'finance']):
                            mock_subreddits = ['stocks', 'investing', 'wallstreetbets']
                        elif any(word in topic_lower for word in ['tech', 'software', 'programming', 'code']):
                            mock_subreddits = ['technology', 'programming', 'software']
                        elif any(word in topic_lower for word in ['game', 'gaming', 'play']):
                            mock_subreddits = ['gaming', 'games', 'pcgaming']
                        elif any(word in topic_lower for word in ['video', 'youtube', 'content']):
                            mock_subreddits = ['videos', 'youtube', 'content']
                        else:
                            # 通用 subreddits
                            mock_subreddits = ['videos', 'technology', 'gaming']
                        
                        mock_trend = {
                            'keyword': topic,
                            'composite_score': round(composite_score, 2),
                            'growth_rate': round(growth_rate, 2),
                            'sources': ['channel_analysis'],
                            'rising_queries': [topic],  # 至少包含关键词本身
                            'twitter_hashtags': mock_hashtags[:5],  # 最多5个 hashtags
                            'reddit_subreddits': mock_subreddits[:3],  # 最多3个 subreddits
                            'trend_score': round(composite_score, 2),  # 兼容字段
                            'interest_over_time': [],  # 时间序列数据（空，因为没有真实数据）
                            'related_queries': []  # 相关查询（空）
                        }
                        mock_social_trends.append(mock_trend)
                
                # 使用 predictive_recommender 生成推荐（确保格式一致）
                if USE_PREDICTIVE_ENGINE and mock_social_trends:
                    recommendations = predictive_recommender.generate_recommendations(
                        channel_analysis,
                        mock_social_trends,
                        request.max_recommendations,
                        enable_predictions=request.enable_predictions and PROPHET_AVAILABLE
                    )
                elif mock_social_trends:
                    # Fallback to intelligent_recommender
                    recommendations = recommendation_engine.generate_recommendations(
                        channel_analysis,
                        mock_social_trends,
                        request.max_recommendations
                    )
                else:
                    # 最后的 fallback：手动生成基础推荐
                    high_performers = channel_analysis.get('high_performers', {})
                    avg_views = high_performers.get('avg_views', high_performers.get('median_views', 10000))
                    
                    for topic_data in channel_topics:
                        topic = topic_data.get('topic', '')
                        if topic:
                            topic_score = topic_data.get('score', 0.5)
                            match_score = topic_score * 100
                            
                            # 生成模拟的 hashtags 和 subreddits（与上面相同的逻辑）
                            topic_words = topic.lower().split()
                            mock_hashtags = []
                            for word in topic_words[:3]:
                                if len(word) > 3:
                                    hashtag = word.replace(' ', '').title()
                                    mock_hashtags.append(hashtag)
                            if not mock_hashtags:
                                mock_hashtags = [topic.replace(' ', '').title()[:20]]
                            
                            mock_subreddits = []
                            topic_lower = topic.lower()
                            if any(word in topic_lower for word in ['trading', 'stock', 'invest', 'finance']):
                                mock_subreddits = ['stocks', 'investing', 'wallstreetbets']
                            elif any(word in topic_lower for word in ['tech', 'software', 'programming', 'code']):
                                mock_subreddits = ['technology', 'programming', 'software']
                            elif any(word in topic_lower for word in ['game', 'gaming', 'play']):
                                mock_subreddits = ['gaming', 'games', 'pcgaming']
                            elif any(word in topic_lower for word in ['video', 'youtube', 'content']):
                                mock_subreddits = ['videos', 'youtube', 'content']
                            else:
                                mock_subreddits = ['videos', 'technology', 'gaming']
                            
                            # 使用与 predictive_recommender 相同的格式
                            recommendations.append({
                                'keyword': topic,
                                'match_score': match_score,
                                'viral_potential': 50 + (topic_score * 30),  # 50-80 范围
                                'performance_score': 60 + (topic_score * 30),  # 60-90 范围
                                'relevance_score': 80 + (topic_score * 20),  # 80-100 范围（高度相关）
                                'opportunity_score': 50 + (topic_score * 30),
                                'composite_social_score': 0,  # 无社交媒体数据
                                'reasoning': f"基于频道内容分析，'{topic}' 是该频道的核心主题之一，与频道风格高度匹配",
                                'content_angle': f"深入探讨 {topic} 的相关内容，结合频道特色",
                                'predicted_performance': {
                                    'tier': 'good' if match_score >= 60 else 'moderate',
                                    'predicted_views': int(avg_views * (0.8 + topic_score * 0.4)),  # 动态计算
                                    'description': '基于频道主题的推荐，预计表现良好' if match_score >= 60 else '预计表现中等，稳定流量',
                                    'confidence': int(match_score)
                                },
                                'suggested_format': channel_analysis.get('content_style', {}).get('primary_style', 'tutorial'),
                                'urgency': 'high' if match_score >= 80 else ('medium' if match_score >= 60 else 'normal'),
                                'sources': ['channel_analysis'],
                                'related_info': {
                                    'rising_queries': [topic],
                                    'hashtags': mock_hashtags[:5],
                                    'subreddits': mock_subreddits[:3]
                                }
                            })
            
            # Generate titles for all recommendations
            for rec in recommendations[:min(5, len(recommendations))]:
                try:
                    titles = title_engine.generate_titles(
                        rec,
                        channel_analysis,
                        count=3
                    )
                    rec['suggested_titles'] = titles
                except Exception as e:
                    print(f"   ⚠️ Title generation failed for {rec.get('keyword', 'unknown')}: {e}")
                    rec['suggested_titles'] = []
            
            print(f"   ✅ Generated {len(recommendations)} recommendations in {(datetime.utcnow() - start_time).total_seconds():.1f}s")
            
        except Exception as e:
            print(f"   ⚠️ Recommendation error: {e}")
            import traceback
            traceback.print_exc()
            recommendations = []
        
        # Step 4: Backtest analysis (if enabled and sufficient videos)
        backtest_results = None
        backtest_status = {
            "enabled": request.enable_backtest,
            "video_count": len(request.videos),
            "meets_requirements": len(request.videos) >= 10,
            "analyzer_available": backtest_analyzer is not None,
            "status": "not_run"
        }
        
        # 回测要求：至少10个视频，推荐50+个视频以获得更准确的结果
        min_videos_for_backtest = 10
        recommended_videos = 50
        if request.enable_backtest and len(request.videos) >= min_videos_for_backtest and backtest_analyzer:
            print("📈 Step 4/5: Running backtest analysis...")
            step_start = datetime.utcnow()
            try:
                # Use ML model if sufficient data (>=20 videos)
                use_ml = len(request.videos) >= 20
                backtest_status["ml_enabled"] = use_ml
                # Add timeout for backtest (60 seconds for 50+ videos)
                timeout_seconds = 60.0 if len(request.videos) >= 50 else 30.0
                # backtest_predictions 现在是同步函数，直接在线程中调用
                backtest_results = await asyncio.wait_for(
                    asyncio.to_thread(
                        backtest_analyzer.backtest_predictions,
                        request.videos,
                        channel_analysis,
                        None,  # historical_trends
                        use_ml  # use_ml_model
                    ),
                    timeout=timeout_seconds
                )
                ml_status = "enabled" if use_ml else "disabled (insufficient data)"
                print(f"   ✅ Backtest complete: {backtest_results.get('total_videos_tested', 0)} videos tested (ML: {ml_status})")
                backtest_status["status"] = "success"
                backtest_status["videos_tested"] = backtest_results.get('total_videos_tested', 0)
            except asyncio.TimeoutError:
                print("   ⚠️ Backtest timeout (30s), skipping backtest")
                backtest_results = None
                backtest_status["status"] = "timeout"
            except Exception as e:
                print(f"   ⚠️ Backtest failed: {e}")
                import traceback
                traceback.print_exc()
                backtest_results = None
                backtest_status["status"] = "error"
                backtest_status["error"] = str(e)
            finally:
                backtest_time = (datetime.utcnow() - step_start).total_seconds()
                print(f"   ⏱️  Backtest: {backtest_time:.2f}s")
        elif request.enable_backtest:
            if len(request.videos) < 10:
                print(f"   ⚠️ Backtest skipped: insufficient videos ({len(request.videos)} < 10)")
                backtest_status["status"] = "insufficient_videos"
            elif not backtest_analyzer:
                print("   ⚠️ Backtest skipped: analyzer not available")
                backtest_status["status"] = "analyzer_unavailable"
        else:
            print("   ℹ️ Backtest disabled in request")
            backtest_status["status"] = "disabled"
        
        # Step 5: Prophet predictions (if enabled and available)
        trend_predictions = None
        emerging_trends = None
        if request.enable_predictions and PROPHET_AVAILABLE and trend_predictor:
            print("🔮 Step 5/5: Generating Prophet predictions...")
            step_start = datetime.utcnow()
            try:
                # Extract keywords from recommendations (use all for better coverage)
                prediction_keywords = [r['keyword'] for r in recommendations[:10]]  # Top 10 recommendations
                
                print(f"   📋 Keywords for prediction: {prediction_keywords}")
                
                if prediction_keywords:
                    # Use sync method in thread (Prophet is CPU-bound)
                    predictions_result = await asyncio.to_thread(
                        trend_predictor.predict_trends,
                        prediction_keywords,
                        7  # forecast_days
                    )
                    
                    trend_predictions = predictions_result.get('predictions', [])
                    emerging_trends_raw = predictions_result.get('emerging_trends', [])
                    
                    print(f"   📊 Predictions generated: {len(trend_predictions)} predictions, {len(emerging_trends_raw)} emerging trends")
                    if trend_predictions:
                        print(f"   ✅ First prediction: {trend_predictions[0].get('keyword')}, peak_day={trend_predictions[0].get('peak_day')}")
                    
                    # Enhance recommendations with predictions
                    if trend_predictions:
                        prediction_map = {p['keyword']: p for p in trend_predictions}
                        for rec in recommendations:
                            keyword = rec.get('keyword')
                            if keyword in prediction_map:
                                pred_data = prediction_map[keyword]
                                # Add full prediction data to recommendation
                                rec['prediction'] = {
                                    'trend_direction': pred_data.get('trend_direction'),
                                    'trend_strength': pred_data.get('trend_strength'),
                                    'confidence': pred_data.get('confidence'),
                                    'peak_day': pred_data.get('peak_day'),
                                    'peak_score': pred_data.get('peak_score'),
                                    'summary': pred_data.get('summary', ''),
                                    'predictions': pred_data.get('predictions', [])[:7]  # 7-day forecast
                                }
                                # Update final score with prediction
                                if 'final_score' not in rec:
                                    rec['final_score'] = rec.get('match_score', 0)
                                # Add prediction bonus to final score
                                if pred_data.get('trend_direction') == 'rising' and pred_data.get('confidence', 0) > 70:
                                    rec['final_score'] = min(100, rec['final_score'] * 1.1)  # 10% bonus
                                    rec['urgency'] = 'urgent' if pred_data.get('peak_day', 7) <= 3 else 'high'
                    
                    # Process emerging trends
                    if emerging_trends_raw:
                        emerging_trends = []
                        for trend in emerging_trends_raw:
                            # Calculate urgency score
                            base_score = trend.get('confidence', 0) * trend.get('trend_strength', 0) / 100
                            peak_day = trend.get('peak_day')
                            urgency = base_score
                            if peak_day and peak_day <= 3:
                                urgency = min(100, base_score * 1.5)
                            elif peak_day and peak_day <= 5:
                                urgency = min(100, base_score * 1.2)
                            
                            emerging_trends.append({
                                'keyword': trend.get('keyword'),
                                'confidence': trend.get('confidence', 0),
                                'trend_strength': trend.get('trend_strength', 0),
                                'peak_day': trend.get('peak_day'),
                                'peak_score': trend.get('peak_score'),
                                'summary': trend.get('summary', ''),
                                'urgency': urgency
                            })
                    else:
                        # Extract emerging trends from predictions if not provided
                        emerging_trends = []
                        if trend_predictions:
                            for pred in trend_predictions:
                                if (pred.get('trend_direction') == 'rising' and 
                                    pred.get('confidence', 0) >= 70 and 
                                    pred.get('trend_strength', 0) > 50):
                                    base_score = pred.get('confidence', 0) * pred.get('trend_strength', 0) / 100
                                    peak_day = pred.get('peak_day')
                                    urgency = base_score
                                    if peak_day and peak_day <= 3:
                                        urgency = min(100, base_score * 1.5)
                                    elif peak_day and peak_day <= 5:
                                        urgency = min(100, base_score * 1.2)
                                    
                                    emerging_trends.append({
                                        'keyword': pred['keyword'],
                                        'confidence': pred['confidence'],
                                        'trend_strength': pred['trend_strength'],
                                        'peak_day': pred.get('peak_day'),
                                        'peak_score': pred.get('peak_score'),
                                        'summary': pred.get('summary', ''),
                                        'urgency': urgency
                                    })
                    
                    print(f"   ✅ Predictions generated: {len(trend_predictions)} keywords, {len(emerging_trends) if emerging_trends else 0} emerging trends")
                else:
                    print("   ℹ️ No keywords for prediction")
            except Exception as e:
                print(f"   ⚠️ Prediction error: {e}")
                import traceback
                traceback.print_exc()
            finally:
                prediction_time = (datetime.utcnow() - step_start).total_seconds()
                print(f"   ⏱️  Predictions: {prediction_time:.2f}s")
        elif request.enable_predictions:
            if not PROPHET_AVAILABLE:
                print("   ℹ️ Prophet not available, skipping predictions")
            elif not trend_predictor:
                print("   ℹ️ Trend predictor not initialized, skipping predictions")
        
        total_time = (datetime.utcnow() - start_time).total_seconds()
        print(f"✅ Analysis complete in {total_time:.1f}s!")
        
        response = {
            "success": True,
            "version": "3.1.0" if PROPHET_AVAILABLE else "2.0.1-quickfix",
            "channel_analysis": {
                "topics": channel_analysis.get('topics', [])[:15],
                "content_style": channel_analysis.get('content_style', {}),
                "target_audience": channel_analysis.get('target_audience', {}),
                "high_performers": channel_analysis.get('high_performers', {}),
                "total_videos_analyzed": channel_analysis.get('total_videos_analyzed', 0)
            },
            "social_trends": {
                "merged_trends": social_trends_data['merged_trends'],
                "source_breakdown": {
                    "twitter_count": len(social_trends_data.get('by_source', {}).get('twitter', [])),
                    "reddit_count": len(social_trends_data.get('by_source', {}).get('reddit', [])),
                    "google_trends_count": len(social_trends_data.get('by_source', {}).get('google_trends', []))
                }
            },
            "recommendations": recommendations,
            "summary": {
                "total_recommendations": len(recommendations),
                "urgent_count": sum(1 for r in recommendations if r.get('urgency') == 'urgent'),
                "high_match_count": sum(1 for r in recommendations if r.get('match_score', 0) > 75),
                "avg_match_score": sum(r.get('match_score', 0) for r in recommendations) / len(recommendations) if recommendations else 0,
                "predicted_rising_count": sum(1 for r in recommendations if r.get('prediction', {}).get('trend_direction') == 'rising') if request.enable_predictions else 0
            },
            "performance": {
                "analysis_time_seconds": total_time,
                "simple_mode": request.use_simple_mode,
                "backtest_enabled": request.enable_backtest,
                "predictions_enabled": request.enable_predictions and PROPHET_AVAILABLE
            },
            "analyzed_at": datetime.utcnow().isoformat()
        }
        
        # Add backtest results and status
        if backtest_results:
            response["backtest"] = backtest_results
            response["backtest_status"] = backtest_status
        else:
            # Always include backtest status, even if no results
            response["backtest"] = None
            response["backtest_status"] = backtest_status
        
        # Add trend predictions and emerging trends (MVP 3.0)
        # Always include these fields, even if empty, for frontend consistency
        if request.enable_predictions and PROPHET_AVAILABLE:
            response["trend_predictions"] = trend_predictions if trend_predictions else []
            response["emerging_trends"] = emerging_trends if emerging_trends else []
        else:
            response["trend_predictions"] = []
            response["emerging_trends"] = []
        
        return response
    
    except Exception as e:
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=f"Full analysis failed: {str(e)}")


@app.post("/api/v2/quick-analysis")
async def quick_analysis(videos: List[Dict], channel_data: Dict):
    """
    ⚡ NEW: Ultra-fast analysis (channel only, no social trends)
    """
    try:
        print("⚡ Starting quick analysis (channel only)...")
        
        analysis = analyze_channel_deeply(videos, channel_data)
        
        return {
            "success": True,
            "version": "3.1.0" if PROPHET_AVAILABLE else "2.0.1-quickfix",
            "channel_analysis": {
                "topics": analysis.get('topics', [])[:15],
                "content_style": analysis.get('content_style', {}),
                "target_audience": analysis.get('target_audience', {}),
                "high_performers": analysis.get('high_performers', {}),
            },
            "analyzed_at": datetime.utcnow().isoformat()
        }
    
    except Exception as e:
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=f"Quick analysis failed: {str(e)}")


@app.get("/health")
async def health_check():
    """Enhanced health check with service status"""
    
    # Check YouTube API key (used by frontend, but we can verify if it's configured)
    youtube_api_key = os.getenv('YOUTUBE_API_KEY')
    youtube_configured = bool(youtube_api_key)
    
    social_status = {
        "twitter": social_aggregator.twitter.client is not None if hasattr(social_aggregator, 'twitter') else False,
        "reddit": social_aggregator.reddit.reddit is not None if hasattr(social_aggregator, 'reddit') else False,
        "google_trends": True,
        "serpapi": social_aggregator.serpapi.available if hasattr(social_aggregator, 'serpapi') else False,
        "youtube": youtube_configured,  # YouTube API (used by frontend)
        "cache": (hasattr(social_aggregator, 'signal_aggregator') and 
                 hasattr(social_aggregator.signal_aggregator, 'cache') and 
                 social_aggregator.signal_aggregator.cache.redis_client is not None) or
                 (hasattr(social_aggregator, 'cache') and 
                 hasattr(social_aggregator.cache, 'redis_client') and 
                 social_aggregator.cache.redis_client is not None),
        "prophet": PROPHET_AVAILABLE and trend_predictor is not None,
        "script_generator": SCRIPT_GENERATOR_AVAILABLE and script_generator is not None
    }
    
    warnings = [
        f"{service} not configured" 
        for service, available in social_status.items() 
        if not available and service not in ['cache', 'prophet']
    ]
    
    return {
        "status": "healthy",
        "version": "3.1.0" if PROPHET_AVAILABLE else "2.0.1-quickfix",
        "timestamp": datetime.utcnow().isoformat(),
        "capabilities": {
            "nlp_analysis": True,
            "transcript_analysis": True,
            "social_media": True,
            "intelligent_recommendations": True,
            "title_generation": True,
            "rate_limiting": True,
            "caching": True,
            "cross_platform_verification": True,
            "time_series_prediction": PROPHET_AVAILABLE and trend_predictor is not None,
            "script_generation": SCRIPT_GENERATOR_AVAILABLE and script_generator is not None,
            "youtube_data_collection": youtube_configured,  # YouTube API capability
        },
        "services": social_status,
        "warnings": warnings
    }


# ==================== MVP 3.0: Prophet Prediction Endpoints ====================

@app.get("/api/v3/debug-runtime")
async def debug_runtime():
    """
    🔧 Debug endpoint to verify runtime environment and loaded trend predictor code.
    """
    try:
        import sys
        import inspect
        from services import trend_predictor as trend_predictor_module

        confidence_src = inspect.getsource(
            trend_predictor_module.TrendPredictionEngine._calculate_prediction_confidence
        ).splitlines()

        return {
            "success": True,
            "sys_executable": sys.executable,
            "trend_predictor_module_file": getattr(trend_predictor_module, "__file__", None),
            "prophet_available": bool(PROPHET_AVAILABLE and trend_predictor is not None),
            "confidence_fn_head": confidence_src[:25],
            "timestamp": datetime.utcnow().isoformat(),
        }
    except Exception as e:
        return {
            "success": False,
            "error": str(e),
            "timestamp": datetime.utcnow().isoformat(),
        }

@app.post("/api/v3/predict-trends")
async def predict_trends(request: TrendPredictionRequest):
    """
    🔮 MVP 3.0: Predict future trends using Prophet time series forecasting
    
    Returns 7-day forecast with confidence intervals, trend direction, and peak timing
    """
    if not PROPHET_AVAILABLE or not trend_predictor:
        raise HTTPException(
            status_code=503,
            detail="Prophet prediction engine not available. Install: pip install prophet"
        )
    
    try:
        print(f"🔮 Predicting trends for {len(request.keywords)} keywords...")
        
        # Use sync method in thread (Prophet is CPU-bound)
        result = await asyncio.to_thread(
            trend_predictor.predict_trends,
            request.keywords,
            request.forecast_days
        )
        
        return {
            "success": True,
            "predictions": result.get('predictions', []),
            "emerging_trends": result.get('emerging_trends', []),
            "forecast_days": request.forecast_days,
            "generated_at": datetime.utcnow().isoformat()
        }
    
    except Exception as e:
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=f"Prediction failed: {str(e)}")


@app.post("/api/v3/store-trend-data")
async def store_trend_data(request: StoreTrendDataRequest):
    """
    🔮 MVP 3.0: Store current trend data for future predictions
    
    This endpoint allows you to store historical trend data that will be used
    to improve future predictions. Data is stored in the database configured
    via DATABASE_URL environment variable.
    """
    if not trend_predictor:
        raise HTTPException(
            status_code=503,
            detail="Trend predictor not initialized"
        )
    
    try:
        await trend_predictor.store_trend_data(request.keyword, request.data)
        
        return {
            "success": True,
            "message": f"Trend data stored for '{request.keyword}'",
            "stored_at": datetime.utcnow().isoformat()
        }
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Storage failed: {str(e)}")


@app.post("/api/v3/generate-scripts")
async def generate_scripts(request: ScriptGenerationRequest):
    """
    ✍️ MVP 3.0: Generate video scripts based on channel analysis and recommendations
    
    Generates multiple script variations based on:
    - User product/service description
    - Channel analysis (style, audience, high performers)
    - AI recommendations (topics, match scores, viral potential)
    
    Returns scripts with performance predictions and reasoning.
    """
    if not SCRIPT_GENERATOR_AVAILABLE or not script_generator:
        raise HTTPException(
            status_code=503,
            detail="Script generator not available"
        )
    
    try:
        print(f"✍️ Generating {request.count} scripts for prompt: {request.user_prompt[:50]}...")
        
        # Use sync method in thread (script generation is CPU-bound)
        scripts = await asyncio.to_thread(
            script_generator.generate_scripts,
            request.user_prompt,
            request.channel_analysis,
            request.recommendations,
            request.count
        )
        
        print(f"   ✅ Generated {len(scripts)} scripts")
        
        return {
            "success": True,
            "scripts": scripts,
            "count": len(scripts),
            "generated_at": datetime.utcnow().isoformat()
        }
    
    except Exception as e:
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=f"Script generation failed: {str(e)}")


if __name__ == "__main__":
    import uvicorn
    version_str = "MVP 3.1 (Prophet + LLM)" if PROPHET_AVAILABLE else "MVP 2.0"
    print(f"🚀 Starting TrendForge Backend ({version_str})")
    if PROPHET_AVAILABLE:
        print("   ✅ Prophet time series prediction enabled")
        print("   ✅ Predictive recommendations enabled")
    else:
        print("   ⚠️ Prophet not available, using MVP 2.0 features")
    print("   - Features: Deep analysis, Social trends, Recommendations, Backtest")
    print("   - Optimized: Social media collection with timeouts")
    print("   - New: Simple mode for faster analysis")
    uvicorn.run(app, host="0.0.0.0", port=8000, log_level="info")
