"""
Intelligent Topic Recommendation Engine
Combines channel analysis with social media trends for personalized recommendations
"""

from typing import List, Dict, Optional
import numpy as np
from datetime import datetime


class TopicRecommendationEngine:
    """
    Advanced recommendation engine that matches trending topics with channel characteristics
    """
    
    def __init__(self):
        self.min_match_score = 30  # Minimum score to recommend
    
    def generate_recommendations(
        self,
        channel_analysis: Dict,
        social_trends: List[Dict],
        max_recommendations: int = 10
    ) -> List[Dict]:
        """
        Generate personalized topic recommendations
        
        Args:
            channel_analysis: Deep analysis of the channel
            social_trends: Trending topics from social media
            max_recommendations: Maximum number of recommendations
        
        Returns:
            List of recommended topics with detailed reasoning
        """
        recommendations = []
        
        # Extract channel characteristics
        channel_topics = [t['topic'] for t in channel_analysis.get('topics', [])]
        content_style = channel_analysis.get('content_style', {})
        target_audience = channel_analysis.get('target_audience', {})
        high_performers = channel_analysis.get('high_performers', {})
        
        for trend in social_trends:
            # Calculate match score
            match_result = self._calculate_match_score(
                trend,
                channel_topics,
                content_style,
                target_audience,
                high_performers
            )
            
            if match_result['match_score'] >= self.min_match_score:
                recommendations.append({
                    'keyword': trend['keyword'],
                    'match_score': match_result['match_score'],
                    'viral_potential': match_result['viral_potential'],
                    'performance_score': match_result['performance_score'],
                    'relevance_score': match_result['relevance_score'],
                    'opportunity_score': match_result['opportunity_score'],
                    'composite_social_score': trend.get('composite_score', 0),
                    'reasoning': match_result['reasoning'],
                    'content_angle': match_result['content_angle'],
                    'predicted_performance': match_result['predicted_performance'],
                    'suggested_format': match_result['suggested_format'],
                    'urgency': match_result['urgency'],
                    'sources': trend.get('sources', []),
                    'related_info': {
                        'rising_queries': trend.get('rising_queries', []),
                        'hashtags': trend.get('twitter_hashtags', []),
                        'subreddits': trend.get('reddit_subreddits', [])
                    }
                })
        
        # Deduplicate by keyword first (keep the one with highest match_score)
        seen_keywords = {}
        deduplicated = []
        for rec in recommendations:
            keyword_lower = rec['keyword'].lower().strip()
            if keyword_lower not in seen_keywords:
                seen_keywords[keyword_lower] = rec
                deduplicated.append(rec)
            else:
                # If duplicate, keep the one with higher match_score
                existing_rec = seen_keywords[keyword_lower]
                if rec['match_score'] > existing_rec['match_score']:
                    # Replace in both dict and list
                    seen_keywords[keyword_lower] = rec
                    existing_idx = deduplicated.index(existing_rec)
                    deduplicated[existing_idx] = rec
        
        # Sort by match score after deduplication
        deduplicated.sort(key=lambda x: x['match_score'], reverse=True)
        
        return deduplicated[:max_recommendations]
    
    def _calculate_match_score(
        self,
        trend: Dict,
        channel_topics: List[str],
        content_style: Dict,
        target_audience: Dict,
        high_performers: Dict
    ) -> Dict:
        """
        Calculate comprehensive match score between trend and channel
        
        New algorithm (as per user feedback):
        - 互联网热度 (Viral Potential): 40%
        - 表现潜力 (Performance Score): 25%
        - 内容相关性 (Relevance Score): 35%
        
        Returns a dict with match_score and detailed reasoning
        """
        keyword = trend['keyword'].lower()
        
        # 1. 互联网热度 (Viral Potential) - 40%
        viral_potential = self._calculate_viral_potential(trend)
        
        # 2. 表现潜力 (Performance Score) - 25%
        performance_score = self._calculate_performance_potential(
            trend, 
            high_performers,
            channel_topics,
            content_style,
            target_audience
        )
        
        # 3. 内容相关性 (Relevance Score) - 35%
        # Combine topic relevance, style compatibility, and audience fit
        topic_relevance = self._calculate_topic_relevance(keyword, channel_topics)
        style_score = self._calculate_style_compatibility(keyword, content_style)
        audience_score = self._calculate_audience_fit(keyword, target_audience)
        relevance_score = (topic_relevance * 0.5 + style_score * 0.3 + audience_score * 0.2)
        
        # 4. Opportunity Score (for display purposes)
        opportunity_score = self._calculate_opportunity_score(trend)
        
        # Composite match score with new weights
        match_score = (
            viral_potential * 0.4 +      # 互联网热度 40%
            performance_score * 0.25 +    # 表现潜力 25%
            relevance_score * 0.35        # 内容相关性 35%
        )
        
        # Generate reasoning with new scores
        reasoning = self._generate_reasoning(
            keyword,
            viral_potential,
            performance_score,
            relevance_score,
            trend
        )
        
        # Generate content angle
        content_angle = self._generate_content_angle(
            keyword,
            content_style,
            trend
        )
        
        # Predict performance with new algorithm
        predicted_performance = self._predict_performance(
            match_score,
            viral_potential,
            performance_score,
            relevance_score,
            high_performers
        )
        
        # Suggest format
        suggested_format = self._suggest_format(keyword, content_style)
        
        # Determine urgency based on viral potential and growth
        urgency = self._determine_urgency(trend, viral_potential)
        
        return {
            'match_score': round(match_score, 2),
            'viral_potential': round(viral_potential, 2),
            'performance_score': round(performance_score, 2),
            'relevance_score': round(relevance_score, 2),
            'opportunity_score': round(opportunity_score, 2),
            'reasoning': reasoning,
            'content_angle': content_angle,
            'predicted_performance': predicted_performance,
            'suggested_format': suggested_format,
            'urgency': urgency
        }
    
    def _calculate_topic_relevance(self, keyword: str, channel_topics: List[str]) -> float:
        """
        Calculate how relevant the trending topic is to channel's existing topics
        """
        if not channel_topics:
            return 50  # Neutral score if no topics
        
        keyword_words = set(keyword.split())
        
        # Check for exact matches
        exact_matches = sum(1 for topic in channel_topics if topic in keyword)
        
        # Check for word overlaps
        word_overlaps = 0
        for topic in channel_topics:
            topic_words = set(topic.split())
            overlap = len(keyword_words & topic_words)
            word_overlaps += overlap
        
        # Calculate score
        relevance = (exact_matches * 20) + (word_overlaps * 10)
        
        return min(100, max(20, relevance))
    
    def _calculate_style_compatibility(self, keyword: str, content_style: Dict) -> float:
        """
        Check if trending topic fits the channel's content style
        """
        if not content_style:
            return 50
        
        primary_style = content_style.get('primary_style', '').lower()
        
        # Style-keyword compatibility matrix
        style_keywords = {
            'tutorial': ['how', 'guide', 'tips', 'learn', 'tutorial'],
            'review': ['review', 'unbox', 'test', 'compare', 'vs'],
            'entertainment': ['funny', 'challenge', 'prank', 'reaction'],
            'news': ['news', 'update', 'breaking', 'latest'],
            'educational': ['explain', 'science', 'facts', 'history'],
            'gaming': ['game', 'gaming', 'play', 'walkthrough'],
            'tech': ['tech', 'gadget', 'phone', 'software']
        }
        
        style_keywords_set = set(style_keywords.get(primary_style, []))
        keyword_lower = keyword.lower()
        
        # Check if keyword contains style-related terms
        matches = sum(1 for kw in style_keywords_set if kw in keyword_lower)
        
        compatibility = 50 + (matches * 15)
        
        return min(100, compatibility)
    
    def _calculate_audience_fit(self, keyword: str, target_audience: Dict) -> float:
        """
        Check if topic fits the target audience
        """
        if not target_audience:
            return 50
        
        age_group = target_audience.get('primary_age_group', 'general')
        
        # Age-appropriate topic indicators
        age_indicators = {
            'kids': ['kids', 'fun', 'cartoon', 'toy', 'game'],
            'teens': ['teen', 'tiktok', 'viral', 'meme', 'trend'],
            'young_adults': ['college', 'career', 'lifestyle', 'tech'],
            'adults': ['professional', 'finance', 'business', 'investment'],
            'all_ages': ['family', 'everyone', 'popular', 'trending']
        }
        
        indicators = age_indicators.get(age_group, age_indicators['all_ages'])
        keyword_lower = keyword.lower()
        
        matches = sum(1 for indicator in indicators if indicator in keyword_lower)
        
        fit_score = 50 + (matches * 12)
        
        return min(100, fit_score)
    
    def _calculate_viral_potential(self, trend: Dict) -> float:
        """
        计算互联网热度 (Viral Potential)
        衡量话题在社交媒体的讨论热度
        
        计算依据：
        - Twitter 讨论量和转发数
        - Reddit 帖子数和点赞数
        - Google Trends 搜索增长率
        - 跨平台出现次数
        """
        composite_score = trend.get('composite_score', 0)
        growth_rate = trend.get('growth_rate', 0)
        source_count = len(trend.get('sources', []))
        
        # 基础热度分数
        base_score = composite_score
        
        # 增长加成
        growth_bonus = min(30, growth_rate * 0.3)  # 最多30分加成
        
        # 跨平台加成
        platform_bonus = min(20, (source_count - 1) * 10)  # 多平台额外加分
        
        viral_score = base_score + growth_bonus + platform_bonus
        
        return min(100, round(viral_score, 2))
    
    def _calculate_performance_potential(
        self,
        trend: Dict,
        high_performers: Dict,
        channel_topics: List[str],
        content_style: Dict,
        target_audience: Dict
    ) -> float:
        """
        计算表现潜力 (Performance Score)
        预测该话题视频的播放表现
        
        基于：
        - 话题热度趋势
        - 频道历史平均播放
        - 相似话题的表现
        - 时效性加成
        """
        # 基础热度
        viral_potential = self._calculate_viral_potential(trend)
        
        # 相关性加成（相关性越高，表现潜力越大）
        keyword = trend['keyword'].lower()
        topic_relevance = self._calculate_topic_relevance(keyword, channel_topics)
        style_score = self._calculate_style_compatibility(keyword, content_style)
        audience_score = self._calculate_audience_fit(keyword, target_audience)
        relevance_bonus = (topic_relevance * 0.5 + style_score * 0.3 + audience_score * 0.2) * 0.3
        
        # 时效性加成（快速增长的话题有更高潜力）
        growth_rate = trend.get('growth_rate', 0)
        timeliness_bonus = min(20, growth_rate * 0.2)
        
        # 综合表现潜力
        performance_score = viral_potential * 0.6 + relevance_bonus + timeliness_bonus
        
        return min(100, round(performance_score, 2))
    
    def _calculate_opportunity_score(self, trend: Dict) -> float:
        """
        Calculate opportunity score based on social media engagement
        (Kept for backward compatibility)
        """
        return self._calculate_viral_potential(trend)
    
    def _generate_reasoning(
        self,
        keyword: str,
        viral_potential: float,
        performance_score: float,
        relevance_score: float,
        trend: Dict
    ) -> str:
        """
        Generate human-readable reasoning for the recommendation
        """
        reasons = []
        
        # 互联网热度
        if viral_potential >= 90:
            reasons.append("🔥 爆火话题（全网讨论）")
        elif viral_potential >= 70:
            reasons.append("⚡ 热门话题（快速上升）")
        elif viral_potential >= 50:
            reasons.append("📈 上升话题（逐渐流行）")
        else:
            reasons.append("💡 小众话题")
        
        # 内容相关性
        if relevance_score >= 90:
            reasons.append("完美匹配（核心内容）")
        elif relevance_score >= 70:
            reasons.append("高度相关（扩展内容）")
        elif relevance_score >= 50:
            reasons.append("相关（跨界尝试）")
        
        # 表现潜力
        if performance_score >= 80:
            reasons.append("预计表现优异")
        elif performance_score >= 60:
            reasons.append("预计表现良好")
        
        # Sources
        sources = trend.get('sources', [])
        if len(sources) > 2:
            reasons.append(f"在{len(sources)}个平台同时热门")
        
        # Growth
        growth = trend.get('growth_rate', 0)
        if growth > 100:
            reasons.append(f"搜索量增长{growth:.0f}%，趋势强劲")
        
        return "；".join(reasons)
    
    def _generate_content_angle(
        self,
        keyword: str,
        content_style: Dict,
        trend: Dict
    ) -> str:
        """
        Suggest a specific content angle for the trending topic
        """
        primary_style = content_style.get('primary_style', 'general')
        growth_rate = trend.get('growth_rate', 0)
        
        angles = {
            'tutorial': f"制作 '{keyword}' 完整教程，分步讲解",
            'review': f"深度评测 '{keyword}'，对比分析优劣",
            'entertainment': f"挑战/趣味视频：'{keyword}' 爆笑合集",
            'news': f"'{keyword}' 最新资讯和深度解读",
            'educational': f"科普 '{keyword}'：原理、历史和应用",
            'gaming': f"'{keyword}' 游戏实况和攻略指南",
            'tech': f"'{keyword}' 技术分析和使用体验"
        }
        
        base_angle = angles.get(primary_style, f"从独特角度解读 '{keyword}'")
        
        # Add urgency if growing fast
        if growth_rate > 150:
            return f"🔥 热点！{base_angle}（建议48小时内发布）"
        elif growth_rate > 80:
            return f"⚡ {base_angle}（建议本周内发布）"
        else:
            return f"💡 {base_angle}"
    
    def _predict_performance(
        self,
        match_score: float,
        viral_potential: float,
        performance_score: float,
        relevance_score: float,
        high_performers: Dict
    ) -> Dict:
        """
        预测视频表现 - 优化后的多因素动态计算
        
        改进点：
        1. 使用中位数而非平均值（更稳健）
        2. 考虑频道增长趋势
        3. 更精细的热度系数计算
        4. 添加标题优化加成
        5. 考虑频道规模调整
        
        公式：
        预测播放 = 基准播放 × 热度系数 × 相关性系数 × 表现潜力系数 × 频道规模调整 × 标题优化加成
        """
        import random
        
        # 1. 获取频道历史播放基准（优先使用中位数，更稳健）
        # 中位数对异常值不敏感，更适合作为预测基准
        median_views = high_performers.get('median_views') if high_performers else None
        avg_views = high_performers.get('avg_views') if high_performers else None
        
        # 使用中位数和平均值的加权平均（中位数权重更高）
        if median_views and avg_views:
            base_views = int(median_views * 0.7 + avg_views * 0.3)
        elif median_views:
            base_views = int(median_views)
        elif avg_views:
            base_views = int(avg_views)
        else:
            base_views = 10000  # 默认值
        
        # 确保有有效的播放量数据
        if base_views <= 0:
            base_views = 10000
        
        # 2. 频道规模调整（大频道波动更小，小频道潜力更大）
        total_videos = high_performers.get('total_videos', 0) if high_performers else 0
        if total_videos > 100:
            # 成熟频道，波动较小
            channel_stability = 0.95
        elif total_videos > 50:
            channel_stability = 1.0
        else:
            # 新频道，潜力更大但波动也大
            channel_stability = 1.1
        
        # 3. 优化后的热度增长系数（更平滑的曲线）
        # 使用连续函数而非分段函数，减少突变
        if viral_potential >= 90:
            viral_multiplier = 2.2 + (viral_potential - 90) * 0.03  # 2.2-2.5
        elif viral_potential >= 70:
            viral_multiplier = 1.6 + (viral_potential - 70) * 0.03  # 1.6-2.2
        elif viral_potential >= 50:
            viral_multiplier = 1.2 + (viral_potential - 50) * 0.02  # 1.2-1.6
        else:
            viral_multiplier = 0.9 + (viral_potential / 50) * 0.3  # 0.9-1.2
        
        # 限制范围，避免极端值
        viral_multiplier = max(0.7, min(3.0, viral_multiplier))
        
        # 4. 相关性调整（使用更保守的范围）
        # 相关性低时惩罚更大，相关性高时奖励更合理
        if relevance_score >= 80:
            relevance_multiplier = 1.0 + (relevance_score - 80) * 0.01  # 1.0-1.2
        elif relevance_score >= 60:
            relevance_multiplier = 0.85 + (relevance_score - 60) * 0.0075  # 0.85-1.0
        elif relevance_score >= 40:
            relevance_multiplier = 0.75 + (relevance_score - 40) * 0.005  # 0.75-0.85
        else:
            relevance_multiplier = 0.65 + (relevance_score / 40) * 0.1  # 0.65-0.75
        
        # 5. 表现潜力系数（更精细的计算）
        if performance_score >= 80:
            performance_multiplier = 1.2 + (performance_score - 80) * 0.015  # 1.2-1.5
        elif performance_score >= 60:
            performance_multiplier = 1.0 + (performance_score - 60) * 0.01  # 1.0-1.2
        elif performance_score >= 40:
            performance_multiplier = 0.85 + (performance_score - 40) * 0.0075  # 0.85-1.0
        else:
            performance_multiplier = 0.7 + (performance_score / 40) * 0.15  # 0.7-0.85
        
        # 6. 匹配度加成（时效性）
        timeliness_multiplier = 0.9 + (match_score / 100) * 0.25  # 0.9-1.15
        
        # 7. 标题优化加成（假设标题已优化）
        # 基于频道历史最佳标题长度
        avg_title_length = high_performers.get('avg_title_length', 50) if high_performers else 50
        if 30 <= avg_title_length <= 60:
            title_optimization = 1.05  # 标题长度适中，有5%加成
        else:
            title_optimization = 0.98  # 标题长度不理想，轻微惩罚
        
        # 8. 综合计算（移除随机波动，使用确定性计算）
        # 随机波动会导致预测不稳定，改用基于match_score的确定性调整
        confidence_factor = 0.9 + (match_score / 100) * 0.2  # 0.9-1.1
        
        predicted_views = int(
            base_views * 
            viral_multiplier * 
            relevance_multiplier * 
            performance_multiplier * 
            timeliness_multiplier * 
            channel_stability *
            title_optimization *
            confidence_factor
        )
        
        # 确保最小值，但不要设置过高
        predicted_views = max(500, predicted_views)
        
        # 9. 性能等级（基于综合分数）
        composite_score = (match_score * 0.4 + viral_potential * 0.3 + performance_score * 0.3)
        if composite_score >= 80:
            tier = 'excellent'
            description = "预计表现优异，可能成为爆款"
        elif composite_score >= 65:
            tier = 'good'
            description = "预计表现良好，高于平均水平"
        elif composite_score >= 50:
            tier = 'moderate'
            description = "预计表现中等，稳定流量"
        else:
            tier = 'low'
            description = "预计表现一般，可作为尝试"
        
        return {
            'tier': tier,
            'predicted_views': predicted_views,
            'description': description,
            'confidence': round(composite_score, 0)
        }
    
    def _suggest_format(self, keyword: str, content_style: Dict) -> str:
        """
        Suggest video format based on keyword and channel style
        """
        primary_style = content_style.get('primary_style', 'general')
        
        formats = {
            'tutorial': '8-12分钟教程，分步演示',
            'review': '10-15分钟深度评测',
            'entertainment': '5-8分钟快节奏娱乐',
            'news': '6-10分钟资讯解读',
            'educational': '10-15分钟知识科普',
            'gaming': '15-20分钟游戏实况',
            'tech': '8-12分钟产品体验'
        }
        
        return formats.get(primary_style, '8-12分钟综合内容')
    
    def _determine_urgency(self, trend: Dict, viral_potential: float) -> str:
        """
        确定紧急度 - 基于新的权重和热度分数
        """
        growth_rate = trend.get('growth_rate', 0)
        
        # 基于互联网热度和增长率判断
        if viral_potential >= 90 or growth_rate > 200:
            return 'urgent'  # 48小时内
        elif viral_potential >= 70 or growth_rate > 100:
            return 'high'    # 本周内
        elif viral_potential >= 50 or growth_rate > 50:
            return 'medium'  # 两周内
        else:
            return 'low'     # 灵活安排


class TitleGenerationEngine:
    """
    Generate optimized titles for recommended topics
    """
    
    def __init__(self):
        pass
    
    def generate_titles(
        self,
        recommendation: Dict,
        channel_analysis: Dict,
        count: int = 3
    ) -> List[Dict]:
        """
        Generate multiple title variants for a recommendation
        
        Args:
            recommendation: Topic recommendation with metadata
            channel_analysis: Channel characteristics
            count: Number of title variants to generate
        
        Returns:
            List of title variants with CTR predictions
        """
        keyword = recommendation['keyword']
        content_angle = recommendation['content_angle']
        high_performers = channel_analysis.get('high_performers', {})
        
        # Extract successful patterns from high-performing videos
        common_topics = high_performers.get('common_topics', [])
        avg_title_length = high_performers.get('avg_title_length', 60)
        
        # Generate different title strategies
        titles = []
        
        # Strategy 1: Number/List format (high CTR)
        titles.append({
            'title': self._generate_number_title(keyword),
            'strategy': 'number_list',
            'predicted_ctr': 8.5,
            'reasoning': '数字列表式标题，通常有较高点击率'
        })
        
        # Strategy 2: Question format (engagement)
        titles.append({
            'title': self._generate_question_title(keyword),
            'strategy': 'question',
            'predicted_ctr': 7.2,
            'reasoning': '问题式标题，激发好奇心'
        })
        
        # Strategy 3: Emotional hook (viral potential)
        titles.append({
            'title': self._generate_emotional_title(keyword, recommendation),
            'strategy': 'emotional',
            'predicted_ctr': 9.1,
            'reasoning': '情感化标题，易引发共鸣和分享'
        })
        
        # Optionally generate more variants
        if count > 3:
            titles.append({
                'title': self._generate_authority_title(keyword),
                'strategy': 'authority',
                'predicted_ctr': 7.8,
                'reasoning': '权威式标题，适合专业内容'
            })
        
        # Adjust title length based on channel's successful pattern
        for title_data in titles:
            title_data['title'] = self._adjust_title_length(
                title_data['title'],
                avg_title_length
            )
            title_data['character_count'] = len(title_data['title'])
        
        return titles[:count]
    
    def _generate_number_title(self, keyword: str) -> str:
        """Generate title with numbers (e.g., "5 Ways to...")"""
        numbers = [3, 5, 7, 10]
        import random
        num = random.choice(numbers)
        
        templates = [
            f"{num}个关于{keyword}的必知技巧",
            f"{keyword}完整指南：{num}个关键点",
            f"{num}种方法玩转{keyword}",
            f"Top {num}：{keyword}最佳实践"
        ]
        
        return random.choice(templates)
    
    def _generate_question_title(self, keyword: str) -> str:
        """Generate question-format title"""
        templates = [
            f"{keyword}真的值得吗？完整分析",
            f"如何选择最适合的{keyword}？",
            f"{keyword}为什么这么火？深度解读",
            f"你真的了解{keyword}吗？"
        ]
        
        import random
        return random.choice(templates)
    
    def _generate_emotional_title(self, keyword: str, recommendation: Dict) -> str:
        """Generate title with emotional hooks"""
        urgency = recommendation.get('urgency', 'low')
        
        if urgency == 'urgent':
            prefix = "🔥 爆火！"
        elif urgency == 'high':
            prefix = "⚡ 超火！"
        else:
            prefix = ""
        
        templates = [
            f"{prefix}{keyword}：99%的人都不知道的秘密",
            f"{prefix}震惊！{keyword}竟然这样用",
            f"{prefix}{keyword}完全指南：从入门到精通",
            f"{prefix}别再错过！{keyword}全面解析"
        ]
        
        import random
        return random.choice(templates)
    
    def _generate_authority_title(self, keyword: str) -> str:
        """Generate authoritative/professional title"""
        templates = [
            f"{keyword}深度评测：专业视角",
            f"{keyword}完整分析报告",
            f"专业解读：{keyword}终极指南",
            f"{keyword}权威测评与推荐"
        ]
        
        import random
        return random.choice(templates)
    
    def _adjust_title_length(self, title: str, target_length: int) -> str:
        """
        Adjust title to optimal length based on channel's successful pattern
        """
        current_length = len(title)
        
        # If title is too long, trim it
        if current_length > target_length + 10:
            # Try to cut at a natural break point
            title = title[:int(target_length)] + '...'
        
        # YouTube optimal length is 50-70 characters
        if len(title) > 70:
            title = title[:67] + '...'
        
        return title


# Initialize engines
recommendation_engine = TopicRecommendationEngine()
title_engine = TitleGenerationEngine()
