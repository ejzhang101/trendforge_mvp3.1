"""
ML-based Performance Predictor with XGBoost
优雅降级：无训练数据时使用规则方法，不影响现有功能
"""

import numpy as np
import re
from typing import Dict, Optional
import json
import os
from datetime import datetime

# 尝试导入 ML 库，失败则使用规则方法
try:
    import xgboost as xgb
    from sklearn.preprocessing import StandardScaler
    XGBOOST_AVAILABLE = True
except ImportError:
    XGBOOST_AVAILABLE = False
    print("⚠️  XGBoost not available, using rule-based prediction")


class MLPerformancePredictor:
    """
    基于 XGBoost 的播放量预测器
    
    特性：
    - 自动降级到规则方法（如果 XGBoost 不可用）
    - 特征工程（13 个核心特征）
    - 置信度评估
    """
    
    def __init__(self, model_path: Optional[str] = None):
        self.model = None
        self.scaler = StandardScaler() if XGBOOST_AVAILABLE else None
        self.is_trained = False
        self.use_ml = XGBOOST_AVAILABLE
        
        # 特征名称（用于可解释性）
        self.feature_names = [
            'title_length', 'title_has_numbers', 'title_has_emoji',
            'title_emotional_words', 'desc_length', 'tag_count',
            'log_subscribers', 'log_channel_avg_views', 'channel_engagement',
            'trend_score', 'trend_growth', 'multi_platform', 'relevance_score'
        ]
        
        # 尝试加载预训练模型
        if model_path and os.path.exists(model_path):
            self._load_model(model_path)
    
    def predict_performance(
        self,
        keyword: str,
        channel_analysis: Dict,
        trend: Dict,
        relevance_score: float = 0.0
    ) -> Dict:
        """
        预测视频表现
        
        Args:
            keyword: 推荐的关键词/主题
            channel_analysis: 频道分析数据
            trend: 社交趋势数据
            relevance_score: 相关性分数（0-100）
        
        Returns:
            {
                'predicted_views': int,
                'confidence': float,
                'tier': str,
                'method': str,
                'feature_importance': dict (如果使用 ML)
            }
        """
        # 如果 ML 可用且已训练，使用 ML 预测
        if self.use_ml and self.is_trained:
            return self._ml_prediction(keyword, channel_analysis, trend, relevance_score)
        
        # 否则使用规则方法（与原代码逻辑一致）
        return self._rule_based_prediction(keyword, channel_analysis, trend, relevance_score)
    
    def _extract_features(
        self,
        keyword: str,
        channel_analysis: Dict,
        trend: Dict,
        relevance_score: float
    ) -> np.ndarray:
        """提取 13 个预测特征"""
        
        high_performers = channel_analysis.get('high_performers', {})
        target_audience = channel_analysis.get('target_audience', {})
        channel_data = channel_analysis.get('channel_data', {})
        
        # 1. 标题特征
        title_length = len(keyword)
        title_has_numbers = int(bool(re.search(r'\d', keyword)))
        title_has_emoji = int(bool(re.search(r'[\U0001F600-\U0001F64F\U0001F300-\U0001F5FF]', keyword)))
        
        # 情感词（根据学术研究，情感词提升点击率）
        emotional_words = ['amazing', 'shocking', 'incredible', 'best', 'worst', 
                          'ultimate', 'secret', 'proven', 'must', 'never']
        title_emotional = sum(1 for word in emotional_words if word.lower() in keyword.lower())
        
        # 2. 描述特征（使用关键词长度作为代理）
        desc_length = len(keyword) * 10  # 估算
        
        # 3. 标签特征
        tag_count = len(keyword.split())  # 估算标签数量
        
        # 4. 频道特征
        subscriber_count = channel_data.get('subscriberCount', 1000) if isinstance(channel_data, dict) else 1000
        log_subscribers = np.log1p(subscriber_count)
        
        channel_avg_views = high_performers.get('median_views', 10000)
        log_channel_avg_views = np.log1p(channel_avg_views)
        
        # 计算频道互动率
        engagement_rate_str = target_audience.get('engagement_rate', '0.5%') if isinstance(target_audience, dict) else '0.5%'
        channel_engagement = float(engagement_rate_str.replace('%', '')) / 100 if '%' in str(engagement_rate_str) else 0.005
        
        # 5. 趋势特征
        trend_score = trend.get('composite_score', 0)
        trend_growth = trend.get('growth_rate', 0)
        multi_platform = len(trend.get('sources', []))
        
        # 6. 相关性特征
        relevance = relevance_score / 100  # 归一化到 0-1
        
        # 组装特征向量
        features = np.array([
            title_length,
            title_has_numbers,
            title_has_emoji,
            title_emotional,
            desc_length,
            tag_count,
            log_subscribers,
            log_channel_avg_views,
            channel_engagement,
            trend_score,
            trend_growth,
            multi_platform,
            relevance
        ]).reshape(1, -1)
        
        return features
    
    def _ml_prediction(
        self,
        keyword: str,
        channel_analysis: Dict,
        trend: Dict,
        relevance_score: float
    ) -> Dict:
        """使用 XGBoost 进行预测"""
        
        # 提取特征
        features = self._extract_features(keyword, channel_analysis, trend, relevance_score)
        
        # 标准化
        features_scaled = self.scaler.transform(features)
        
        # 预测（log-transformed views）
        log_predicted_views = self.model.predict(features_scaled)[0]
        predicted_views = int(np.expm1(log_predicted_views))  # 反 log 转换
        
        # 计算置信度（基于特征范围）
        confidence = self._calculate_confidence(features_scaled)
        
        # 分类等级
        tier = self._classify_tier(predicted_views, channel_analysis)
        
        # 特征重要性（用于可解释性）
        feature_importance = self._get_feature_importance(features)
        
        return {
            'predicted_views': max(100, predicted_views),  # 最低 100 播放
            'confidence': confidence,
            'tier': tier,
            'description': self._get_tier_description(tier),
            'method': 'xgboost_ml',
            'feature_importance': feature_importance
        }
    
    def _rule_based_prediction(
        self,
        keyword: str,
        channel_analysis: Dict,
        trend: Dict,
        relevance_score: float
    ) -> Dict:
        """
        基于规则的预测（与原 intelligent_recommender.py 逻辑一致）
        确保降级时结果不变
        """
        
        high_performers = channel_analysis.get('high_performers', {})
        
        # 1. 获取频道基准播放量（使用中位数，更稳定）
        median_views = high_performers.get('median_views', 10000)
        avg_views = high_performers.get('avg_views', 10000)
        
        # 加权平均（中位数权重更高）
        base_views = int(median_views * 0.7 + avg_views * 0.3) if median_views and avg_views else 10000
        base_views = max(500, base_views)  # 最低基准
        
        # 2. 计算热度倍数（病毒潜力）
        viral_potential = self._calculate_viral_potential(trend)
        
        if viral_potential >= 90:
            viral_multiplier = 2.2 + (viral_potential - 90) * 0.03
        elif viral_potential >= 70:
            viral_multiplier = 1.6 + (viral_potential - 70) * 0.03
        elif viral_potential >= 50:
            viral_multiplier = 1.2 + (viral_potential - 50) * 0.02
        else:
            viral_multiplier = 0.9 + (viral_potential / 50) * 0.3
        
        viral_multiplier = max(0.7, min(3.0, viral_multiplier))
        
        # 3. 相关性调整
        if relevance_score >= 80:
            relevance_multiplier = 1.0 + (relevance_score - 80) * 0.01
        elif relevance_score >= 60:
            relevance_multiplier = 0.85 + (relevance_score - 60) * 0.0075
        else:
            relevance_multiplier = 0.7 + (relevance_score / 60) * 0.15
        
        # 4. 频道规模调整
        total_videos = high_performers.get('total_videos', 50)
        if total_videos > 100:
            channel_stability = 0.95  # 成熟频道，波动小
        elif total_videos > 50:
            channel_stability = 1.0
        else:
            channel_stability = 1.1  # 新频道，潜力大
        
        # 5. 标题优化加成
        avg_title_length = high_performers.get('avg_title_length', 50)
        title_length = len(keyword)
        if 30 <= title_length <= 70 and 30 <= avg_title_length <= 60:
            title_optimization = 1.05
        else:
            title_optimization = 0.98
        
        # 6. 综合计算
        predicted_views = int(
            base_views * 
            viral_multiplier * 
            relevance_multiplier * 
            channel_stability *
            title_optimization
        )
        
        predicted_views = max(500, predicted_views)
        
        # 7. 分类等级
        tier = self._classify_tier(predicted_views, channel_analysis)
        
        # 8. 计算置信度（基于数据完整性）
        confidence = self._calculate_rule_confidence(channel_analysis, trend)
        
        return {
            'predicted_views': predicted_views,
            'confidence': confidence,
            'tier': tier,
            'description': self._get_tier_description(tier),
            'method': 'rule_based'
        }
    
    def _calculate_viral_potential(self, trend: Dict) -> float:
        """计算病毒潜力分数（与原逻辑一致）"""
        composite_score = trend.get('composite_score', 0)
        growth_rate = trend.get('growth_rate', 0)
        source_count = len(trend.get('sources', []))
        
        base_score = composite_score
        growth_bonus = min(30, growth_rate * 0.3)
        platform_bonus = min(20, (source_count - 1) * 10)
        
        viral_score = base_score + growth_bonus + platform_bonus
        return min(100, round(viral_score, 2))
    
    def _classify_tier(self, predicted_views: int, channel_analysis: Dict) -> str:
        """分类表现等级"""
        high_performers = channel_analysis.get('high_performers', {})
        median_views = high_performers.get('median_views', 10000)
        
        # 相对于频道中位数的表现
        if predicted_views >= median_views * 2:
            return 'excellent'
        elif predicted_views >= median_views * 1.3:
            return 'good'
        elif predicted_views >= median_views * 0.8:
            return 'moderate'
        else:
            return 'low'
    
    def _get_tier_description(self, tier: str) -> str:
        """获取等级描述"""
        descriptions = {
            'excellent': '预计表现优异，可能成为爆款',
            'good': '预计表现良好，高于平均水平',
            'moderate': '预计表现中等，稳定流量',
            'low': '预计表现一般，可作为尝试'
        }
        return descriptions.get(tier, '预计表现中等')
    
    def _calculate_confidence(self, features_scaled: np.ndarray) -> float:
        """计算 ML 预测的置信度"""
        # 简化版：基于特征是否在训练范围内
        # 实际应该使用模型的 prediction interval
        
        # 假设训练数据的特征范围在 [-3, 3]（标准化后）
        out_of_range = np.sum(np.abs(features_scaled) > 3)
        
        if out_of_range == 0:
            confidence = 0.9
        elif out_of_range <= 2:
            confidence = 0.75
        else:
            confidence = 0.6
        
        return round(confidence, 2)
    
    def _calculate_rule_confidence(self, channel_analysis: Dict, trend: Dict) -> float:
        """计算规则方法的置信度"""
        confidence = 0.6  # 基础置信度
        
        # 数据完整性加成
        high_performers = channel_analysis.get('high_performers', {})
        
        if high_performers.get('total_videos', 0) > 50:
            confidence += 0.1  # 频道数据充足
        
        if trend.get('sources', []):
            confidence += 0.05 * len(trend['sources'])  # 多平台验证
        
        if high_performers.get('median_views', 0) > 0:
            confidence += 0.1  # 有可靠基准
        
        return min(0.9, round(confidence, 2))
    
    def _get_feature_importance(self, features: np.ndarray) -> Dict:
        """获取特征重要性（仅在 ML 模式下）"""
        if not self.is_trained or not hasattr(self.model, 'feature_importances_'):
            return {}
        
        importance = self.model.feature_importances_
        
        # 返回 top 5 重要特征
        feature_scores = list(zip(self.feature_names, importance))
        feature_scores.sort(key=lambda x: x[1], reverse=True)
        
        return {
            name: round(float(score), 3) 
            for name, score in feature_scores[:5]
        }
    
    def _load_model(self, model_path: str):
        """加载预训练模型"""
        try:
            self.model = xgb.XGBRegressor()
            self.model.load_model(model_path)
            
            # 加载 scaler
            scaler_path = model_path.replace('.json', '_scaler.pkl')
            if os.path.exists(scaler_path):
                import pickle
                with open(scaler_path, 'rb') as f:
                    self.scaler = pickle.load(f)
            
            self.is_trained = True
            print(f"✅ ML model loaded from {model_path}")
        except Exception as e:
            print(f"⚠️  Failed to load ML model: {e}")
            self.is_trained = False
    
    def save_training_data(self, data_point: Dict, output_dir: str = 'data/ml_training'):
        """
        保存训练数据点（用于未来训练模型）
        
        Args:
            data_point: {
                'keyword': str,
                'channel_analysis': dict,
                'trend': dict,
                'relevance_score': float,
                'actual_views': int (可选，稍后更新),
                'timestamp': str
            }
        """
        try:
            os.makedirs(output_dir, exist_ok=True)
            
            # 生成唯一文件名
            timestamp = datetime.utcnow().strftime('%Y%m%d_%H%M%S')
            filename = f"{output_dir}/training_data_{timestamp}.json"
            
            # 添加特征向量
            features = self._extract_features(
                data_point['keyword'],
                data_point['channel_analysis'],
                data_point['trend'],
                data_point.get('relevance_score', 0)
            )
            
            data_point['features'] = features.tolist()[0]
            data_point['feature_names'] = self.feature_names
            
            # 保存
            with open(filename, 'w') as f:
                json.dump(data_point, f, indent=2)
            
            print(f"📊 Training data saved: {filename}")
        except Exception as e:
            print(f"⚠️  Failed to save training data: {e}")


# 全局实例（懒加载）
_predictor_instance = None

def get_ml_performance_predictor(model_path: Optional[str] = None) -> MLPerformancePredictor:
    """获取预测器单例"""
    global _predictor_instance
    if _predictor_instance is None:
        _predictor_instance = MLPerformancePredictor(model_path)
    return _predictor_instance
