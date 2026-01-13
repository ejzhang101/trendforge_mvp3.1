# 社交媒体趋势收集器

## 功能概述

社交媒体趋势收集器可以从 Twitter、Reddit 和 Google Trends 收集热门话题，并聚合分析。

## API 端点

### POST `/api/trends/collect`

收集来自所有社交媒体源的 trending topics。

**请求体:**
```json
{
  "keywords": ["AI", "technology", "programming"],
  "geo": "US"
}
```

**响应:**
```json
{
  "success": true,
  "data": {
    "merged_trends": [
      {
        "keyword": "AI",
        "twitter_score": 85.16,
        "reddit_score": 83.90,
        "google_score": 32.98,
        "composite_score": 78.91,
        "sources": ["twitter", "reddit", "google_trends"],
        "source_count": 3,
        "twitter_hashtags": ["#AI", "#ArtificialIntelligence"],
        "reddit_subreddits": ["technology", "MachineLearning"],
        "growth_rate": 20.97,
        "rising_queries": ["AI trends", "machine learning"]
      }
    ],
    "by_source": {
      "twitter": [...],
      "reddit": [...],
      "google_trends": [...]
    },
    "collected_at": "2024-01-10T12:00:00"
  }
}
```

## 数据源

### 1. Twitter/X
- 搜索相关推文
- 计算参与度分数（点赞、转发、回复）
- 提取相关标签
- **需要**: `TWITTER_BEARER_TOKEN` (可选，未配置时使用模拟数据)

### 2. Reddit
- 搜索热门帖子
- 分析点赞数和评论数
- 识别热门 subreddits
- **需要**: `REDDIT_CLIENT_ID` 和 `REDDIT_CLIENT_SECRET` (可选，未配置时使用模拟数据)

### 3. Google Trends
- 获取搜索趋势数据
- 计算增长率
- 提取相关查询
- **无需 API keys**

## 配置 API Keys

请参考 `API_KEYS_SETUP.md` 文件了解如何配置 API keys。

### 快速配置

在 `backend/.env` 文件中添加：

```env
TWITTER_BEARER_TOKEN=your_twitter_bearer_token_here
REDDIT_CLIENT_ID=your_reddit_client_id_here
REDDIT_CLIENT_SECRET=your_reddit_client_secret_here
```

## 使用示例

### Python
```python
import requests

response = requests.post(
    "http://localhost:8000/api/trends/collect",
    json={
        "keywords": ["AI", "technology"],
        "geo": "US"
    }
)

data = response.json()
print(data["data"]["merged_trends"])
```

### cURL
```bash
curl -X POST http://localhost:8000/api/trends/collect \
  -H "Content-Type: application/json" \
  -d '{
    "keywords": ["AI", "technology", "programming"],
    "geo": "US"
  }'
```

## 评分系统

### Composite Score (综合分数)
- Twitter: 30% 权重
- Reddit: 30% 权重
- Google Trends: 40% 权重
- 多源加成: 每个额外来源 +5 分

### 趋势排名
趋势按 composite_score 降序排列，分数越高表示越热门。

## 注意事项

1. **Rate Limiting**: 各 API 都有速率限制，系统已内置延迟以避免超限
2. **模拟数据**: 如果未配置 API keys，系统会使用模拟数据，适合测试
3. **异步处理**: 所有数据收集都是异步并行进行的，提高效率
4. **错误处理**: 如果某个数据源失败，其他源仍会正常工作

## 依赖项

- `tweepy>=4.14.0` - Twitter API
- `praw>=7.7.0` - Reddit API
- `pytrends>=4.9.0` - Google Trends

所有依赖已包含在 `requirements_v2.txt` 中。
