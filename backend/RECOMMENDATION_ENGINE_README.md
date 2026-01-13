# 智能主题推荐引擎

## 功能概述

智能主题推荐引擎结合频道分析和社会媒体趋势，为内容创作者生成个性化的主题推荐。

## 核心功能

1. **个性化推荐** - 基于频道特征匹配热门话题
2. **标题生成** - 为推荐主题生成优化的视频标题
3. **性能预测** - 预测视频的潜在表现
4. **完整工作流** - 一站式分析、收集和推荐

## API 端点

### 1. POST `/api/recommendations/generate`

生成个性化主题推荐

**请求体:**
```json
{
  "channel_analysis": {
    "topics": [{"topic": "AI", "score": 0.9}],
    "content_style": {"primary_style": "tutorial"},
    "target_audience": {"primary_age_group": "young_adults"},
    "high_performers": {"avg_title_length": 60}
  },
  "social_trends": [
    {
      "keyword": "AI",
      "composite_score": 85,
      "growth_rate": 120,
      "sources": ["twitter", "reddit", "google_trends"]
    }
  ],
  "max_recommendations": 10
}
```

**响应:**
```json
{
  "success": true,
  "recommendations": [
    {
      "keyword": "AI",
      "match_score": 85.5,
      "relevance_score": 90.0,
      "opportunity_score": 82.0,
      "composite_social_score": 85,
      "reasoning": "'AI' 高度匹配您的频道核心主题；当前社交媒体讨论热度极高；在3个平台同时热门；搜索量增长120%，趋势强劲",
      "content_angle": "🔥 热点！制作 'AI' 完整教程，分步讲解（建议48小时内发布）",
      "predicted_performance": {
        "tier": "excellent",
        "predicted_views": 20000,
        "description": "预计表现优异，可能成为爆款",
        "confidence": 84
      },
      "suggested_format": "8-12分钟教程，分步演示",
      "urgency": "urgent",
      "sources": ["twitter", "reddit", "google_trends"],
      "related_info": {
        "rising_queries": ["AI trends", "machine learning"],
        "hashtags": ["#AI", "#ArtificialIntelligence"],
        "subreddits": ["technology", "MachineLearning"]
      }
    }
  ],
  "count": 1
}
```

### 2. POST `/api/recommendations/titles`

为推荐主题生成优化的视频标题

**请求体:**
```json
{
  "recommendation": {
    "keyword": "AI",
    "urgency": "urgent",
    "content_angle": "制作 'AI' 完整教程"
  },
  "channel_analysis": {
    "high_performers": {
      "avg_title_length": 60
    }
  },
  "count": 3
}
```

**响应:**
```json
{
  "success": true,
  "titles": [
    {
      "title": "🔥 爆火！5个关于AI的必知技巧",
      "strategy": "number_list",
      "predicted_ctr": 8.5,
      "reasoning": "数字列表式标题，通常有较高点击率",
      "character_count": 18
    },
    {
      "title": "AI真的值得吗？完整分析",
      "strategy": "question",
      "predicted_ctr": 7.2,
      "reasoning": "问题式标题，激发好奇心",
      "character_count": 13
    },
    {
      "title": "🔥 爆火！AI：99%的人都不知道的秘密",
      "strategy": "emotional",
      "predicted_ctr": 9.1,
      "reasoning": "情感化标题，易引发共鸣和分享",
      "character_count": 22
    }
  ],
  "count": 3
}
```

### 3. POST `/api/recommendations/complete`

完整工作流：分析频道 → 收集趋势 → 生成推荐 → 生成标题

**请求体:**
```json
{
  "channel_request": {
    "videos": [
      {
        "videoId": "abc123",
        "title": "How to use AI",
        "viewCount": 10000,
        "likeCount": 500,
        "commentCount": 100
      }
    ],
    "channel_data": {
      "subscriberCount": 50000,
      "title": "Tech Channel"
    }
  },
  "trends_request": {
    "keywords": ["AI", "technology"],
    "geo": "US"
  },
  "max_recommendations": 10
}
```

**响应:**
包含完整的频道分析、社会趋势、推荐和标题建议。

## 推荐评分系统

### Match Score (匹配分数)
综合评分，基于：
- **主题相关性 (40%)** - 与频道现有主题的匹配度
- **风格兼容性 (20%)** - 与内容风格的匹配度
- **受众匹配 (20%)** - 与目标受众的匹配度
- **机会分数 (20%)** - 基于社交媒体参与度和增长

### 推荐等级
- **Excellent (>80)** - 预计表现优异，可能成为爆款
- **Good (65-80)** - 预计表现良好，高于平均水平
- **Moderate (50-65)** - 预计表现中等，稳定流量
- **Low (<50)** - 预计表现一般，可作为尝试

### 紧急程度
- **urgent** - 48小时内发布
- **high** - 本周内发布
- **medium** - 两周内发布
- **low** - 灵活安排

## 标题策略

1. **数字列表式** - 高点击率，如 "5个关于AI的必知技巧"
2. **问题式** - 激发好奇心，如 "AI真的值得吗？"
3. **情感化** - 易引发共鸣，如 "🔥 爆火！AI：99%的人都不知道的秘密"
4. **权威式** - 适合专业内容，如 "AI深度评测：专业视角"

## 使用示例

### Python
```python
import requests

# 生成推荐
response = requests.post(
    "http://localhost:8000/api/recommendations/generate",
    json={
        "channel_analysis": {...},
        "social_trends": [...],
        "max_recommendations": 10
    }
)

recommendations = response.json()["recommendations"]
```

### cURL
```bash
curl -X POST http://localhost:8000/api/recommendations/complete \
  -H "Content-Type: application/json" \
  -d '{
    "channel_request": {
      "videos": [...],
      "channel_data": {...}
    },
    "trends_request": {
      "keywords": ["AI", "technology"],
      "geo": "US"
    }
  }'
```

## 工作流程

1. **分析频道** - 使用 `/api/analyze/channel` 分析频道特征
2. **收集趋势** - 使用 `/api/trends/collect` 收集社交媒体趋势
3. **生成推荐** - 使用 `/api/recommendations/generate` 生成个性化推荐
4. **生成标题** - 使用 `/api/recommendations/titles` 为推荐生成标题
5. **或使用完整流程** - 使用 `/api/recommendations/complete` 一次性完成所有步骤

## 注意事项

- 推荐引擎需要有效的频道分析数据和社会趋势数据
- 匹配分数低于 30 的主题不会被推荐
- 标题长度会自动调整以匹配频道的成功模式
- 性能预测基于频道的历史表现数据
