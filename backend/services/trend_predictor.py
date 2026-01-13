"""
Prophet Time Series Prediction Engine
MVP 3.0 - Predictive trend forecasting with confidence intervals
"""

import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from typing import List, Dict, Optional, Tuple
import json

# Prophet for time series forecasting
try:
    from prophet import Prophet
    PROPHET_AVAILABLE = True
except ImportError:
    PROPHET_AVAILABLE = False
    print("⚠️ Prophet not installed. Install: pip install prophet")

# For data storage
try:
    from sqlalchemy import create_engine, Column, String, Float, DateTime, Integer, JSON
    from sqlalchemy.ext.declarative import declarative_base
    from sqlalchemy.orm import sessionmaker
    SQLALCHEMY_AVAILABLE = True
    Base = declarative_base()
except ImportError:
    SQLALCHEMY_AVAILABLE = False
    print("⚠️ SQLAlchemy not installed. Install: pip install sqlalchemy")


class TrendHistoryModel(Base):
    """
    Database model for storing historical trend data
    """
    __tablename__ = 'trend_history'
    
    id = Column(Integer, primary_key=True)
    keyword = Column(String, index=True)
    date = Column(DateTime, index=True)
    search_volume = Column(Float)
    twitter_score = Column(Float, nullable=True)
    reddit_score = Column(Float, nullable=True)
    google_score = Column(Float, nullable=True)
    composite_score = Column(Float)
    trend_metadata = Column(JSON, nullable=True)  # Renamed from 'metadata' (SQLAlchemy reserved)
    created_at = Column(DateTime, default=datetime.utcnow)


class TrendPredictionEngine:
    """
    Advanced trend prediction using Facebook Prophet
    
    Features:
    - Time series forecasting (7-30 days ahead)
    - Confidence intervals
    - Trend direction detection
    - Seasonality analysis
    - Anomaly detection
    """
    
    def __init__(self, db_url: Optional[str] = None, min_history_days: int = 30):
        """
        Initialize prediction engine
        
        Args:
            db_url: Database connection string (e.g., 'postgresql://...')
            min_history_days: Minimum days of historical data required
        """
        self.min_history_days = min_history_days
        self.db_engine = None
        self.Session = None
        
        if SQLALCHEMY_AVAILABLE and db_url:
            try:
                self.db_engine = create_engine(db_url)
                Base.metadata.create_all(self.db_engine)
                self.Session = sessionmaker(bind=self.db_engine)
                print("✅ Database connected for trend history")
            except Exception as e:
                print(f"⚠️ Database connection failed: {e}")
    
    async def store_trend_data(self, keyword: str, data: Dict):
        """
        Store current trend data for future predictions
        
        Args:
            keyword: The trending keyword
            data: Trend data (scores, metadata)
        """
        if not self.Session:
            print("⚠️ Database not available, skipping storage")
            return
        
        session = self.Session()
        try:
            trend_record = TrendHistoryModel(
                keyword=keyword,
                date=datetime.utcnow(),
                search_volume=data.get('search_volume', 0),
                twitter_score=data.get('twitter_score', 0),
                reddit_score=data.get('reddit_score', 0),
                google_score=data.get('google_score', 0),
                composite_score=data.get('composite_score', 0),
                trend_metadata=data.get('metadata', {})
            )
            session.add(trend_record)
            session.commit()
        except Exception as e:
            print(f"Error storing trend data: {e}")
            session.rollback()
        finally:
            session.close()
    
    def get_historical_data(self, keyword: str, days: int = 90) -> Optional[pd.DataFrame]:
        """
        Retrieve historical trend data for a keyword
        
        Args:
            keyword: The keyword to query
            days: Number of days of history to retrieve
        
        Returns:
            DataFrame with columns: date, composite_score
        """
        if not self.Session:
            print("⚠️ Database not available, using mock data")
            return self._generate_mock_historical_data(keyword, days)
        
        session = self.Session()
        try:
            cutoff_date = datetime.utcnow() - timedelta(days=days)
            
            records = session.query(TrendHistoryModel).filter(
                TrendHistoryModel.keyword == keyword,
                TrendHistoryModel.date >= cutoff_date
            ).order_by(TrendHistoryModel.date).all()
            
            if len(records) < self.min_history_days:
                print(f"⚠️ Insufficient historical data for {keyword} ({len(records)} days)")
                return None
            
            df = pd.DataFrame([
                {
                    'date': r.date,
                    'composite_score': r.composite_score,
                    'google_score': r.google_score,
                    'twitter_score': r.twitter_score,
                    'reddit_score': r.reddit_score
                }
                for r in records
            ])
            
            return df
            
        except Exception as e:
            print(f"Error retrieving historical data: {e}")
            return None
        finally:
            session.close()
    
    def _generate_mock_historical_data(self, keyword: str, days: int) -> pd.DataFrame:
        """
        Generate mock historical data for testing
        """
        # Create synthetic trend data with realistic patterns
        dates = pd.date_range(end=datetime.utcnow(), periods=days, freq='D')
        
        # Base trend with noise
        base_trend = 50 + np.random.randn(days).cumsum() * 2
        
        # Add weekly seasonality
        weekly_pattern = 10 * np.sin(np.arange(days) * 2 * np.pi / 7)
        
        # Add random spikes (viral moments)
        spikes = np.zeros(days)
        spike_indices = np.random.choice(days, size=max(1, days // 20), replace=False)
        spikes[spike_indices] = np.random.uniform(20, 50, size=len(spike_indices))
        
        composite_score = base_trend + weekly_pattern + spikes
        composite_score = np.clip(composite_score, 0, 100)
        
        df = pd.DataFrame({
            'date': dates,
            'composite_score': composite_score,
            'google_score': composite_score * 0.4 + np.random.randn(days) * 2,
            'twitter_score': composite_score * 0.3 + np.random.randn(days) * 3,
            'reddit_score': composite_score * 0.3 + np.random.randn(days) * 3
        })
        
        return df
    
    def predict_trend(self, keyword: str, forecast_days: int = 7) -> Optional[Dict]:
        """
        Predict future trend for a keyword using Prophet
        
        Args:
            keyword: Keyword to predict
            forecast_days: Number of days to forecast (default: 7)
        
        Returns:
            {
                'keyword': str,
                'predictions': List[Dict],  # Daily predictions
                'trend_direction': 'rising'|'falling'|'stable',
                'confidence': float,  # 0-100
                'peak_day': int,  # Days until peak (if rising)
                'summary': str,
                'model_accuracy': Dict
            }
        """
        if not PROPHET_AVAILABLE:
            print("⚠️ Prophet not available")
            return None
        
        # Get historical data (reduced to 60 days for faster processing)
        historical_df = self.get_historical_data(keyword, days=60)
        
        # If no database data, generate mock data quickly
        if historical_df is None or len(historical_df) < self.min_history_days:
            print(f"⚠️ Insufficient historical data for {keyword}, generating mock data...")
            historical_df = self._generate_mock_historical_data(keyword, days=60)
        
        if historical_df is None or len(historical_df) < self.min_history_days:
            print(f"⚠️ Failed to generate data for {keyword}")
            return None
        
        try:
            # Prepare data for Prophet
            prophet_df = historical_df[['date', 'composite_score']].copy()
            prophet_df.columns = ['ds', 'y']
            
            # Initialize Prophet model with optimized parameters for speed
            model = Prophet(
                changepoint_prior_scale=0.05,  # Flexibility in trend changes
                seasonality_prior_scale=10.0,   # Strength of seasonality
                seasonality_mode='additive',    # Additive seasonality
                daily_seasonality=False,
                weekly_seasonality=True,
                yearly_seasonality=False,
                interval_width=0.95,          # 95% confidence interval
                mcmc_samples=0,               # Disable MCMC for faster fitting (use MAP instead)
                n_changepoints=10             # Reduce changepoints for faster computation
            )
            
            # Fit model
            model.fit(prophet_df)
            
            # Make future predictions
            future = model.make_future_dataframe(periods=forecast_days, freq='D')
            forecast = model.predict(future)
            
            # Extract predictions
            predictions = self._extract_predictions(forecast, forecast_days)
            
            # Analyze trend direction
            trend_analysis = self._analyze_trend_direction(forecast, forecast_days)
            
            # Calculate confidence
            confidence = self._calculate_prediction_confidence(forecast, historical_df)
            
            # Detect peak
            peak_info = self._detect_peak(predictions)
            
            # Generate summary
            summary = self._generate_prediction_summary(
                keyword, trend_analysis, confidence, peak_info
            )
            
            # Model accuracy metrics
            accuracy = self._calculate_model_accuracy(model, prophet_df)
            
            return {
                'keyword': keyword,
                'predictions': predictions,
                'trend_direction': trend_analysis['direction'],
                'trend_strength': trend_analysis['strength'],
                'confidence': confidence,
                'peak_day': peak_info['peak_day'],
                'peak_score': peak_info['peak_score'],
                'summary': summary,
                'model_accuracy': accuracy,
                'forecast_start': datetime.utcnow().isoformat(),
                'forecast_end': (datetime.utcnow() + timedelta(days=forecast_days)).isoformat()
            }
            
        except Exception as e:
            print(f"❌ Prediction failed for {keyword}: {e}")
            import traceback
            traceback.print_exc()
            return None
    
    def _extract_predictions(self, forecast: pd.DataFrame, days: int) -> List[Dict]:
        """
        Extract daily predictions with confidence intervals
        """
        predictions = []
        
        # Get last N rows (future predictions)
        future_forecast = forecast.tail(days)
        
        for _, row in future_forecast.iterrows():
            predictions.append({
                'date': row['ds'].isoformat(),
                'predicted_score': round(float(row['yhat']), 2),
                'lower_bound': round(float(row['yhat_lower']), 2),
                'upper_bound': round(float(row['yhat_upper']), 2),
                'confidence_range': round(float(row['yhat_upper'] - row['yhat_lower']), 2)
            })
        
        return predictions
    
    def _analyze_trend_direction(self, forecast: pd.DataFrame, days: int) -> Dict:
        """
        Determine if trend is rising, falling, or stable
        """
        recent_values = forecast['yhat'].tail(days).values
        
        if len(recent_values) < 2:
            return {'direction': 'stable', 'strength': 0}
        
        # Calculate trend slope
        x = np.arange(len(recent_values))
        slope, _ = np.polyfit(x, recent_values, 1)
        
        # Normalize slope to 0-100
        strength = abs(slope) * 10
        strength = min(100, strength)
        
        # Determine direction
        if slope > 2:
            direction = 'rising'
        elif slope < -2:
            direction = 'falling'
        else:
            direction = 'stable'
        
        return {
            'direction': direction,
            'strength': round(strength, 2),
            'slope': round(slope, 4)
        }
    
    def _calculate_prediction_confidence(self, forecast: pd.DataFrame, 
                                        historical_df: pd.DataFrame) -> float:
        """
        Calculate confidence score based on prediction interval width
        
        Returns:
            Confidence score 0-100 (higher = more confident)
        """
        # Get future predictions
        future_forecast = forecast.tail(7)
        
        # Calculate average confidence interval width
        avg_interval_width = (
            future_forecast['yhat_upper'] - future_forecast['yhat_lower']
        ).mean()
        
        # Calculate average predicted value
        avg_prediction = future_forecast['yhat'].mean()
        
        # Confidence is inversely proportional to interval width
        if avg_prediction == 0:
            return 50.0
        
        relative_width = avg_interval_width / avg_prediction
        
        # Convert to 0-100 scale (smaller width = higher confidence)
        confidence = 100 * (1 - min(1, relative_width))
        
        # Adjust based on data quality
        data_quality_factor = min(1, len(historical_df) / 90)  # More data = higher confidence
        confidence *= data_quality_factor
        
        return round(confidence, 2)
    
    def _detect_peak(self, predictions: List[Dict]) -> Dict:
        """
        Detect if and when the trend will peak
        """
        scores = [p['predicted_score'] for p in predictions]
        
        if not scores:
            return {'peak_day': None, 'peak_score': None}
        
        max_score = max(scores)
        max_index = scores.index(max_score)
        
        # Check if peak is in future (not just the last day)
        is_peak = max_index < len(scores) - 1
        
        if is_peak:
            return {
                'peak_day': max_index + 1,  # Days from now
                'peak_score': max_score,
                'peak_date': predictions[max_index]['date']
            }
        else:
            return {
                'peak_day': None,
                'peak_score': max_score,
                'peak_date': None
            }
    
    def _generate_prediction_summary(self, keyword: str, trend: Dict, 
                                    confidence: float, peak: Dict) -> str:
        """
        Generate human-readable summary
        """
        direction = trend['direction']
        strength = trend['strength']
        
        # Direction description
        if direction == 'rising':
            if strength > 70:
                trend_desc = "快速上升"
            elif strength > 40:
                trend_desc = "稳定上升"
            else:
                trend_desc = "缓慢上升"
        elif direction == 'falling':
            if strength > 70:
                trend_desc = "快速下降"
            elif strength > 40:
                trend_desc = "稳定下降"
            else:
                trend_desc = "缓慢下降"
        else:
            trend_desc = "保持稳定"
        
        # Confidence description
        if confidence > 80:
            conf_desc = "高置信度"
        elif confidence > 60:
            conf_desc = "中等置信度"
        else:
            conf_desc = "低置信度"
        
        # Build summary
        summary = f"'{keyword}' 预计未来7天将{trend_desc}（{conf_desc}）"
        
        # Add peak info
        if peak['peak_day']:
            summary += f"，预计第{peak['peak_day']}天达到峰值"
        
        # Add recommendation
        if direction == 'rising' and confidence > 70:
            summary += "。🔥 建议立即制作相关内容！"
        elif direction == 'rising':
            summary += "。💡 可以考虑制作相关内容。"
        elif direction == 'falling':
            summary += "。⚠️ 热度正在下降，建议观望。"
        
        return summary
    
    def _calculate_model_accuracy(self, model, df: pd.DataFrame) -> Dict:
        """
        Calculate model accuracy metrics using cross-validation
        """
        try:
            from prophet.diagnostics import cross_validation, performance_metrics
            
            # Perform cross-validation (last 7 days as test)
            df_cv = cross_validation(
                model, 
                initial='30 days', 
                period='7 days', 
                horizon='7 days',
                parallel="processes"
            )
            
            # Calculate performance metrics
            perf_metrics = performance_metrics(df_cv)
            
            return {
                'mae': round(float(perf_metrics['mae'].mean()), 2),
                'rmse': round(float(perf_metrics['rmse'].mean()), 2),
                'mape': round(float(perf_metrics['mape'].mean()), 2),
                'coverage': round(float(perf_metrics['coverage'].mean()), 2)
            }
        except Exception as e:
            # If cross-validation fails, return basic metrics
            print(f"⚠️ Cross-validation failed: {e}")
            return {
                'mae': 0,
                'rmse': 0,
                'mape': 0,
                'coverage': 0.95
            }
    
    def batch_predict(self, keywords: List[str], 
                     forecast_days: int = 7) -> List[Dict]:
        """
        Predict trends for multiple keywords
        
        Args:
            keywords: List of keywords to predict
            forecast_days: Days to forecast for each
        
        Returns:
            List of prediction results
        """
        predictions = []
        
        for keyword in keywords:
            print(f"🔮 Predicting trend for: {keyword}")
            prediction = self.predict_trend(keyword, forecast_days)
            
            if prediction:
                predictions.append(prediction)
        
        # Sort by confidence * trend strength
        predictions.sort(
            key=lambda x: x['confidence'] * x['trend_strength'],
            reverse=True
        )
        
        return predictions
    
    def detect_emerging_trends(self, predictions: List[Dict], 
                              threshold: float = 70.0) -> List[Dict]:
        """
        Identify emerging trends from predictions
        
        Args:
            predictions: List of prediction results
            threshold: Minimum confidence score
        
        Returns:
            List of emerging trends with high confidence rising patterns
        """
        emerging = []
        
        for pred in predictions:
            is_emerging = (
                pred['trend_direction'] == 'rising' and
                pred['confidence'] >= threshold and
                pred['trend_strength'] > 50
            )
            
            if is_emerging:
                emerging.append({
                    'keyword': pred['keyword'],
                    'confidence': pred['confidence'],
                    'trend_strength': pred['trend_strength'],
                    'peak_day': pred['peak_day'],
                    'summary': pred['summary'],
                    'urgency': self._calculate_urgency(pred)
                })
        
        # Sort by urgency
        emerging.sort(key=lambda x: x['urgency'], reverse=True)
        
        return emerging
    
    def _calculate_urgency(self, prediction: Dict) -> float:
        """
        Calculate urgency score (0-100) for acting on a trend
        
        Higher urgency = should act sooner
        """
        base_score = prediction['confidence'] * prediction['trend_strength'] / 100
        
        # If peak is soon, increase urgency
        if prediction['peak_day']:
            days_to_peak = prediction['peak_day']
            if days_to_peak <= 3:
                peak_factor = 1.5
            elif days_to_peak <= 5:
                peak_factor = 1.2
            else:
                peak_factor = 1.0
        else:
            peak_factor = 1.1  # No clear peak = sustained trend
        
        urgency = base_score * peak_factor
        
        return min(100, round(urgency, 2))


# Initialize predictor (without DB for now, can be configured later)
# Can be configured with DATABASE_URL from environment
import os
from dotenv import load_dotenv
load_dotenv()

db_url = os.getenv('DATABASE_URL')
trend_predictor = TrendPredictionEngine(db_url=db_url, min_history_days=30)

# Export for use in other modules
__all__ = ['TrendPredictionEngine', 'TrendHistoryModel', 'trend_predictor']
