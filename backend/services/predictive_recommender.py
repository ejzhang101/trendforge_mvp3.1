"""
Enhanced Intelligent Topic Recommendation Engine with Prophet Predictions
MVP 3.0 - Predictive recommendations with time series forecasting
"""

from typing import List, Dict, Optional
import numpy as np
from datetime import datetime

# Import Prophet predictor
try:
    from services.trend_predictor import trend_predictor
    PROPHET_AVAILABLE = True
except ImportError:
    PROPHET_AVAILABLE = False
    print("⚠️ Prophet predictor not available")


class PredictiveRecommendationEngine:
    """
    Enhanced recommendation engine with Prophet-powered predictions
    
    New features:
    - Future trend predictions (7-day forecast)
    - Confidence-based ranking
    - Peak timing detection
    - Emerging trend identification
    """
    
    def __init__(self):
        self.min_match_score = 30
        self.prophet = trend_predictor if PROPHET_AVAILABLE else None
    
    def generate_recommendations(
        self,
        channel_analysis: Dict,
        social_trends: List[Dict],
        max_recommendations: int = 10,
        enable_predictions: bool = True
    ) -> List[Dict]:
        """
        Generate intelligent recommendations with predictive insights
        
        Args:
            channel_analysis: Channel characteristics
            social_trends: Current trending topics
            max_recommendations: Max number to return
            enable_predictions: Whether to include Prophet predictions
        
        Returns:
            List of recommendations with predictions
        """
        recommendations = []
        
        # Extract channel characteristics
        channel_topics = [t['topic'] for t in channel_analysis.get('topics', [])]
        content_style = channel_analysis.get('content_style', {})
        target_audience = channel_analysis.get('target_audience', {})
        high_performers = channel_analysis.get('high_performers', {})
        
        # Generate base recommendations
        for trend in social_trends:
            match_result = self._calculate_match_score(
                trend,
                channel_topics,
                content_style,
                target_audience,
                high_performers
            )
            
            if match_result['match_score'] >= self.min_match_score:
                rec = {
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
                }
                
                recommendations.append(rec)
        
        # Add Prophet predictions if enabled
        if enable_predictions and self.prophet and recommendations:
            print("🔮 Generating Prophet predictions...")
            recommendations = self._enhance_with_predictions(
                recommendations, 
                channel_analysis
            )
        
        # Sort by composite score (match + prediction)
        recommendations.sort(
            key=lambda x: x.get('final_score', x['match_score']), 
            reverse=True
        )
        
        return recommendations[:max_recommendations]
    
    def _enhance_with_predictions(
        self, 
        recommendations: List[Dict],
        channel_analysis: Dict
    ) -> List[Dict]:
        """
        Enhance recommendations with Prophet predictions
        """
        keywords = [r['keyword'] for r in recommendations]
        
        # Get predictions for all keywords
        try:
            predictions = self.prophet.batch_predict(keywords, forecast_days=7)
        except Exception as e:
            print(f"⚠️ Prophet prediction failed: {e}")
            predictions = []
        
        # Create prediction lookup
        pred_map = {p['keyword']: p for p in predictions}
        
        # Enhance each recommendation
        for rec in recommendations:
            keyword = rec['keyword']
            
            if keyword in pred_map:
                pred = pred_map[keyword]
                
                # Add prediction data
                rec['prediction'] = {
                    'trend_direction': pred['trend_direction'],
                    'trend_strength': pred['trend_strength'],
                    'confidence': pred['confidence'],
                    'peak_day': pred.get('peak_day'),
                    'peak_score': pred.get('peak_score'),
                    'summary': pred['summary'],
                    'predictions': pred['predictions'][:7] if 'predictions' in pred else []  # 7-day forecast
                }
                
                # Calculate final score (blend current + predicted)
                rec['final_score'] = self._calculate_final_score(rec, pred)
                
                # Update urgency based on prediction
                rec['urgency'] = self._update_urgency_with_prediction(
                    rec['urgency'], 
                    pred
                )
                
                # Enhance reasoning
                rec['reasoning'] = self._enhance_reasoning_with_prediction(
                    rec['reasoning'], 
                    pred
                )
            else:
                # No prediction available
                rec['prediction'] = None
                rec['final_score'] = rec['match_score']
        
        return recommendations
    
    def _calculate_final_score(self, recommendation: Dict, prediction: Dict) -> float:
        """
        Calculate final recommendation score combining current state and predictions
        
        Formula:
        final_score = current_match * 60% + predictive_score * 40%
        """
        current_score = recommendation['match_score']
        
        # Predictive score based on confidence and direction
        trend_multiplier = {
            'rising': 1.2,
            'stable': 1.0,
            'falling': 0.7
        }
        
        direction = prediction['trend_direction']
        multiplier = trend_multiplier.get(direction, 1.0)
        
        predictive_score = (
            prediction['confidence'] * 
            prediction['trend_strength'] / 100 * 
            multiplier
        )
        
        # Blend scores
        final_score = current_score * 0.6 + predictive_score * 0.4
        
        return round(final_score, 2)
    
    def _update_urgency_with_prediction(self, current_urgency: str, 
                                       prediction: Dict) -> str:
        """
        Update urgency level based on prediction
        
        Rules:
        - Rising trend + high confidence + near peak = urgent
        - Rising trend + high confidence = high
        - Rising trend = medium
        - Stable/falling = keep current or downgrade
        """
        direction = prediction['trend_direction']
        confidence = prediction['confidence']
        peak_day = prediction.get('peak_day')
        
        if direction == 'rising':
            if confidence > 80 and peak_day and peak_day <= 3:
                return 'urgent'  # Peak in 3 days!
            elif confidence > 70:
                return 'high'
            else:
                return 'medium'
        elif direction == 'stable':
            return current_urgency  # Keep current
        else:  # falling
            # Downgrade urgency
            urgency_levels = ['urgent', 'high', 'medium', 'low']
            current_idx = urgency_levels.index(current_urgency) if current_urgency in urgency_levels else 2
            return urgency_levels[min(len(urgency_levels) - 1, current_idx + 1)]
    
    def _enhance_reasoning_with_prediction(self, current_reasoning: str, 
                                          prediction: Dict) -> str:
        """
        Add prediction insights to reasoning
        """
        direction = prediction['trend_direction']
        confidence = prediction['confidence']
        peak_day = prediction.get('peak_day')
        
        # Add prediction insight
        if direction == 'rising' and confidence > 70:
            insight = f"🔮 预测：未来7天热度持续上升（置信度{confidence:.0f}%）"
            if peak_day:
                insight += f"，预计第{peak_day}天达到峰值"
        elif direction == 'falling':
            insight = f"⚠️ 预测：热度正在下降（置信度{confidence:.0f}%）"
        else:
            insight = f"📊 预测：热度保持稳定（置信度{confidence:.0f}%）"
        
        return f"{current_reasoning}；{insight}"
    
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
        
        Algorithm:
        - 互联网热度 (Viral Potential): 40%
        - 表现潜力 (Performance Score): 25%
        - 内容相关性 (Relevance Score): 35%
        """
        keyword = trend['keyword'].lower()
        
        # 1. 互联网热度 (Viral Potential)
        viral_potential = self._calculate_viral_potential(trend)
        
        # 2. 表现潜力 (Performance Score)
        performance_score = self._calculate_performance_potential(
            trend, 
            high_performers,
            channel_topics,
            content_style,
            target_audience
        )
        
        # 3. 内容相关性 (Relevance Score)
        topic_relevance = self._calculate_topic_relevance(keyword, channel_topics)
        style_score = self._calculate_style_compatibility(keyword, content_style)
        audience_score = self._calculate_audience_fit(keyword, target_audience)
        relevance_score = (topic_relevance * 0.5 + style_score * 0.3 + audience_score * 0.2)
        
        # 4. Opportunity Score
        opportunity_score = self._calculate_opportunity_score(trend)
        
        # Composite match score
        match_score = (
            viral_potential * 0.4 +
            performance_score * 0.25 +
            relevance_score * 0.35
        )
        
        # Generate reasoning
        reasoning = self._generate_reasoning(
            keyword,
            viral_potential,
            performance_score,
            relevance_score,
            trend
        )
        
        # Generate content angle
        content_angle = self._generate_content_angle(keyword, content_style, trend)
        
        # Predict performance
        predicted_performance = self._predict_performance(
            match_score,
            viral_potential,
            performance_score,
            relevance_score,
            high_performers
        )
        
        # Suggest format
        suggested_format = self._suggest_format(keyword, content_style)
        
        # Determine urgency
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
    
    def _calculate_viral_potential(self, trend: Dict) -> float:
        """互联网热度计算"""
        composite_score = trend.get('composite_score', 0)
        growth_rate = trend.get('growth_rate', 0)
        source_count = len(trend.get('sources', []))
        
        base_score = composite_score
        growth_bonus = min(30, growth_rate * 0.3)
        platform_bonus = min(20, (source_count - 1) * 10)
        
        viral_score = base_score + growth_bonus + platform_bonus
        return min(100, round(viral_score, 2))
    
    def _calculate_performance_potential(self, trend, high_performers, 
                                        channel_topics, content_style, 
                                        target_audience) -> float:
        """表现潜力计算"""
        viral_potential = self._calculate_viral_potential(trend)
        
        keyword = trend['keyword'].lower()
        topic_relevance = self._calculate_topic_relevance(keyword, channel_topics)
        style_score = self._calculate_style_compatibility(keyword, content_style)
        audience_score = self._calculate_audience_fit(keyword, target_audience)
        relevance_bonus = (topic_relevance * 0.5 + style_score * 0.3 + audience_score * 0.2) * 0.3
        
        growth_rate = trend.get('growth_rate', 0)
        timeliness_bonus = min(20, growth_rate * 0.2)
        
        performance_score = viral_potential * 0.6 + relevance_bonus + timeliness_bonus
        return min(100, round(performance_score, 2))
    
    def _calculate_opportunity_score(self, trend: Dict) -> float:
        """机会分数"""
        return self._calculate_viral_potential(trend)
    
    def _calculate_topic_relevance(self, keyword: str, channel_topics: List[str]) -> float:
        """主题相关性"""
        if not channel_topics:
            return 50
        
        keyword_words = set(keyword.split())
        exact_matches = sum(1 for topic in channel_topics if topic in keyword)
        word_overlaps = sum(
            len(keyword_words & set(topic.split())) 
            for topic in channel_topics
        )
        
        relevance = (exact_matches * 20) + (word_overlaps * 10)
        return min(100, max(20, relevance))
    
    def _calculate_style_compatibility(self, keyword: str, content_style: Dict) -> float:
        """风格兼容性"""
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
        
        matches = sum(1 for kw in style_keywords_set if kw in keyword_lower)
        compatibility = 50 + (matches * 15)
        return min(100, compatibility)
    
    def _calculate_audience_fit(self, keyword: str, target_audience: Dict) -> float:
        """受众适配性"""
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
    
    def _generate_reasoning(self, keyword, viral, performance, relevance, trend) -> str:
        """生成推理说明"""
        reasons = []
        
        if viral >= 90:
            reasons.append("🔥 爆火话题（全网讨论）")
        elif viral >= 70:
            reasons.append("⚡ 热门话题（快速上升）")
        
        if relevance >= 90:
            reasons.append("完美匹配（核心内容）")
        elif relevance >= 70:
            reasons.append("高度相关（扩展内容）")
        
        if performance >= 80:
            reasons.append("预计表现优异")
        
        sources = trend.get('sources', [])
        if len(sources) > 2:
            reasons.append(f"在{len(sources)}个平台同时热门")
        
        return "；".join(reasons) if reasons else f"'{keyword}' 值得关注"
    
    def _generate_content_angle(self, keyword, content_style, trend) -> str:
        """内容角度建议"""
        primary_style = content_style.get('primary_style', 'general')
        growth_rate = trend.get('growth_rate', 0)
        
        base_angle = f"制作 '{keyword}' 主题内容"
        
        if growth_rate > 150:
            return f"🔥 热点！{base_angle}（建议48小时内发布）"
        elif growth_rate > 80:
            return f"⚡ {base_angle}（建议本周内发布）"
        else:
            return f"💡 {base_angle}"
    
    def _predict_performance(self, match_score, viral, performance, 
                            relevance, high_performers) -> Dict:
        """
        性能预测 - 优化算法，避免数据失真
        
        使用多因素动态计算，确保预测值合理
        """
        # 获取基准播放量
        if high_performers:
            median_views = high_performers.get('median_views', 0) or high_performers.get('median_views', 10000)
            avg_views = high_performers.get('avg_views', 0) or high_performers.get('avg_views', 10000)
        else:
            median_views = 10000
            avg_views = 10000
        
        # 使用加权平均作为基准（中位数70% + 平均值30%）
        base_views = median_views * 0.7 + avg_views * 0.3
        
        # 确保基准值合理（至少1000，最多1000万）
        base_views = max(1000, min(10000000, base_views))
        
        # 多因素系数计算
        # 1. 热度系数（基于互联网热度）
        viral_multiplier = 1.0
        if viral >= 90:
            viral_multiplier = 2.5  # 爆火话题
        elif viral >= 70:
            viral_multiplier = 2.0  # 热门话题
        elif viral >= 50:
            viral_multiplier = 1.5  # 上升话题
        else:
            viral_multiplier = 1.0  # 正常
        
        # 2. 相关性系数（基于内容相关性）
        relevance_multiplier = 0.7 + (relevance / 100) * 0.6  # 0.7-1.3
        
        # 3. 表现潜力系数（基于表现潜力）
        performance_multiplier = 0.8 + (performance / 100) * 0.7  # 0.8-1.5
        
        # 4. 时效性系数（基于匹配分数）
        timeliness_multiplier = 0.9 + (match_score / 100) * 0.3  # 0.9-1.2
        
        # 5. 频道稳定性系数（基于历史表现）
        channel_stability = 1.0
        if high_performers and high_performers.get('std_views'):
            std_views = high_performers.get('std_views', 0)
            if std_views > 0 and avg_views > 0:
                cv = std_views / avg_views  # 变异系数
                # 稳定性越高，系数越高（0.95-1.1）
                channel_stability = 0.95 + min(0.15, (1 - min(1, cv)) * 0.15)
        
        # 6. 标题优化系数（小幅提升）
        title_optimization = 0.98 + (match_score / 100) * 0.07  # 0.98-1.05
        
        # 7. 置信度因子（基于预测置信度，如果有）
        confidence_factor = 0.8 + (match_score / 100) * 0.3  # 0.8-1.1
        
        # 综合计算预测播放量
        predicted_views = base_views * viral_multiplier * relevance_multiplier * \
                         performance_multiplier * timeliness_multiplier * \
                         channel_stability * title_optimization * confidence_factor
        
        # 确保预测值在合理范围内（1000 - 5000万）
        predicted_views = max(1000, min(50000000, int(predicted_views)))
        
        # 确定表现等级
        if match_score >= 80:
            tier = 'excellent'
            description = "预计表现优异，可能成为爆款"
        elif match_score >= 65:
            tier = 'good'
            description = "预计表现良好，高于平均水平"
        elif match_score >= 50:
            tier = 'moderate'
            description = "预计表现中等，稳定流量"
        else:
            tier = 'low'
            description = "预计表现一般，可作为尝试"
        
        return {
            'tier': tier,
            'predicted_views': predicted_views,
            'description': description,
            'confidence': round(match_score, 0)
        }
    
    def _suggest_format(self, keyword, content_style) -> str:
        """格式建议"""
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
    
    def _determine_urgency(self, trend, viral_potential) -> str:
        """紧急程度"""
        growth_rate = trend.get('growth_rate', 0)
        
        if viral_potential >= 90 or growth_rate > 200:
            return 'urgent'
        elif viral_potential >= 70 or growth_rate > 100:
            return 'high'
        elif viral_potential >= 50 or growth_rate > 50:
            return 'medium'
        else:
            return 'low'


# Keep original TitleGenerationEngine unchanged
class TitleGenerationEngine:
    """Title generation engine (unchanged from original)"""
    
    def __init__(self):
        pass
    
    def generate_titles(self, recommendation: Dict, channel_analysis: Dict, 
                       count: int = 3) -> List[Dict]:
        """Generate title variants"""
        import random
        
        keyword = recommendation['keyword']
        urgency = recommendation.get('urgency', 'low')
        
        titles = []
        
        # Number list format
        num = random.choice([3, 5, 7, 10])
        titles.append({
            'title': f"🔥 爆火！{num}个关于{keyword}的必知技巧",
            'strategy': 'number_list',
            'predicted_ctr': 8.5,
            'reasoning': '数字列表式标题，通常有较高点击率',
            'character_count': len(f"🔥 爆火！{num}个关于{keyword}的必知技巧")
        })
        
        # Question format
        titles.append({
            'title': f"{keyword}真的值得吗？完整分析",
            'strategy': 'question',
            'predicted_ctr': 7.2,
            'reasoning': '问题式标题，激发好奇心',
            'character_count': len(f"{keyword}真的值得吗？完整分析")
        })
        
        # Emotional format
        if urgency == 'urgent':
            prefix = "🔥 爆火！"
        elif urgency == 'high':
            prefix = "⚡ 超火！"
        else:
            prefix = ""
        
        titles.append({
            'title': f"{prefix}{keyword}：99%的人都不知道的秘密",
            'strategy': 'emotional',
            'predicted_ctr': 9.1,
            'reasoning': '情感化标题，易引发共鸣和分享',
            'character_count': len(f"{prefix}{keyword}：99%的人都不知道的秘密")
        })
        
        return titles[:count]


# Initialize engines
predictive_recommendation_engine = PredictiveRecommendationEngine()
title_engine = TitleGenerationEngine()
