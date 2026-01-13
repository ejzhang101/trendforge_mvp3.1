"""
Machine Learning Enhanced Predictor
使用机器学习模型提升预测准确性
"""

from typing import List, Dict, Optional, Tuple
import numpy as np
from datetime import datetime
import warnings
warnings.filterwarnings('ignore')

# Machine Learning Libraries
try:
    from sklearn.ensemble import RandomForestRegressor, GradientBoostingRegressor, VotingRegressor, StackingRegressor
    from sklearn.model_selection import train_test_split, cross_val_score, GridSearchCV, RandomizedSearchCV, KFold
    from sklearn.preprocessing import StandardScaler, RobustScaler, PowerTransformer
    from sklearn.feature_selection import SelectKBest, f_regression
    from sklearn.metrics import mean_absolute_error, mean_squared_error, r2_score, mean_absolute_percentage_error
    from sklearn.linear_model import Ridge, Lasso, ElasticNet
    SKLEARN_AVAILABLE = True
except ImportError:
    SKLEARN_AVAILABLE = False
    print("⚠️  scikit-learn not available")

try:
    import xgboost as xgb
    XGBOOST_AVAILABLE = True
except (ImportError, Exception) as e:
    XGBOOST_AVAILABLE = False
    print(f"⚠️  XGBoost not available: {e}")

try:
    import lightgbm as lgb
    LIGHTGBM_AVAILABLE = True
except (ImportError, Exception) as e:
    LIGHTGBM_AVAILABLE = False
    print(f"⚠️  LightGBM not available: {e}")


class MLPredictor:
    """
    机器学习预测器 - 使用多种模型提升预测准确性
    """
    
    def __init__(self):
        self.models = {}
        # 使用RobustScaler，对异常值更稳健
        self.scaler = RobustScaler() if SKLEARN_AVAILABLE else None
        self.is_trained = False
        self.feature_importance = {}
        self.feature_selector = None
        self.selected_features = None
        # 用于对数变换的标记
        self.use_log_transform = False
        self.y_scaler = None  # 用于目标变量的标准化
        
    def extract_features(
        self,
        video: Dict,
        channel_analysis: Dict,
        trend_data: Dict,
        period_avg: float = 0
    ) -> np.ndarray:
        """
        提取特征向量
        
        特征包括：
        1. 频道特征：平均播放量、中位数播放量、视频总数
        2. 趋势特征：热度分数、相关性分数、表现潜力分数
        3. 内容特征：标题长度、关键词数量、内容主题
        4. 时间特征：发布时间（小时、星期）、发布时间段
        5. 互动特征：历史平均互动率
        """
        features = []
        
        # 1. 频道特征
        high_performers = channel_analysis.get('high_performers', {})
        features.append(float(high_performers.get('avg_views', 0) or 0))
        features.append(float(high_performers.get('median_views', 0) or 0))
        features.append(float(high_performers.get('total_videos', 0) or 0))
        features.append(float(period_avg or 0))
        
        # 2. 趋势特征
        features.append(float(trend_data.get('viral_potential', 50)))
        features.append(float(trend_data.get('relevance_score', 50)))
        features.append(float(trend_data.get('performance_score', 50)))
        features.append(float(trend_data.get('match_score', 50)))
        features.append(float(trend_data.get('growth_rate', 0)))
        
        # 3. 内容特征
        title = video.get('title', '')
        description = video.get('description', '')
        features.append(float(len(title)))
        features.append(float(len(description)))
        
        # 标题关键词数量（简单估算）
        title_words = len(title.split())
        features.append(float(title_words))
        
        # 内容主题匹配度
        content_style = channel_analysis.get('content_style', {})
        primary_style = content_style.get('primary_style', 'general')
        style_score = 1.0 if primary_style != 'general' else 0.5
        features.append(float(style_score))
        
        # 4. 时间特征
        published_at = video.get('publishedAt', '')
        try:
            if isinstance(published_at, str):
                publish_date = datetime.fromisoformat(published_at.replace('Z', '+00:00'))
            else:
                publish_date = published_at
            features.append(float(publish_date.hour))  # 发布小时
            features.append(float(publish_date.weekday()))  # 星期几
            # 是否周末
            features.append(float(1.0 if publish_date.weekday() >= 5 else 0.0))
        except:
            features.extend([12.0, 3.0, 0.0])  # 默认值
        
        # 5. 互动特征（如果有历史数据）
        features.append(float(high_performers.get('avg_engagement_rate', 0) or 0))
        
        # 6. 频道规模特征
        subscriber_count = channel_analysis.get('target_audience', {}).get('subscriber_count', 0)
        features.append(float(subscriber_count))
        
        # 7. 标题优化特征
        title_length = len(title)
        if 30 <= title_length <= 60:
            title_opt = 1.0
        elif 20 <= title_length < 30 or 60 < title_length <= 70:
            title_opt = 0.8
        else:
            title_opt = 0.5
        features.append(float(title_opt))
        
        # 8. 高级特征：视频时长（如果有）
        duration_seconds = video.get('duration', 0)
        if isinstance(duration_seconds, str):
            # 解析ISO 8601格式（如PT5M30S）
            import re
            match = re.match(r'PT(?:(\d+)H)?(?:(\d+)M)?(?:(\d+)S)?', duration_seconds)
            if match:
                hours = int(match.group(1) or 0)
                minutes = int(match.group(2) or 0)
                seconds = int(match.group(3) or 0)
                duration_seconds = hours * 3600 + minutes * 60 + seconds
            else:
                duration_seconds = 0
        features.append(float(duration_seconds))
        
        # 9. 高级特征：视频时长类别
        if duration_seconds > 0:
            if duration_seconds < 60:
                duration_category = 1  # 短视频
            elif duration_seconds < 300:
                duration_category = 2  # 中等视频
            elif duration_seconds < 600:
                duration_category = 3  # 长视频
            else:
                duration_category = 4  # 超长视频
        else:
            duration_category = 2  # 默认中等
        features.append(float(duration_category))
        
        # 10. 高级特征：标题情感倾向（简单估算）
        title_lower = title.lower()
        positive_words = ['best', 'great', 'amazing', 'awesome', 'top', 'win', 'success']
        negative_words = ['worst', 'bad', 'fail', 'lose', 'terrible', 'awful']
        positive_count = sum(1 for word in positive_words if word in title_lower)
        negative_count = sum(1 for word in negative_words if word in title_lower)
        sentiment_score = (positive_count - negative_count) / max(1, len(title.split()))
        features.append(float(sentiment_score))
        
        # 11. 高级特征：标题包含数字
        has_numbers = 1.0 if any(char.isdigit() for char in title) else 0.0
        features.append(float(has_numbers))
        
        # 12. 高级特征：标题包含问号
        has_question = 1.0 if '?' in title else 0.0
        features.append(float(has_question))
        
        # 13. 高级特征：标题包含感叹号
        has_exclamation = 1.0 if '!' in title else 0.0
        features.append(float(has_exclamation))
        
        # 14. 高级特征：频道增长趋势（基于视频总数）
        total_videos = high_performers.get('total_videos', 0)
        if total_videos > 0:
            # 估算频道年龄（假设每周发布1个视频）
            estimated_age_weeks = total_videos
            growth_trend = min(1.0, estimated_age_weeks / 100)  # 归一化到0-1
        else:
            growth_trend = 0.0
        features.append(float(growth_trend))
        
        # 15. 高级特征：播放量稳定性（变异系数）
        avg_views = high_performers.get('avg_views', 0)
        median_views = high_performers.get('median_views', 0)
        if avg_views > 0 and median_views > 0:
            # 使用中位数和平均值的差异作为稳定性指标
            stability = 1.0 - abs(avg_views - median_views) / max(avg_views, median_views)
        else:
            stability = 0.5
        features.append(float(stability))
        
        # 16. 高级特征：趋势增长率（归一化）
        growth_rate = trend_data.get('growth_rate', 0)
        normalized_growth = min(1.0, max(0.0, (growth_rate + 100) / 200))  # 归一化到0-1
        features.append(float(normalized_growth))
        
        # 17. 高级特征：综合匹配分数（归一化）
        match_score = trend_data.get('match_score', 50)
        normalized_match = match_score / 100.0
        features.append(float(normalized_match))
        
        # 18. 高级特征：热度与相关性的交互
        viral_potential = trend_data.get('viral_potential', 50)
        relevance_score = trend_data.get('relevance_score', 50)
        interaction = (viral_potential / 100.0) * (relevance_score / 100.0)
        features.append(float(interaction))
        
        return np.array(features, dtype=np.float32)
    
    def train_models(
        self,
        X: np.ndarray,
        y: np.ndarray,
        test_size: float = 0.2,
        use_cross_validation: bool = True,
        cv_folds: int = 5
    ) -> Dict:
        """
        训练多个模型并选择最佳模型 - 优化版（确保跨频道一致性）
        
        改进：
        1. 异常值处理
        2. 特征选择
        3. 超参数调优
        4. 集成学习
        5. 交叉验证（确保评估一致性）
        6. 对数变换（减少数据分布差异）
        7. 自适应超参数（根据数据特征调整）
        """
        if not SKLEARN_AVAILABLE:
            return {'error': 'scikit-learn not available'}
        
        # 分析数据特征，决定是否使用对数变换
        y_mean = np.mean(y)
        y_std = np.std(y)
        y_cv = y_std / y_mean if y_mean > 0 else 0  # 变异系数
        
        # 如果变异系数 > 0.5，使用对数变换（减少不同频道数据分布差异）
        self.use_log_transform = y_cv > 0.5 and y_mean > 0
        if self.use_log_transform:
            print(f"📊 数据变异系数: {y_cv:.2f}，使用对数变换以减少分布差异")
            y_clean = np.log1p(y)  # log1p = log(1+x)，避免log(0)
            X_clean = X.copy()
        else:
            X_clean = X
            y_clean = y.copy()
        
        # 异常值处理：使用更宽松的标准（保留更多数据）
        # 只移除极端异常值（超过3个标准差）
        if not self.use_log_transform:
            y_mean_clean = np.mean(y_clean)
            y_std_clean = np.std(y_clean)
            if y_std_clean > 0:
                lower_bound = max(0, y_mean_clean - 3 * y_std_clean)
                upper_bound = y_mean_clean + 3 * y_std_clean
                mask = (y_clean >= lower_bound) & (y_clean <= upper_bound)
                X_clean = X_clean[mask]
                y_clean = y_clean[mask]
        
        if len(X_clean) < 10:
            # 如果清理后数据太少，使用原始数据
            X_clean = X
            y_clean = np.log1p(y) if self.use_log_transform else y
        
        # 自适应超参数：根据数据量调整
        n_samples = len(X_clean)
        if n_samples < 30:
            # 小数据集：使用更简单的模型
            max_depth_rf = 8
            max_depth_gb = 4
            n_estimators = 100
        elif n_samples < 50:
            # 中等数据集
            max_depth_rf = 10
            max_depth_gb = 5
            n_estimators = 120
        else:
            # 大数据集
            max_depth_rf = 12
            max_depth_gb = 6
            n_estimators = 150
        
        print(f"📊 自适应参数: n_samples={n_samples}, max_depth_rf={max_depth_rf}, max_depth_gb={max_depth_gb}")
        
        # 初始化K-Fold（如果需要）
        kf = None
        if use_cross_validation and n_samples >= 20:
            # 使用K-Fold交叉验证获得更稳健的评估
            kf = KFold(n_splits=min(cv_folds, n_samples // 5), shuffle=True, random_state=42)
            print(f"📊 使用 {kf.n_splits}-Fold 交叉验证")
        
        # 数据分割（用于最终评估）
        split_idx = int(len(X_clean) * (1 - test_size))
        X_train = X_clean[:split_idx]
        X_test = X_clean[split_idx:]
        y_train = y_clean[:split_idx]
        y_test = y_clean[split_idx:]
        
        # 确保测试集至少有10个样本（如果数据足够）
        min_test_samples = 10
        if len(X_test) < min_test_samples and len(X_clean) >= min_test_samples * 2:
            # 如果测试集太小且数据足够，从训练集中再分一些
            additional_test = min_test_samples - len(X_test)
            if additional_test <= len(X_train):
                X_test = np.concatenate([X_test, X_train[-additional_test:]])
                y_test = np.concatenate([y_test, y_train[-additional_test:]])
                X_train = X_train[:-additional_test]
                y_train = y_train[:-additional_test]
        
        print(f"📊 数据分割: 训练集 {len(X_train)} 个样本, 测试集 {len(X_test)} 个样本")
        if not self.use_log_transform:
            print(f"   测试集播放量范围: {y_test.min():.0f} - {y_test.max():.0f}, 均值: {y_test.mean():.0f}")
        else:
            print(f"   测试集（对数变换后）范围: {y_test.min():.3f} - {y_test.max():.3f}, 均值: {y_test.mean():.3f}")
        
        # 特征选择：选择最重要的特征（更保守，保留更多特征）
        if len(X_train) > 15 and X_train.shape[1] > 10:
            try:
                # 选择前k个最重要的特征（k = min(特征数, 20)，保留更多特征）
                k = min(X_train.shape[1], 20)
                self.feature_selector = SelectKBest(score_func=f_regression, k=k)
                X_train_selected = self.feature_selector.fit_transform(X_train, y_train)
                X_test_selected = self.feature_selector.transform(X_test)
                self.selected_features = self.feature_selector.get_support()
                print(f"✅ 特征选择：从 {X_train.shape[1]} 个特征中选择 {k} 个最重要的")
            except Exception as e:
                print(f"⚠️  特征选择失败，使用所有特征: {e}")
                # 如果特征选择失败，使用所有特征
                X_train_selected = X_train
                X_test_selected = X_test
                self.selected_features = None
        else:
            X_train_selected = X_train
            X_test_selected = X_test
            self.selected_features = None
        
        # 特征标准化（使用RobustScaler，对异常值更稳健）
        X_train_scaled = self.scaler.fit_transform(X_train_selected)
        X_test_scaled = self.scaler.transform(X_test_selected)
        
        results = {}
        
        # 1. 随机森林（使用自适应超参数）
        try:
            rf_model = RandomForestRegressor(
                n_estimators=n_estimators,
                max_depth=max_depth_rf,
                min_samples_split=5,
                min_samples_leaf=3,
                max_features='sqrt',
                random_state=42,
                n_jobs=-1
            )
            # 使用交叉验证评估（如果启用）
            if kf is not None:
                cv_scores = cross_val_score(rf_model, X_train_scaled, y_train, cv=kf, scoring='r2', n_jobs=-1)
                cv_mae_scores = -cross_val_score(rf_model, X_train_scaled, y_train, cv=kf, scoring='neg_mean_absolute_error', n_jobs=-1)
                print(f"   RF CV R²: {cv_scores.mean():.3f} (+/- {cv_scores.std() * 2:.3f})")
            
            rf_model.fit(X_train_scaled, y_train)
            rf_pred = rf_model.predict(X_test_scaled)
            
            # 如果使用对数变换，需要转换回原始尺度
            if self.use_log_transform:
                rf_pred = np.expm1(rf_pred)
                y_test_orig = np.expm1(y_test)
            else:
                y_test_orig = y_test
            
            rf_mae = mean_absolute_error(y_test_orig, rf_pred)
            rf_r2 = r2_score(y_test_orig, rf_pred)
            rf_mape = mean_absolute_percentage_error(y_test_orig, rf_pred) * 100
            rf_rmse = np.sqrt(mean_squared_error(y_test_orig, rf_pred))
            
            self.models['random_forest'] = rf_model
            results['random_forest'] = {
                'mae': float(rf_mae),
                'mape': float(rf_mape),
                'rmse': float(rf_rmse),
                'r2': float(rf_r2),
                'feature_importance': {
                    f'feature_{i}': float(imp)
                    for i, imp in enumerate(rf_model.feature_importances_)
                }
            }
        except Exception as e:
            print(f"Random Forest training failed: {e}")
        
        # 2. 梯度提升（使用自适应超参数）
        try:
            gb_model = GradientBoostingRegressor(
                n_estimators=n_estimators,
                max_depth=max_depth_gb,
                learning_rate=0.08,
                min_samples_split=5,
                min_samples_leaf=3,
                subsample=0.85,
                random_state=42
            )
            # 使用交叉验证评估（如果启用）
            if kf is not None:
                cv_scores = cross_val_score(gb_model, X_train_scaled, y_train, cv=kf, scoring='r2', n_jobs=-1)
                print(f"   GB CV R²: {cv_scores.mean():.3f} (+/- {cv_scores.std() * 2:.3f})")
            
            gb_model.fit(X_train_scaled, y_train)
            gb_pred = gb_model.predict(X_test_scaled)
            
            # 如果使用对数变换，需要转换回原始尺度
            if self.use_log_transform:
                gb_pred = np.expm1(gb_pred)
                y_test_orig = np.expm1(y_test)
            else:
                y_test_orig = y_test
            
            gb_mae = mean_absolute_error(y_test_orig, gb_pred)
            gb_r2 = r2_score(y_test_orig, gb_pred)
            gb_mape = mean_absolute_percentage_error(y_test_orig, gb_pred) * 100
            gb_rmse = np.sqrt(mean_squared_error(y_test_orig, gb_pred))
            
            self.models['gradient_boosting'] = gb_model
            results['gradient_boosting'] = {
                'mae': float(gb_mae),
                'mape': float(gb_mape),
                'rmse': float(gb_rmse),
                'r2': float(gb_r2),
                'feature_importance': {
                    f'feature_{i}': float(imp)
                    for i, imp in enumerate(gb_model.feature_importances_)
                }
            }
        except Exception as e:
            print(f"Gradient Boosting training failed: {e}")
        
        # 3. XGBoost（使用自适应超参数）
        if XGBOOST_AVAILABLE:
            try:
                xgb_model = xgb.XGBRegressor(
                    n_estimators=n_estimators,
                    max_depth=max_depth_gb,
                    learning_rate=0.08,
                    min_child_weight=5,
                    subsample=0.85,
                    colsample_bytree=0.85,
                    gamma=0.2,
                    reg_alpha=0.2,
                    reg_lambda=1.5,
                    objective='reg:squarederror',
                    random_state=42,
                    n_jobs=-1
                )
                xgb_model.fit(X_train_scaled, y_train)
                xgb_pred = xgb_model.predict(X_test_scaled)
                
                # 如果使用对数变换，需要转换回原始尺度
                if self.use_log_transform:
                    xgb_pred = np.expm1(xgb_pred)
                    y_test_orig = np.expm1(y_test)
                else:
                    y_test_orig = y_test
                
                xgb_mae = mean_absolute_error(y_test_orig, xgb_pred)
                xgb_r2 = r2_score(y_test_orig, xgb_pred)
                xgb_mape = mean_absolute_percentage_error(y_test_orig, xgb_pred) * 100
                xgb_rmse = np.sqrt(mean_squared_error(y_test_orig, xgb_pred))
                
                self.models['xgboost'] = xgb_model
                results['xgboost'] = {
                    'mae': float(xgb_mae),
                    'mape': float(xgb_mape),
                    'rmse': float(xgb_rmse),
                    'r2': float(xgb_r2),
                    'feature_importance': {
                        f'feature_{i}': float(imp)
                        for i, imp in enumerate(xgb_model.feature_importances_)
                    }
                }
            except Exception as e:
                print(f"XGBoost training failed: {e}")
        
        # 4. LightGBM（使用自适应超参数）
        if LIGHTGBM_AVAILABLE:
            try:
                lgb_model = lgb.LGBMRegressor(
                    n_estimators=n_estimators,
                    max_depth=max_depth_gb + 1,  # LightGBM通常需要稍深的树
                    learning_rate=0.08,
                    num_leaves=25,
                    min_child_samples=25,
                    subsample=0.85,
                    colsample_bytree=0.85,
                    reg_alpha=0.2,
                    reg_lambda=1.5,
                    random_state=42,
                    n_jobs=-1,
                    verbose=-1
                )
                lgb_model.fit(X_train_scaled, y_train)
                lgb_pred = lgb_model.predict(X_test_scaled)
                
                # 如果使用对数变换，需要转换回原始尺度
                if self.use_log_transform:
                    lgb_pred = np.expm1(lgb_pred)
                    y_test_orig = np.expm1(y_test)
                else:
                    y_test_orig = y_test
                
                lgb_mae = mean_absolute_error(y_test_orig, lgb_pred)
                lgb_r2 = r2_score(y_test_orig, lgb_pred)
                lgb_mape = mean_absolute_percentage_error(y_test_orig, lgb_pred) * 100
                lgb_rmse = np.sqrt(mean_squared_error(y_test_orig, lgb_pred))
                
                self.models['lightgbm'] = lgb_model
                results['lightgbm'] = {
                    'mae': float(lgb_mae),
                    'mape': float(lgb_mape),
                    'rmse': float(lgb_rmse),
                    'r2': float(lgb_r2),
                    'feature_importance': {
                        f'feature_{i}': float(imp)
                        for i, imp in enumerate(lgb_model.feature_importances_)
                    }
                }
            except Exception as e:
                print(f"LightGBM training failed: {e}")
        
        # 5. 集成模型：Stacking（如果至少有两个模型）
        if len(self.models) >= 2:
            try:
                # 使用前两个最佳模型作为基模型
                base_models = list(self.models.items())[:2]
                base_estimators = [(name, model) for name, model in base_models]
                
                # 使用Ridge作为元模型
                meta_model = Ridge(alpha=1.0)
                stacking_model = StackingRegressor(
                    estimators=base_estimators,
                    final_estimator=meta_model,
                    cv=3,
                    n_jobs=-1
                )
                stacking_model.fit(X_train_scaled, y_train)
                stacking_pred = stacking_model.predict(X_test_scaled)
                
                # 如果使用对数变换，需要转换回原始尺度
                if self.use_log_transform:
                    stacking_pred = np.expm1(stacking_pred)
                    y_test_orig = np.expm1(y_test)
                else:
                    y_test_orig = y_test
                
                stacking_mae = mean_absolute_error(y_test_orig, stacking_pred)
                stacking_r2 = r2_score(y_test_orig, stacking_pred)
                stacking_mape = mean_absolute_percentage_error(y_test_orig, stacking_pred) * 100
                stacking_rmse = np.sqrt(mean_squared_error(y_test_orig, stacking_pred))
                
                self.models['stacking'] = stacking_model
                results['stacking'] = {
                    'mae': float(stacking_mae),
                    'mape': float(stacking_mape),
                    'rmse': float(stacking_rmse),
                    'r2': float(stacking_r2)
                }
            except Exception as e:
                print(f"Stacking model training failed: {e}")
        
        # 选择最佳模型（综合考虑R²、MAPE和稳定性，确保跨频道一致性）
        # 目标：R² > 0.5, MAPE < 30%（更宽松但一致的标准）
        best_model_name = None
        best_score = -float('inf')
        
        for model_name, metrics in results.items():
            r2 = metrics.get('r2', 0)
            mape = metrics.get('mape', 100)
            mae = metrics.get('mae', float('inf'))
            rmse = metrics.get('rmse', float('inf'))
            
            # 计算相对MAE（相对于均值），确保跨频道一致性
            y_mean_orig = np.expm1(y_test.mean()) if self.use_log_transform else y_test.mean()
            relative_mae = (mae / y_mean_orig) * 100 if y_mean_orig > 0 else 100
            
            # 综合评分：R²权重50%，MAPE权重30%，相对MAE权重20%（更平衡）
            # 使用更一致的标准，不偏向特定数据分布
            bonus = 0
            if r2 >= 0.5:  # 降低阈值，更一致
                bonus += 0.1
            if mape <= 30:  # 更宽松的MAPE标准
                bonus += 0.1
            if relative_mae <= 20:  # 相对MAE <= 20%
                bonus += 0.05
            
            # MAPE归一化到0-1（假设最大MAPE为100%）
            mape_score = max(0, 1 - min(mape, 100) / 100)
            # 相对MAE归一化
            relative_mae_score = max(0, 1 - min(relative_mae, 100) / 100)
            
            # 更平衡的评分：R² 50%, MAPE 30%, 相对MAE 20%
            score = r2 * 0.5 + mape_score * 0.3 + relative_mae_score * 0.2 + bonus
            
            if score > best_score:
                best_score = score
                best_model_name = model_name
        
        # 如果没有找到合适的模型，使用R²最高的
        if best_model_name is None:
            best_r2 = -float('inf')
            for model_name, metrics in results.items():
                if metrics.get('r2', 0) > best_r2:
                    best_r2 = metrics.get('r2', 0)
                    best_model_name = model_name
        
        print(f"✅ 最佳模型选择: {best_model_name}, R²={results.get(best_model_name, {}).get('r2', 0):.3f}, MAPE={results.get(best_model_name, {}).get('mape', 0):.1f}%")
        
        self.best_model_name = best_model_name
        self.is_trained = True
        
        best_metrics = results.get(best_model_name, {})
        results['best_model'] = best_model_name
        results['best_r2'] = best_metrics.get('r2', 0)
        results['best_mape'] = best_metrics.get('mape', 0)
        results['best_mae'] = best_metrics.get('mae', 0)
        results['best_rmse'] = best_metrics.get('rmse', 0)
        
        return results
    
    def predict(
        self,
        video: Dict,
        channel_analysis: Dict,
        trend_data: Dict,
        period_avg: float = 0
    ) -> Dict:
        """
        使用训练好的模型进行预测
        """
        if not self.is_trained or not self.best_model_name:
            # 如果模型未训练，使用传统方法
            return self._fallback_predict(video, channel_analysis, trend_data, period_avg)
        
        # 提取特征
        features = self.extract_features(video, channel_analysis, trend_data, period_avg)
        features = features.reshape(1, -1)
        
        # 特征选择（如果已训练）
        if self.feature_selector is not None:
            features = self.feature_selector.transform(features)
        
        # 标准化
        features_scaled = self.scaler.transform(features)
        
        # 使用最佳模型预测
        best_model = self.models.get(self.best_model_name)
        if best_model:
            prediction = best_model.predict(features_scaled)[0]
            
            # 如果使用对数变换，需要转换回原始尺度
            if self.use_log_transform:
                prediction = np.expm1(prediction)
            
            prediction = max(500, int(prediction))  # 确保最小值
            
            # 使用集成预测（如果有多个模型）
            ensemble_predictions = []
            model_weights = []
            
            for model_name, model in self.models.items():
                try:
                    pred = model.predict(features_scaled)[0]
                    # 如果使用对数变换，需要转换回原始尺度
                    if self.use_log_transform:
                        pred = np.expm1(pred)
                    ensemble_predictions.append(pred)
                    
                    # 根据模型类型分配权重
                    if model_name == self.best_model_name:
                        model_weights.append(0.4)  # 最佳模型权重最高
                    elif model_name == 'stacking':
                        model_weights.append(0.3)  # Stacking模型权重较高
                    else:
                        model_weights.append(0.1)  # 其他模型权重较低
                except:
                    pass
            
            if ensemble_predictions and len(ensemble_predictions) > 1:
                # 归一化权重
                total_weight = sum(model_weights)
                if total_weight > 0:
                    model_weights = [w / total_weight for w in model_weights]
                    # 使用加权平均
                    ensemble_pred = sum(pred * weight for pred, weight in zip(ensemble_predictions, model_weights))
                    prediction = max(500, int(ensemble_pred))
            
            return {
                'predicted_views': prediction,
                'model_used': self.best_model_name,
                'confidence': 0.8 if self.is_trained else 0.5
            }
        else:
            return self._fallback_predict(video, channel_analysis, trend_data, period_avg)
    
    def _fallback_predict(
        self,
        video: Dict,
        channel_analysis: Dict,
        trend_data: Dict,
        period_avg: float
    ) -> Dict:
        """
        回退到传统预测方法
        """
        high_performers = channel_analysis.get('high_performers', {})
        median_views = high_performers.get('median_views')
        avg_views = high_performers.get('avg_views')
        
        if median_views and avg_views:
            base_views = int(median_views * 0.7 + avg_views * 0.3)
        elif median_views:
            base_views = int(median_views)
        elif avg_views:
            base_views = int(avg_views)
        else:
            base_views = int(period_avg) if period_avg > 0 else 10000
        
        viral_potential = trend_data.get('viral_potential', 50)
        if viral_potential >= 90:
            multiplier = 2.2 + (viral_potential - 90) * 0.03
        elif viral_potential >= 70:
            multiplier = 1.6 + (viral_potential - 70) * 0.03
        elif viral_potential >= 50:
            multiplier = 1.2 + (viral_potential - 50) * 0.02
        else:
            multiplier = 0.9 + (viral_potential / 50) * 0.3
        
        predicted_views = int(base_views * multiplier)
        return {
            'predicted_views': max(500, predicted_views),
            'model_used': 'fallback',
            'confidence': 0.5
        }


# 全局实例
ml_predictor = MLPredictor()
