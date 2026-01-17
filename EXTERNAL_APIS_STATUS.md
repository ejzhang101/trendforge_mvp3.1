# 外部 API 调用状态 - MVP 3.1

## 概述

TrendForge 后端和前端会调用多个外部 API 来收集社交媒体趋势数据和生成内容。本文档说明哪些 API 被调用，以及它们的配置状态。

## 后端 API 调用

### 1. Twitter API (Twitter/X)

**用途**：收集 Twitter 上的热门话题和讨论

**库**：`tweepy`

**环境变量**：
- `TWITTER_BEARER_TOKEN` - Twitter Bearer Token

**调用位置**：
- `backend/services/enhanced_social_collector.py` - `EnhancedTwitterCollector`
- `backend/services/social_media_collector.py` - `TwitterTrendCollector`

**功能**：
- 搜索关键词相关的推文
- 分析推文参与度（点赞、转发、回复）
- 提取相关标签（hashtags）
- 计算趋势分数

**状态检查**：
```python
# 在 backend/app_v2.py 中
twitter_token = os.getenv('TWITTER_BEARER_TOKEN')
# 如果未设置，Twitter 收集器会返回空数据
```

**Fallback**：如果 Twitter API 不可用或超时，会跳过并继续使用其他数据源

---

### 2. Reddit API

**用途**：收集 Reddit 上的热门讨论和子版块

**库**：`praw` (Python Reddit API Wrapper)

**环境变量**：
- `REDDIT_CLIENT_ID` - Reddit Client ID
- `REDDIT_CLIENT_SECRET` - Reddit Client Secret

**调用位置**：
- `backend/services/enhanced_social_collector.py` - `EnhancedRedditCollector`
- `backend/services/social_media_collector.py` - `RedditTrendCollector`

**功能**：
- 搜索关键词相关的帖子
- 分析帖子参与度（点赞、评论）
- 识别相关子版块（subreddits）
- 计算趋势分数

**状态检查**：
```python
# 在 backend/app_v2.py 中
reddit_id = os.getenv('REDDIT_CLIENT_ID')
reddit_secret = os.getenv('REDDIT_CLIENT_SECRET')
# 如果未设置，Reddit 收集器会返回空数据
```

**Fallback**：如果 Reddit API 不可用或超时，会跳过并继续使用其他数据源

---

### 3. Google Trends API

**用途**：收集 Google 搜索趋势数据

**库**：`pytrends`

**环境变量**：**无需 API Key**（使用公开的 Google Trends 数据）

**调用位置**：
- `backend/services/enhanced_social_collector.py` - `EnhancedGoogleTrendsCollector`
- `backend/services/social_media_collector.py` - `GoogleTrendsEnhancedCollector`

**功能**：
- 获取关键词的搜索兴趣度（Interest Over Time）
- 计算增长率（Growth Rate）
- 识别相关查询（Related Queries）
- 计算趋势分数

**限制**：
- Google Trends 有速率限制（建议每个关键词间隔 1-2 秒）
- 可能返回空数据（如果关键词太新或太冷门）

**Fallback**：如果 Google Trends 超时或失败，会跳过并继续使用其他数据源

---

### 4. SerpAPI

**用途**：作为 Google Trends 的替代/补充数据源

**库**：`google-search-results`

**环境变量**：
- `SERPAPI_KEY` - SerpAPI API Key

**调用位置**：
- `backend/services/enhanced_social_collector.py` - `EnhancedSerpAPICollector`

**功能**：
- 搜索关键词的 Google 搜索结果
- 获取搜索量数据
- 识别相关查询
- 作为 Google Trends 的备用数据源

**状态检查**：
```python
# 在 backend/app_v2.py 中
serpapi_key = os.getenv('SERPAPI_KEY')
# 如果未设置，SerpAPI 收集器会返回空数据
```

**Fallback**：如果 SerpAPI 不可用或超时，会跳过并继续使用其他数据源

---

### 5. OpenAI API

**用途**：AI 脚本生成（语义分析和智能脚本生成）

**库**：`openai`

**环境变量**：
- `OPENAI_API_KEY` - OpenAI API Key

**调用位置**：
- `backend/services/script_generator.py` - `ScriptGeneratorEngine`

**功能**：
- 语义分析用户输入的 prompt（中英文）
- 生成视频脚本内容
- 提取产品/服务信息

**状态检查**：
```python
# 在 backend/services/script_generator.py 中
OPENAI_API_KEY = os.getenv('OPENAI_API_KEY')
OPENAI_AVAILABLE = bool(OPENAI_API_KEY)
# 如果未设置，会使用模板生成脚本（fallback）
```

**Fallback**：如果 OpenAI API 不可用，会使用模板生成脚本

---

## 前端 API 调用

### 6. YouTube Data API v3

**用途**：获取 YouTube 频道和视频数据

**库**：`googleapis` (Node.js)

**环境变量**：
- `YOUTUBE_API_KEY` - YouTube Data API Key

**调用位置**：
- `frontend/lib/youtube-public.ts` - `analyzePublicChannel`

**功能**：
- 解析频道 ID（支持用户名、自定义 URL）
- 获取频道详情（标题、描述、订阅数等）
- 获取视频列表（最多 50 个）
- 获取视频统计数据（播放量、点赞、评论等）

**状态检查**：
```typescript
// 在 frontend/lib/youtube-public.ts 中
const youtube = google.youtube({
  version: 'v3',
  auth: process.env.YOUTUBE_API_KEY,
});
```

**Fallback**：如果 YouTube API 失败，会返回错误，前端显示错误信息

---

## API 调用流程

### 完整分析流程

```
1. 前端调用 YouTube API
   ↓
2. 获取频道和视频数据
   ↓
3. 后端分析频道内容（NLTK，无需外部 API）
   ↓
4. 后端并行调用社交媒体 API（15秒超时）
   ├─ Twitter API
   ├─ Reddit API
   ├─ Google Trends
   └─ SerpAPI（可选）
   ↓
5. 聚合所有数据源
   ↓
6. 生成推荐（使用聚合数据）
   ↓
7. Prophet 预测（无需外部 API）
   ↓
8. 返回结果
```

### 简化模式（无社交媒体数据）

```
1. 前端调用 YouTube API
   ↓
2. 获取频道和视频数据
   ↓
3. 后端分析频道内容（NLTK）
   ↓
4. 跳过社交媒体 API（use_simple_mode=true 或超时）
   ↓
5. 基于频道主题生成模拟社交趋势数据
   ↓
6. 生成推荐（使用模拟数据）
   ↓
7. Prophet 预测（可选）
   ↓
8. 返回结果
```

---

## 当前配置状态

### Railway 后端环境变量

检查以下环境变量是否已设置：

```bash
# 社交媒体 API
TWITTER_BEARER_TOKEN=你的Twitter_Bearer_Token
REDDIT_CLIENT_ID=你的Reddit_Client_ID
REDDIT_CLIENT_SECRET=你的Reddit_Client_Secret
SERPAPI_KEY=你的SerpAPI_Key

# AI 服务
OPENAI_API_KEY=你的OpenAI_API_Key

# 数据库和缓存
DATABASE_URL=你的PostgreSQL_URL
REDIS_URL=你的Redis_URL
```

### Vercel 前端环境变量

检查以下环境变量是否已设置：

```bash
# 后端服务
BACKEND_SERVICE_URL=https://你的-railway-后端-url.up.railway.app

# YouTube API
YOUTUBE_API_KEY=你的YouTube_API_Key

# 数据库
DATABASE_URL=你的PostgreSQL_URL
```

---

## API 调用状态检查

### 后端健康检查端点

访问：`https://你的-railway-后端-url.up.railway.app/health`

应该看到：
```json
{
  "status": "healthy",
  "version": "3.1.0",
  "features": {
    "prophet": true,
    "script_generator": true
  },
  "api_status": {
    "twitter": true/false,  // 取决于 TWITTER_BEARER_TOKEN 是否设置
    "reddit": true/false,   // 取决于 REDDIT_CLIENT_ID/SECRET 是否设置
    "google_trends": true,  // 总是 true（无需 API Key）
    "serpapi": true/false  // 取决于 SERPAPI_KEY 是否设置
  }
}
```

---

## 数据准确性说明

### 有真实社交媒体数据时

- ✅ **互联网热度**：基于真实的 Twitter + Reddit + Google Trends 数据
- ✅ **匹配度**：基于真实趋势数据和频道分析
- ✅ **预测观看数**：基于真实热度数据

### 无真实社交媒体数据时（使用模拟数据）

- ⚠️ **互联网热度**：基于频道主题分数和频道表现（模拟）
- ⚠️ **匹配度**：基于频道分析（仍然准确）
- ⚠️ **预测观看数**：基于频道表现和主题相关性（仍然合理）

**注意**：即使没有社交媒体数据，系统仍然可以生成合理的推荐，只是互联网热度分数可能不如真实数据准确。

---

## 速率限制和超时

### 超时设置

- **Twitter API**：15秒超时
- **Reddit API**：15秒超时
- **Google Trends**：15秒超时
- **SerpAPI**：15秒超时
- **总体超时**：如果所有社交媒体 API 都超时，会使用模拟数据

### 速率限制处理

- **Twitter**：自动检测速率限制，快速失败（不等待）
- **Reddit**：自动检测速率限制，快速失败
- **Google Trends**：自动间隔请求，避免速率限制
- **缓存**：使用 Redis 缓存（1小时），减少 API 调用

---

## 如何配置 API Keys

### 1. Twitter Bearer Token

1. 访问 [Twitter Developer Portal](https://developer.twitter.com/)
2. 创建应用并获取 Bearer Token
3. 在 Railway 环境变量中添加：`TWITTER_BEARER_TOKEN`

### 2. Reddit API

1. 访问 [Reddit Apps](https://www.reddit.com/prefs/apps)
2. 创建应用，获取 Client ID 和 Client Secret
3. 在 Railway 环境变量中添加：
   - `REDDIT_CLIENT_ID`
   - `REDDIT_CLIENT_SECRET`

### 3. SerpAPI

1. 访问 [SerpAPI](https://serpapi.com/)
2. 注册并获取 API Key
3. 在 Railway 环境变量中添加：`SERPAPI_KEY`

### 4. OpenAI API

1. 访问 [OpenAI Platform](https://platform.openai.com/)
2. 创建 API Key
3. 在 Railway 环境变量中添加：`OPENAI_API_KEY`

### 5. YouTube API

1. 访问 [Google Cloud Console](https://console.cloud.google.com/)
2. 启用 YouTube Data API v3
3. 创建 API Key
4. 在 Vercel 环境变量中添加：`YOUTUBE_API_KEY`

---

## 总结

**调用的外部 API**：
1. ✅ **Twitter API** - 需要 `TWITTER_BEARER_TOKEN`
2. ✅ **Reddit API** - 需要 `REDDIT_CLIENT_ID` 和 `REDDIT_CLIENT_SECRET`
3. ✅ **Google Trends** - 无需 API Key（公开数据）
4. ✅ **SerpAPI** - 需要 `SERPAPI_KEY`（可选）
5. ✅ **OpenAI API** - 需要 `OPENAI_API_KEY`（用于脚本生成）
6. ✅ **YouTube Data API** - 需要 `YOUTUBE_API_KEY`（前端）

**Fallback 机制**：
- 如果社交媒体 API 不可用或超时，会使用基于频道分析的模拟数据
- 如果 OpenAI API 不可用，会使用模板生成脚本
- 所有 API 都有超时保护（15秒），不会阻塞整个分析流程

**数据准确性**：
- 有真实社交媒体数据时：所有指标都基于真实数据，准确性高
- 无真实社交媒体数据时：使用模拟数据，仍然可以生成合理的推荐

---

**更新日期**：2026-01-14
