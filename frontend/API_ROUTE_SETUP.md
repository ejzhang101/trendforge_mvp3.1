# API Route Setup Guide

## 概述

`/app/api/analyze/route.ts` 是 MVP 2.0 的主要分析端点，它整合了：
1. YouTube 频道数据收集
2. 后端深度分析（NLP、社交媒体趋势）
3. 数据库存储

## 环境变量配置

在 `frontend/.env` 文件中添加以下环境变量：

```env
# Database
DATABASE_URL="postgresql://postgres:password@host:port/database"

# Backend Service
BACKEND_SERVICE_URL="http://localhost:8000"

# YouTube API
YOUTUBE_API_KEY="your_youtube_api_key_here"
```

### 获取 YouTube API Key

1. 访问 [Google Cloud Console](https://console.cloud.google.com/)
2. 创建新项目或选择现有项目
3. 启用 "YouTube Data API v3"
4. 创建凭据（API Key）
5. 将 API Key 添加到 `.env` 文件

## API 端点

### POST `/api/analyze`

分析 YouTube 频道并生成推荐

**请求体:**
```json
{
  "channelIdentifier": "UCxxxxxxxxxxxxx"  // Channel ID, username, or custom URL
}
```

**响应:**
```json
{
  "success": true,
  "channelId": "UCxxxxxxxxxxxxx",
  "channel": {
    "title": "Channel Name",
    "subscriberCount": 50000,
    "thumbnailUrl": "https://...",
    "description": "..."
  },
  "analysis": {
    "topics": [...],
    "contentStyle": {...},
    "targetAudience": {...},
    "highPerformers": {...},
    "videosAnalyzed": 50
  },
  "socialTrends": {
    "merged_trends": [...],
    "source_breakdown": {...}
  },
  "recommendations": [
    {
      "id": "...",
      "keyword": "AI",
      "matchScore": 85.5,
      "relevanceScore": 90.0,
      "opportunityScore": 82.0,
      "reasoning": "...",
      "contentAngle": "...",
      "urgency": "urgent",
      "predictedPerformance": {...},
      "suggestedFormat": "...",
      "suggestedTitles": [...],
      "sources": [...],
      "relatedInfo": {...}
    }
  ],
  "summary": {
    "total_recommendations": 10,
    "urgent_count": 2,
    "high_match_count": 5,
    "avg_match_score": 72.5
  }
}
```

## 工作流程

1. **接收请求** - 获取频道标识符
2. **YouTube API** - 使用 `analyzePublicChannel` 获取频道数据
3. **后端分析** - 调用 `/api/v2/full-analysis` 进行深度分析
4. **数据库存储** - 保存频道、趋势和推荐到数据库
5. **返回结果** - 返回完整的分析结果

## 数据库模型

### Channel
- 存储频道基本信息
- 包含 fingerprint（频道特征）
- 包含 v2_analysis（深度分析结果）

### TrendSnapshot
- 存储趋势快照
- 包含关键词、增长率、趋势分数等

### ChannelTrend
- 关联频道和趋势
- 包含匹配分数、推荐理由等

## 使用示例

### JavaScript/TypeScript
```typescript
const response = await fetch('/api/analyze', {
  method: 'POST',
  headers: { 'Content-Type': 'application/json' },
  body: JSON.stringify({
    channelIdentifier: 'UCxxxxxxxxxxxxx'
  })
});

const data = await response.json();
console.log(data.recommendations);
```

### cURL
```bash
curl -X POST http://localhost:3000/api/analyze \
  -H "Content-Type: application/json" \
  -d '{"channelIdentifier": "UCxxxxxxxxxxxxx"}'
```

## 错误处理

- **400** - 缺少频道标识符
- **404** - 频道未找到
- **500** - 分析失败（检查后端服务是否运行）

## 注意事项

1. **YouTube API 配额** - 每天有请求限制，注意使用频率
2. **后端服务** - 确保后端服务在 `BACKEND_SERVICE_URL` 运行
3. **数据库连接** - 确保 `DATABASE_URL` 正确配置
4. **性能** - 完整分析可能需要 30-60 秒，建议添加加载状态

## 调试

查看服务器日志以了解分析进度：
- `🔍 Starting MVP 2.0 analysis for: ...`
- `✅ Channel data collected: ...`
- `🌐 Calling enhanced backend...`
- `✅ Backend analysis complete`
- `💾 Saving to database...`
- `✅ Data saved successfully`
