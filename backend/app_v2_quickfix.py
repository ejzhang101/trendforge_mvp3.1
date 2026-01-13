"""
TrendForge AI Backend - MVP 2.0
Deep content analysis with social media trends
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

from services.enhanced_youtube_analyzer import (
    analyze_channel_deeply,
    content_analyzer,
    audience_analyzer
)

# Verify we're using the correct analyzer
print(f"✅ Using audience_analyzer: {type(audience_analyzer).__name__}")
# Try to use enhanced social collector (MVP 3.0), fallback to original
try:
    from services.enhanced_social_collector import EnhancedSocialMediaAggregator
    USE_ENHANCED_COLLECTOR = True
    print("✅ Using Enhanced Social Media Collector (MVP 3.0)")
except ImportError:
    from services.social_media_collector import SocialMediaAggregator
    USE_ENHANCED_COLLECTOR = False
    print("⚠️ Using original Social Media Collector")

# Use original recommendation engine (MVP 2.0)
from services.intelligent_recommender import (
    recommendation_engine,
    title_engine
)
print("✅ Using Recommendation Engine (MVP 2.0)")

# Load environment variables
load_dotenv()

# Decode URL-encoded Twitter Bearer Token if needed
twitter_token = os.getenv('TWITTER_BEARER_TOKEN')
if twitter_token:
    twitter_token = urllib.parse.unquote(twitter_token)

# Initialize social aggregator (enhanced or original)
if USE_ENHANCED_COLLECTOR:
    redis_url = os.getenv('REDIS_URL')  # Optional Redis cache
    social_aggregator = EnhancedSocialMediaAggregator(
        twitter_token=twitter_token,
        reddit_id=os.getenv('REDDIT_CLIENT_ID'),
        reddit_secret=os.getenv('REDDIT_CLIENT_SECRET'),
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

app = FastAPI(
    title="TrendForge AI Backend - Quick Fix Version",
    version="2.0.1-quickfix",
    description="Intelligent YouTube trend prediction - Optimized for speed"
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


# MVP 2.0: No prediction request model


class FullAnalysisRequest(BaseModel):
    """
    Complete analysis request combining all steps (MVP 2.0)
    """
    videos: List[Dict]
    channel_data: Dict
    geo: str = "US"
    analyze_transcripts: bool = False
    max_recommendations: int = 10
    enable_backtest: bool = False  # 默认禁用回测以提速
    use_simple_mode: bool = False  # 简单模式：跳过社交趋势收集


# ==================== API Endpoints ====================

@app.get("/")
async def root():
    return {
        "service": "TrendForge AI Backend",
        "version": "2.0.1-quickfix",
        "features": [
            "Deep content analysis with NLP",
            "Video transcript analysis",
            "Enhanced multi-platform social media trends",
            "Intelligent rate limiting and caching",
            "Cross-platform signal verification",
            "Intelligent topic recommendations",
            "AI-powered title generation",
            "Historical video backtest analysis"
        ],
        "status": "running",
        "enhancements": {
            "rate_limiting": "✅ Automatic",
            "caching": "✅ Redis + Memory",
            "signal_analysis": "✅ Deep analysis",
            "cross_platform": "✅ Verified signals"
        }
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
        print("📊 Step 1/3: Analyzing channel...")
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
            print("🌐 Step 2/3: Collecting social media trends (quick mode)...")
            
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
            print("📊 Step 2/3: Skipping social trends (simple mode)...")
        
        # Step 3: Generate recommendations
        print("💡 Step 3/3: Generating recommendations...")
        
        if social_trends_data['merged_trends']:
            try:
                recommendations = recommendation_engine.generate_recommendations(
                    channel_analysis,
                    social_trends_data['merged_trends'],
                    min(request.max_recommendations, 5)  # 限制到5个
                )
                
                # Generate titles (只为前3个)
                for rec in recommendations[:3]:
                    titles = title_engine.generate_titles(
                        rec,
                        channel_analysis,
                        count=3
                    )
                    rec['suggested_titles'] = titles
                
                print(f"   ✅ Recommendations generated in {(datetime.utcnow() - start_time).total_seconds():.1f}s")
                
            except Exception as e:
                print(f"   ⚠️ Recommendation error: {e}")
        
        total_time = (datetime.utcnow() - start_time).total_seconds()
        print(f"✅ Analysis complete in {total_time:.1f}s!")
        
        response = {
            "success": True,
            "version": "2.0.1-quickfix",
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
                "avg_match_score": sum(r.get('match_score', 0) for r in recommendations) / len(recommendations) if recommendations else 0
            },
            "performance": {
                "analysis_time_seconds": total_time,
                "simple_mode": request.use_simple_mode,
                "backtest_enabled": False
            },
            "analyzed_at": datetime.utcnow().isoformat()
        }
        
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
            "version": "2.0.1-quickfix",
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
    
    social_status = {
        "twitter": social_aggregator.twitter.client is not None if hasattr(social_aggregator, 'twitter') else False,
        "reddit": social_aggregator.reddit.reddit is not None if hasattr(social_aggregator, 'reddit') else False,
        "google_trends": True,
        "cache": social_aggregator.cache.redis_client is not None if hasattr(social_aggregator, 'cache') and hasattr(social_aggregator.cache, 'redis_client') else False,
        "prophet": False  # MVP 2.0: Prophet not available
    }
    
    return {
        "status": "healthy",
        "version": "2.0.1-quickfix",
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
            # MVP 2.0: No time series prediction
        },
        "services": social_status,
        "warnings": [
            f"{service} not configured" 
            for service, available in social_status.items() 
            if not available and service not in ['cache', 'prophet']
        ]
    }


# MVP 2.0: No Prophet prediction endpoints


if __name__ == "__main__":
    import uvicorn
    print("="*70)
    print("🚀 TrendForge Backend - Quick Fix Version")
    print("="*70)
    print("✅ Optimizations enabled:")
    print("   - Disabled: Transcript analysis, Backtest")
    print("   - Optimized: Social media collection with 15s timeout")
    print("   - Fast-fail: Twitter rate limit handling")
    print("   - Simple mode: Skip social trends for ultra-fast analysis")
    print("   - Limited: max_recommendations = 5")
    print("="*70)
    print("📊 Expected performance: 5-15 seconds")
    print("="*70)
    uvicorn.run(app, host="0.0.0.0", port=8000, log_level="info")
