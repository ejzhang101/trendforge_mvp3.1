# TrendForge AI Backend - MVP 2.0 API 文档

## 概述

TrendForge AI Backend MVP 2.0 是一个智能 YouTube 趋势预测系统，集成了深度内容分析、社交媒体趋势收集和智能推荐功能。

## 架构

```
backend/
├── app_v2.py                    # 主应用文件
├── services/                    # 服务模块
│   ├── __init__.py
│   ├── enhanced_youtube_analyzer.py    # YouTube 频道分析
│   ├── social_media_collector.py       # 社交媒体趋势收集
│   └── intelligent_recommender.py      # 智能推荐引擎
└── .env                         # 环境变量配置
```

## 启动应用

```bash
cd backend
source venv/bin/activate
python app_v2.py
```

应用将在 http://localhost:8000 启动

## API 端点

### 1. GET `/`
获取服务信息和功能列表

**响应:**
```json
{
  "service": "TrendForge AI Backend",
  "version": "2.0.0",
  "features": [
    "Deep content analysis with NLP",
    "Video transcript analysis",
    "Multi-platform social media trends",
    "Intelligent topic recommendations",
    "AI-powered title generation"
  ],
  "status": "running"
}
```

### 2. GET `/health`
健康检查端点

**响应:**
```json
{
  "status": "healthy",
  "version": "2.0.0",
  "timestamp": "2026-01-11T00:18:04.447905",
  "capabilities": {
    "nlp_analysis": true,
    "transcript_analysis": true,
    "social_media": true,
    "intelligent_recommendations": true,
    "title_generation": true
  }
}
```

### 3. POST `/api/v2/analyze-channel`
深度频道分析

**请求体:**
```json
{
  "videos": [
    {
      "videoId": "abc123",
      "title": "Video Title",
      "viewCount": 10000,
      "likeCount": 500,
      "commentCount": 100,
      "publishedAt": "2024-01-01T00:00:00Z",
      "description": "Video description"
    }
  ],
  "channel_data": {
    "subscriberCount": 50000,
    "title": "Channel Name",
    "description": "Channel description"
  },
  "analyze_transcripts": false
}
```

**响应:**
包含主题提取、内容风格、目标受众、高表现视频分析等。

### 4. POST `/api/v2/collect-social-trends`
收集社交媒体趋势

**请求体:**
```json
{
  "keywords": ["AI", "technology"],
  "geo": "US",
  "channel_context": {}
}
```

**响应:**
包含合并的趋势、按来源分类的数据等。

### 5. POST `/api/v2/generate-recommendations`
生成智能推荐

**请求体:**
```json
{
  "channel_analysis": {...},
  "keywords": ["AI", "technology"],
  "geo": "US",
  "max_recommendations": 10
}
```

**响应:**
包含个性化推荐和标题建议。

### 6. POST `/api/v2/generate-titles`
生成优化的视频标题

**请求体:**
```json
{
  "recommendation": {...},
  "channel_analysis": {...},
  "count": 3
}
```

### 7. POST `/api/v2/full-analysis` ⭐
**完整分析管道（推荐使用）**

一次性完成所有步骤：
1. 深度频道分析
2. 社交媒体趋势收集
3. 智能推荐生成
4. 标题生成

**请求体:**
```json
{
  "videos": [...],
  "channel_data": {...},
  "geo": "US",
  "analyze_transcripts": false,
  "max_recommendations": 10
}
```

**响应:**
```json
{
  "success": true,
  "channel_analysis": {
    "topics": [...],
    "content_style": {...},
    "target_audience": {...},
    "high_performers": {...},
    "total_videos_analyzed": 50
  },
  "social_trends": {
    "merged_trends": [...],
    "source_breakdown": {
      "twitter_count": 5,
      "reddit_count": 5,
      "google_trends_count": 10
    }
  },
  "recommendations": [
    {
      "keyword": "AI",
      "match_score": 85.5,
      "relevance_score": 90.0,
      "opportunity_score": 82.0,
      "reasoning": "...",
      "content_angle": "...",
      "predicted_performance": {...},
      "suggested_format": "...",
      "urgency": "urgent",
      "suggested_titles": [...]
    }
  ],
  "summary": {
    "total_recommendations": 10,
    "urgent_count": 2,
    "high_match_count": 5,
    "avg_match_score": 72.5
  },
  "analyzed_at": "2026-01-11T00:18:04.447905"
}
```

## 使用示例

### Python
```python
import requests

# 完整分析
response = requests.post(
    "http://localhost:8000/api/v2/full-analysis",
    json={
        "videos": [...],
        "channel_data": {...},
        "geo": "US",
        "max_recommendations": 10
    }
)

result = response.json()
recommendations = result["recommendations"]
```

### cURL
```bash
curl -X POST http://localhost:8000/api/v2/full-analysis \
  -H "Content-Type: application/json" \
  -d '{
    "videos": [...],
    "channel_data": {...},
    "geo": "US",
    "max_recommendations": 10
  }'
```

## 环境变量配置

在 `backend/.env` 文件中配置：

```env
# Twitter API (X API)
TWITTER_BEARER_TOKEN=your_token_here

# Reddit API
REDDIT_CLIENT_ID=your_client_id
REDDIT_CLIENT_SECRET=your_client_secret
```

## API 文档

访问 http://localhost:8000/docs 查看完整的 Swagger API 文档。

## 功能特性

- ✅ 深度内容分析（NLP 增强）
- ✅ 视频字幕分析
- ✅ 多平台社交媒体趋势（Twitter, Reddit, Google Trends）
- ✅ 智能主题推荐
- ✅ AI 驱动的标题生成
- ✅ 性能预测
- ✅ 紧急程度判断

## 注意事项

1. **完整分析管道** (`/api/v2/full-analysis`) 是最推荐的端点，一次性完成所有分析
2. 字幕分析是资源密集型的，建议只在需要时启用
3. Twitter API 有速率限制，系统会自动处理
4. 如果没有配置 API keys，系统会使用模拟数据
