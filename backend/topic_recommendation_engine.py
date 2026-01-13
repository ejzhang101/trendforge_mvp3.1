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
        
        # Sort by match score
        recommendations.sort(key=lambda x: x['match_score'], reverse=True)
        
        return recommendations[:max_recommendations]
    
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
        
        Returns a dict with match_score and detailed reasoning
        """
        keyword = trend['keyword'].lower()
        
        # 1. Topic Relevance (40%)
        relevance_score = self._calculate_topic_relevance(keyword, channel_topics)
        
        # 2. Style Compatibility (20%)
        style_score = self._calculate_style_compatibility(keyword, content_style)
        
        # 3. Audience Fit (20%)
        audience_score = self._calculate_audience_fit(keyword, target_audience)
        
        # 4. Opportunity Score (20%) - Based on social engagement and growth
        opportunity_score = self._calculate_opportunity_score(trend)
        
        # Composite match score
        match_score = (
            relevance_score * 0.4 +
            style_score * 0.2 +
            audience_score * 0.2 +
            opportunity_score * 0.2
        )
        
        # Generate reasoning
        reasoning = self._generate_reasoning(
            keyword,
            relevance_score,
            style_score,
            audience_score,
            opportunity_score,
            trend
        )
        
        # Generate content angle
        content_angle = self._generate_content_angle(
            keyword,
            content_style,
            trend
        )
        
        # Predict performance
        predicted_performance = self._predict_performance(
            match_score,
            opportunity_score,
            high_performers
        )
        
        # Suggest format
        suggested_format = self._suggest_format(keyword, content_style)
        
        # Determine urgency
        urgency = self._determine_urgency(trend)
        
        return {
            'match_score': round(match_score, 2),
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
    
    def _calculate_opportunity_score(self, trend: Dict) -> float:
        """
        Calculate opportunity score based on social media engagement
        """
        composite_score = trend.get('composite_score', 0)
        growth_rate = trend.get('growth_rate', 0)
        source_count = len(trend.get('sources', []))
        
        # Weighted calculation
        score = (
            composite_score * 0.6 +  # Social engagement
            min(100, growth_rate) * 0.3 +  # Growth potential
            (source_count * 10) * 0.1  # Cross-platform presence
        )
        
        return min(100, score)
    
    def _generate_reasoning(
        self,
        keyword: str,
        relevance: float,
        style: float,
        audience: float,
        opportunity: float,
        trend: Dict
    ) -> str:
        """
        Generate human-readable reasoning for the recommendation
        """
        reasons = []
        
        # Relevance
        if relevance > 70:
            reasons.append(f"'{keyword}' 高度匹配您的频道核心主题")
        elif relevance > 50:
            reasons.append(f"'{keyword}' 与您的内容方向相关")
        else:
            reasons.append(f"'{keyword}' 可以帮助您拓展新的内容领域")
        
        # Opportunity
        if opportunity > 80:
            reasons.append("当前社交媒体讨论热度极高")
        elif opportunity > 60:
            reasons.append("话题热度持续上升")
        
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
        opportunity_score: float,
        high_performers: Dict
    ) -> Dict:
        """
        Predict video performance based on match and opportunity scores
        """
        # Base prediction on scores
        base_performance = (match_score + opportunity_score) / 2
        
        # Adjust based on channel's historical performance
        avg_views = high_performers.get('avg_views', 10000) if high_performers else 10000
        
        # Performance tiers
        if base_performance > 80:
            tier = 'excellent'
            view_multiplier = 2.0
            description = "预计表现优异，可能成为爆款"
        elif base_performance > 65:
            tier = 'good'
            view_multiplier = 1.5
            description = "预计表现良好，高于平均水平"
        elif base_performance > 50:
            tier = 'moderate'
            view_multiplier = 1.2
            description = "预计表现中等，稳定流量"
        else:
            tier = 'low'
            view_multiplier = 0.8
            description = "预计表现一般，可作为尝试"
        
        predicted_views = int(avg_views * view_multiplier)
        
        return {
            'tier': tier,
            'predicted_views': predicted_views,
            'description': description,
            'confidence': round(base_performance, 0)
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
    
    def _determine_urgency(self, trend: Dict) -> str:
        """
        Determine how urgent it is to create content on this topic
        """
        growth_rate = trend.get('growth_rate', 0)
        composite_score = trend.get('composite_score', 0)
        
        if growth_rate > 200 or composite_score > 90:
            return 'urgent'  # 48小时内
        elif growth_rate > 100 or composite_score > 75:
            return 'high'    # 本周内
        elif growth_rate > 50 or composite_score > 60:
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
