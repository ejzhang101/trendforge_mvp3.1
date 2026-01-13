"""
TrendForge Backend API - Main Entry Point
"""
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List, Dict, Optional
import uvicorn

import os
import urllib.parse
from dotenv import load_dotenv

from content_analyzer import (
    analyze_channel_deeply,
    content_analyzer,
    audience_analyzer
)
from social_trends_collector import SocialMediaAggregator
from topic_recommendation_engine import (
    recommendation_engine,
    title_engine
)

# Load environment variables
load_dotenv()

# Decode URL-encoded Twitter Bearer Token if needed
twitter_token = os.getenv('TWITTER_BEARER_TOKEN')
if twitter_token:
    # Decode URL encoding (e.g., %2F -> /, %3D -> =)
    twitter_token = urllib.parse.unquote(twitter_token)

# Initialize social media aggregator with API keys from environment
social_aggregator = SocialMediaAggregator(
    twitter_token=twitter_token,
    reddit_id=os.getenv('REDDIT_CLIENT_ID'),
    reddit_secret=os.getenv('REDDIT_CLIENT_SECRET')
)

app = FastAPI(
    title="TrendForge API",
    description="TrendForge Backend API - Enhanced YouTube Channel Analyzer",
    version="2.0.0"
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://127.0.0.1:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Request/Response Models
class VideoData(BaseModel):
    videoId: str
    title: str
    viewCount: Optional[int] = 0
    likeCount: Optional[int] = 0
    commentCount: Optional[int] = 0
    publishedAt: Optional[str] = None
    description: Optional[str] = ""

class ChannelData(BaseModel):
    subscriberCount: Optional[int] = 0
    title: Optional[str] = ""
    description: Optional[str] = ""

class ChannelAnalysisRequest(BaseModel):
    videos: List[VideoData]
    channel_data: ChannelData

class TopicsRequest(BaseModel):
    titles: List[str]

class VideoAnalysisRequest(BaseModel):
    video_id: str

class SocialTrendsRequest(BaseModel):
    keywords: List[str]
    geo: Optional[str] = 'US'

class RecommendationRequest(BaseModel):
    channel_analysis: Dict
    social_trends: List[Dict]
    max_recommendations: Optional[int] = 10

class TitleGenerationRequest(BaseModel):
    recommendation: Dict
    channel_analysis: Dict
    count: Optional[int] = 3

@app.get("/")
async def root():
    return {"message": "TrendForge API v2.0", "status": "running"}

@app.get("/health")
async def health():
    return {"status": "healthy"}

@app.post("/api/analyze/channel")
async def analyze_channel(request: ChannelAnalysisRequest):
    """
    Comprehensive channel analysis with deep content insights
    """
    try:
        # Convert Pydantic models to dicts
        videos = [video.dict() for video in request.videos]
        channel_data = request.channel_data.dict()
        
        # Perform analysis
        result = analyze_channel_deeply(videos, channel_data)
        
        return {
            "success": True,
            "data": result
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/analyze/topics")
async def extract_topics(request: TopicsRequest):
    """
    Extract topics from video titles using NLP
    """
    try:
        topics = content_analyzer.extract_topics_from_titles(request.titles)
        return {
            "success": True,
            "topics": topics,
            "count": len(topics)
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/analyze/video")
async def analyze_video(request: VideoAnalysisRequest):
    """
    Analyze individual video content from transcript
    """
    try:
        analysis = content_analyzer.analyze_video_content(request.video_id)
        return {
            "success": True,
            "data": analysis
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/analyze/high-performers")
async def analyze_high_performers(request: ChannelAnalysisRequest):
    """
    Analyze what makes high-performing videos successful
    """
    try:
        videos = [video.dict() for video in request.videos]
        result = content_analyzer.analyze_high_performing_videos(videos)
        return {
            "success": True,
            "data": result
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/analyze/content-style")
async def analyze_content_style(request: ChannelAnalysisRequest):
    """
    Identify the channel's content style and format
    """
    try:
        videos = [video.dict() for video in request.videos]
        result = content_analyzer.identify_content_style(videos)
        return {
            "success": True,
            "data": result
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/analyze/audience")
async def analyze_audience(request: ChannelAnalysisRequest):
    """
    Analyze target audience based on content and engagement
    """
    try:
        videos = [video.dict() for video in request.videos]
        channel_data = request.channel_data.dict()
        result = audience_analyzer.analyze_target_audience(videos, channel_data)
        return {
            "success": True,
            "data": result
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/trends/collect")
async def collect_social_trends(request: SocialTrendsRequest):
    """
    Collect trending topics from Twitter, Reddit, and Google Trends
    """
    try:
        result = await social_aggregator.collect_all_trends(
            keywords=request.keywords,
            geo=request.geo
        )
        return {
            "success": True,
            "data": result
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/recommendations/generate")
async def generate_recommendations(request: RecommendationRequest):
    """
    Generate personalized topic recommendations based on channel analysis and social trends
    """
    try:
        recommendations = recommendation_engine.generate_recommendations(
            channel_analysis=request.channel_analysis,
            social_trends=request.social_trends,
            max_recommendations=request.max_recommendations
        )
        return {
            "success": True,
            "recommendations": recommendations,
            "count": len(recommendations)
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/recommendations/titles")
async def generate_titles(request: TitleGenerationRequest):
    """
    Generate optimized video titles for a recommended topic
    """
    try:
        titles = title_engine.generate_titles(
            recommendation=request.recommendation,
            channel_analysis=request.channel_analysis,
            count=request.count
        )
        return {
            "success": True,
            "titles": titles,
            "count": len(titles)
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/recommendations/complete")
async def get_complete_recommendations(
    channel_request: ChannelAnalysisRequest,
    trends_request: SocialTrendsRequest,
    max_recommendations: Optional[int] = 10
):
    """
    Complete workflow: Analyze channel, collect trends, and generate recommendations
    """
    try:
        # Step 1: Analyze channel
        videos = [video.dict() for video in channel_request.videos]
        channel_data = channel_request.channel_data.dict()
        channel_analysis = analyze_channel_deeply(videos, channel_data)
        
        # Step 2: Collect social trends
        social_trends_result = await social_aggregator.collect_all_trends(
            keywords=trends_request.keywords,
            geo=trends_request.geo
        )
        social_trends = social_trends_result.get('merged_trends', [])
        
        # Step 3: Generate recommendations
        recommendations = recommendation_engine.generate_recommendations(
            channel_analysis=channel_analysis,
            social_trends=social_trends,
            max_recommendations=max_recommendations
        )
        
        # Step 4: Generate titles for top recommendations
        titles_for_recommendations = []
        for rec in recommendations[:3]:  # Top 3 recommendations
            titles = title_engine.generate_titles(
                recommendation=rec,
                channel_analysis=channel_analysis,
                count=3
            )
            titles_for_recommendations.append({
                'keyword': rec['keyword'],
                'titles': titles
            })
        
        return {
            "success": True,
            "channel_analysis": channel_analysis,
            "social_trends": social_trends_result,
            "recommendations": recommendations,
            "title_suggestions": titles_for_recommendations,
            "summary": {
                "total_recommendations": len(recommendations),
                "high_match_count": len([r for r in recommendations if r['match_score'] > 70]),
                "urgent_count": len([r for r in recommendations if r['urgency'] == 'urgent'])
            }
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    uvicorn.run(
        "main_v2:app",
        host="0.0.0.0",
        port=8000,
        reload=True
    )
