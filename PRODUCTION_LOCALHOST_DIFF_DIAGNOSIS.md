# 生产环境与 Localhost 差异诊断 - MVP 3.1

## 问题描述

部署上线后的 3.1 版本与 localhost 呈现巨大差异：
- ❌ 功能呈现不一致
- ❌ 信息字段缺失或错误
- ❌ 数据值不准确

## 可能原因分析

### 1. 环境变量配置差异

**检查项**：
- `BACKEND_SERVICE_URL` 是否正确指向生产后端
- `YOUTUBE_API_KEY` 是否配置
- `DATABASE_URL` 是否指向正确的数据库
- 后端环境变量（Twitter, Reddit, SerpAPI, OpenAI）是否配置

### 2. 数据库缓存问题

**问题**：生产环境可能使用了旧的缓存数据（MVP 2.0 格式）

**症状**：
- 数据格式不匹配
- 字段缺失
- 版本号不一致

### 3. 前端/后端版本不一致

**问题**：前端可能缓存了旧版本，或后端未正确部署

**检查**：
- 前端构建时间
- 后端版本号（`/health` 端点）
- Git 提交记录

### 4. API 调用失败导致 Fallback

**问题**：生产环境的 API 调用可能失败，导致使用模拟数据

**症状**：
- 互联网热度固定为 50
- 预测观看数不准确
- 7天趋势预测缺失

## 诊断步骤

### 步骤 1: 检查后端健康状态

访问：`https://你的-railway-后端-url.up.railway.app/health`

**期望响应**：
```json
{
  "status": "healthy",
  "version": "3.1.0",
  "capabilities": {
    "time_series_prediction": true,
    "script_generation": true,
    "youtube_data_collection": true
  },
  "services": {
    "twitter": true/false,
    "reddit": false,
    "google_trends": true,
    "serpapi": true/false,
    "youtube": true/false,
    "prophet": true,
    "script_generator": true
  }
}
```

**如果版本不是 3.1.0**：
- 后端未正确部署
- 需要重新部署后端

### 步骤 2: 检查前端环境变量

在 Vercel Dashboard 中验证：

```bash
BACKEND_SERVICE_URL=https://你的-railway-后端-url.up.railway.app
YOUTUBE_API_KEY=你的YouTube_API_Key
DATABASE_URL=你的PostgreSQL_URL
```

**重要**：
- `BACKEND_SERVICE_URL` 必须包含 `https://`
- 确保所有环境变量都已设置

### 步骤 3: 检查数据库缓存

**问题**：生产数据库可能包含旧格式的数据

**解决方案**：
1. 清除特定频道的分析记录
2. 重新分析频道
3. 验证新数据格式

### 步骤 4: 检查 API 调用日志

**后端日志**（Railway Dashboard）：
- 查看是否有 API 调用失败
- 检查是否使用了模拟数据
- 确认 Prophet 预测是否执行

**前端日志**（浏览器控制台）：
- 检查 API 请求/响应
- 查看数据格式是否正确
- 确认是否有错误信息

## 快速修复方案

### 修复 1: 清除数据库缓存并重新分析

```sql
-- 在 PostgreSQL 中执行（通过 Railway Dashboard）
-- 删除特定频道的分析记录
DELETE FROM "ChannelTrend" WHERE "channelId" = '你的频道ID';
DELETE FROM "Channel" WHERE "channelId" = '你的频道ID';
```

然后在前端重新分析该频道。

### 修复 2: 验证环境变量

**Vercel 环境变量检查清单**：
- [ ] `BACKEND_SERVICE_URL` = `https://你的-railway-后端-url.up.railway.app`
- [ ] `YOUTUBE_API_KEY` = 已设置
- [ ] `DATABASE_URL` = 已设置

**Railway 环境变量检查清单**：
- [ ] `TWITTER_BEARER_TOKEN` = 已设置（可选）
- [ ] `REDDIT_CLIENT_ID` = 已设置（可选）
- [ ] `REDDIT_CLIENT_SECRET` = 已设置（可选）
- [ ] `SERPAPI_KEY` = 已设置（可选）
- [ ] `OPENAI_API_KEY` = 已设置（可选）
- [ ] `DATABASE_URL` = 已设置
- [ ] `REDIS_URL` = 已设置（可选）

### 修复 3: 强制重新部署

**前端（Vercel）**：
1. 在 Vercel Dashboard 中清除构建缓存
2. 触发新的部署
3. 确保使用最新的代码

**后端（Railway）**：
1. 在 Railway Dashboard 中触发重新部署
2. 检查部署日志，确认使用最新代码
3. 验证健康检查端点返回 `version: "3.1.0"`

### 修复 4: 检查数据映射

**前端 API 路由**：
- `frontend/app/api/analyze/route.ts` - 确保正确调用后端
- `frontend/app/api/analysis/[channelId]/route.ts` - 确保正确解析数据

**验证点**：
- 字段名映射（snake_case → camelCase）
- 数据格式转换
- 默认值处理

## 详细对比检查清单

### 功能对比

| 功能 | Localhost | 生产环境 | 状态 |
|------|-----------|---------|------|
| 频道分析 | ✅ | ❓ | 需验证 |
| 主题提取 | ✅ | ❓ | 需验证 |
| 社交媒体趋势 | ✅ | ❓ | 需验证 |
| AI 推荐 | ✅ | ❓ | 需验证 |
| 7天趋势预测 | ✅ | ❓ | 需验证 |
| 预测观看数 | ✅ | ❓ | 需验证 |
| 回测分析 | ✅ | ❓ | 需验证 |
| 脚本生成 | ✅ | ❓ | 需验证 |

### 数据字段对比

| 字段 | Localhost | 生产环境 | 状态 |
|------|-----------|---------|------|
| 匹配度 (matchScore) | ✅ | ❓ | 需验证 |
| 互联网热度 (viralPotential) | ✅ | ❓ | 需验证 |
| 内容相关性 (relevanceScore) | ✅ | ❓ | 需验证 |
| 预测观看数 (predicted_views) | ✅ | ❓ | 需验证 |
| 趋势预测 (prediction) | ✅ | ❓ | 需验证 |
| 峰值时机 (peak_day) | ✅ | ❓ | 需验证 |
| 置信度 (confidence) | ✅ | ❓ | 需验证 |

## 诊断工具

### 创建诊断端点

在后端添加诊断端点（已添加 `/debug/analyzer`）：

```python
@app.get("/debug/full-status")
async def debug_full_status():
    """完整系统状态诊断"""
    return {
        "backend_version": "3.1.0" if PROPHET_AVAILABLE else "2.0.1",
        "prophet_available": PROPHET_AVAILABLE,
        "script_generator_available": SCRIPT_GENERATOR_AVAILABLE,
        "analyzer_type": type(content_analyzer).__name__,
        "environment_vars": {
            "TWITTER_BEARER_TOKEN": bool(os.getenv('TWITTER_BEARER_TOKEN')),
            "REDDIT_CLIENT_ID": bool(os.getenv('REDDIT_CLIENT_ID')),
            "SERPAPI_KEY": bool(os.getenv('SERPAPI_KEY')),
            "OPENAI_API_KEY": bool(os.getenv('OPENAI_API_KEY')),
            "YOUTUBE_API_KEY": bool(os.getenv('YOUTUBE_API_KEY')),
            "DATABASE_URL": bool(os.getenv('DATABASE_URL')),
            "REDIS_URL": bool(os.getenv('REDIS_URL')),
        },
        "recommendation_engine": "PredictiveRecommendationEngine" if USE_PREDICTIVE_ENGINE else "TopicRecommendationEngine",
        "social_aggregator": "EnhancedSocialMediaAggregator" if USE_ENHANCED_COLLECTOR else "SocialMediaAggregator"
    }
```

访问：`https://你的-railway-后端-url.up.railway.app/debug/full-status`

## 常见差异原因

### 1. 数据库使用旧数据

**症状**：数据格式不匹配，字段缺失

**解决**：清除数据库缓存，重新分析

### 2. API 调用失败

**症状**：使用模拟数据，互联网热度固定为 50

**解决**：检查 API 密钥配置，查看后端日志

### 3. 前端缓存

**症状**：显示旧版本的功能或数据

**解决**：清除浏览器缓存，强制刷新（Ctrl+Shift+R）

### 4. 环境变量未设置

**症状**：某些功能不可用

**解决**：在 Vercel/Railway Dashboard 中配置环境变量

## 修复优先级

### 高优先级（立即修复）

1. ✅ 验证 `BACKEND_SERVICE_URL` 配置
2. ✅ 验证后端版本是否为 3.1.0
3. ✅ 清除数据库缓存并重新分析
4. ✅ 检查前端环境变量

### 中优先级（尽快修复）

1. ✅ 验证所有 API 密钥配置
2. ✅ 检查后端日志中的错误
3. ✅ 验证数据映射是否正确

### 低优先级（后续优化）

1. ✅ 优化缓存策略
2. ✅ 添加更多诊断端点
3. ✅ 改进错误处理

## 下一步行动

1. **立即检查**：
   - 后端健康检查端点
   - Vercel 环境变量
   - Railway 环境变量

2. **清除缓存**：
   - 删除生产数据库中的旧分析记录
   - 重新分析一个测试频道

3. **验证修复**：
   - 对比 localhost 和生产环境的数据
   - 确认所有字段都正确显示

---

**更新日期**：2026-01-17
