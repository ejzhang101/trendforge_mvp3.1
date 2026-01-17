# 数据不一致问题修复指南

**问题描述**: 生产环境显示的数据与 localhost 不一致，包括：
1. 所有推荐话题的数据完全相同（match_score, viral_potential, predicted_views）
2. 7天趋势预测显示 "(暂无数据)"
3. 脚本生成失败 ("Load failed")

## 🔍 根本原因分析

### 问题 1: 推荐数据完全相同

**可能原因**:
1. **数据库中的旧数据格式** - `recommendationData` 字段可能为空或格式不对
2. **前端使用 fallback 值** - 当 `recData` 不存在时，前端使用相同的 fallback 计算
3. **后端生成时数据相同** - 如果社交 API 返回的数据相同，所有推荐也会相同

**检查方法**:
```sql
-- 在 Railway PostgreSQL Dashboard 中执行
SELECT 
  ct.id,
  ct."matchScore",
  ct."recommendationData",
  t.keyword
FROM "ChannelTrend" ct
JOIN "Trend" t ON ct."trendId" = t.id
LIMIT 10;
```

### 问题 2: 7天趋势预测无数据

**可能原因**:
1. **`trend_predictions` 字段为空** - 数据库中没有存储预测数据
2. **前端读取逻辑问题** - 前端没有正确读取 `fingerprint.v2_analysis.trend_predictions`
3. **后端未生成预测** - 分析时 `enable_predictions` 为 false 或 Prophet 不可用

**检查方法**:
```sql
-- 检查频道指纹中的预测数据
SELECT 
  "channelId",
  fingerprint->'v2_analysis'->'trend_predictions' as trend_predictions,
  fingerprint->'v2_analysis'->'emerging_trends' as emerging_trends
FROM "Channel"
WHERE "channelId" = 'YOUR_CHANNEL_ID';
```

### 问题 3: 脚本生成失败

**可能原因**:
1. **API 端点错误** - 前端调用的后端 URL 不正确
2. **OpenAI API 密钥问题** - 后端无法调用 OpenAI API
3. **请求格式错误** - 前端发送的数据格式不对

## 🔧 修复步骤

### 步骤 1: 清除数据库缓存（必须）

在 Railway PostgreSQL Dashboard 中执行：

```sql
-- 删除所有分析记录（强制重新分析）
DELETE FROM "ChannelTrend";
DELETE FROM "Channel";
```

或者只删除特定频道：

```sql
-- 删除特定频道的记录
DELETE FROM "ChannelTrend" WHERE "channelId" = 'YOUR_CHANNEL_ID';
DELETE FROM "Channel" WHERE "channelId" = 'YOUR_CHANNEL_ID';
```

### 步骤 2: 验证后端配置

检查生产环境后端状态：

```bash
curl https://tf-mvp31.up.railway.app/debug/full-status | python3 -m json.tool
```

确保：
- ✅ `REDIS_URL: true`
- ✅ `DATABASE_URL: true`
- ✅ `OPENAI_API_KEY: true`
- ✅ `prophet_available: true`

### 步骤 3: 重新分析频道

1. 在前端重新分析一个测试频道
2. 等待分析完成（可能需要 1-2 分钟）
3. 检查后端日志是否有错误

### 步骤 4: 验证数据格式

重新分析后，检查数据库中的数据：

```sql
-- 检查推荐数据格式
SELECT 
  ct.id,
  ct."matchScore",
  jsonb_pretty(ct."recommendationData") as recommendation_data,
  t.keyword
FROM "ChannelTrend" ct
JOIN "Trend" t ON ct."trendId" = t.id
WHERE ct."channelId" = 'YOUR_CHANNEL_ID'
LIMIT 5;
```

应该看到：
- `matchScore` 值不同
- `recommendationData` 包含 `viralPotential`, `performanceScore`, `relevanceScore` 等字段
- 每个推荐的数据应该不同

### 步骤 5: 验证预测数据

```sql
-- 检查预测数据
SELECT 
  "channelId",
  jsonb_pretty(fingerprint->'v2_analysis'->'trend_predictions') as predictions
FROM "Channel"
WHERE "channelId" = 'YOUR_CHANNEL_ID';
```

应该看到：
- `trend_predictions` 是一个数组，包含多个预测对象
- 每个预测对象包含 `keyword`, `trend_direction`, `confidence`, `peak_day` 等字段

## 🐛 如果问题仍然存在

### 检查后端日志

在 Railway Dashboard 中查看后端日志，查找：
- 错误信息
- API 调用失败
- 数据生成警告

### 检查前端控制台

在浏览器开发者工具中查看：
- 网络请求是否成功
- API 响应数据格式
- 控制台错误信息

### 对比 localhost 和生产环境

1. 在 localhost 分析同一个频道
2. 在生产环境分析同一个频道
3. 对比两个环境的 API 响应

```bash
# Localhost
curl http://localhost:8000/api/v2/full-analysis \
  -X POST \
  -H "Content-Type: application/json" \
  -d @test_request.json | python3 -m json.tool > localhost_response.json

# Production
curl https://tf-mvp31.up.railway.app/api/v2/full-analysis \
  -X POST \
  -H "Content-Type: application/json" \
  -d @test_request.json | python3 -m json.tool > production_response.json

# 对比
diff localhost_response.json production_response.json
```

## 📋 验证清单

修复后，验证以下内容：

- [ ] 数据库缓存已清除
- [ ] 后端配置正确（REDIS_URL, DATABASE_URL, OPENAI_API_KEY）
- [ ] 重新分析频道后，推荐数据不同
- [ ] `matchScore` 值不同（不是所有都是 360）
- [ ] `viralPotential` 值不同（不是所有都是 194）
- [ ] `predictedViews` 值不同（不是所有都是 54,468）
- [ ] `trend_predictions` 数组不为空
- [ ] 7天趋势预测正常显示
- [ ] 脚本生成功能正常

## 💡 预防措施

1. **定期清除旧数据** - 如果数据格式更新，清除旧数据
2. **验证数据格式** - 在保存数据前验证格式
3. **监控后端日志** - 及时发现数据生成问题
4. **对比测试** - 定期对比 localhost 和生产环境的数据

---

**更新日期**: 2026-01-17
