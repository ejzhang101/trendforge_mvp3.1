# 生产环境修复检查清单 - MVP 3.1

## 🚨 紧急修复步骤

### 步骤 1: 验证后端版本

访问：`https://你的-railway-后端-url.up.railway.app/health`

**期望**：
```json
{
  "version": "3.1.0",
  "services": {
    "prophet": true,
    "script_generator": true
  }
}
```

**如果不匹配**：
- [ ] 在 Railway Dashboard 触发重新部署
- [ ] 检查部署日志，确认使用最新代码
- [ ] 等待部署完成（通常 2-5 分钟）

---

### 步骤 2: 验证前端环境变量

在 Vercel Dashboard → Settings → Environment Variables 中检查：

- [ ] `BACKEND_SERVICE_URL` = `https://你的-railway-后端-url.up.railway.app`
  - ⚠️ **必须包含 `https://`**
  - ⚠️ **不能有尾部斜杠**
  
- [ ] `YOUTUBE_API_KEY` = 已设置且有效

- [ ] `DATABASE_URL` = 已设置且指向正确的数据库

**修复后**：
- [ ] 在 Vercel Dashboard 中清除构建缓存
- [ ] 触发新的部署

---

### 步骤 3: 使用诊断端点

访问：`https://你的-railway-后端-url.up.railway.app/debug/full-status`

**对比 localhost**：
```bash
# Localhost
curl http://localhost:8000/debug/full-status

# 生产环境
curl https://你的-railway-后端-url.up.railway.app/debug/full-status
```

**检查差异**：
- [ ] `backend_version` 是否都是 `3.1.0`
- [ ] `analyzer_type` 是否都是 `LightweightContentAnalyzer`
- [ ] `recommendation_engine` 是否都是 `PredictiveRecommendationEngine`
- [ ] `environment_vars` 配置是否一致

---

### 步骤 4: 清除数据库缓存

**如果数据格式不匹配**：

1. **识别问题频道**：
   - 记录频道 ID
   - 检查数据库中该频道的数据

2. **清除缓存**（通过 Railway PostgreSQL Dashboard）：
   ```sql
   -- 删除特定频道的分析记录
   DELETE FROM "ChannelTrend" WHERE "channelId" = '你的频道ID';
   DELETE FROM "Channel" WHERE "channelId" = '你的频道ID';
   ```

3. **重新分析**：
   - 在前端重新分析该频道
   - 验证新数据格式是否正确

---

### 步骤 5: 验证数据流

**测试完整分析流程**：

1. **前端发起分析**：
   - 访问生产前端 URL
   - 输入测试频道 ID
   - 点击"分析"

2. **检查后端日志**（Railway Dashboard）：
   - [ ] 看到 `✅ Using content_analyzer: LightweightContentAnalyzer`
   - [ ] 看到 `🔮 Step 5/5: Generating Prophet predictions...`
   - [ ] 看到 `✅ Generated X recommendations`
   - [ ] 没有看到 `⚠️ Social trends timeout`（除非真的超时）

3. **检查前端控制台**（浏览器开发者工具）：
   - [ ] 看到 `✅ Backend analysis complete`
   - [ ] 看到 `📊 Backend response includes backtest`
   - [ ] 没有看到错误信息

4. **验证显示的数据**：
   - [ ] 匹配度（matchScore）在 0-100 范围
   - [ ] 互联网热度（viralPotential）在 20-100 范围
   - [ ] 内容相关性（relevanceScore）在 0-100 范围
   - [ ] 预测观看数（predicted_views）在 1,000 - 50,000,000 范围
   - [ ] 7天趋势预测（prediction）存在且包含 `peak_day`
   - [ ] 置信度（confidence）>= 75%

---

## 🔍 常见问题快速修复

### 问题 1: 所有数据都是固定值

**症状**：
- 互联网热度 = 50
- 预测观看数 = 12000 或 8000
- 匹配度 = 固定值

**原因**：使用了旧的缓存数据或模拟数据

**修复**：
1. 清除数据库缓存（步骤 4）
2. 重新分析频道
3. 验证新数据

---

### 问题 2: 7天趋势预测不显示

**症状**：推荐卡片中没有趋势预测信息

**原因**：
- Prophet 未启用
- 预测置信度 < 75%
- 数据格式不匹配

**修复**：
1. 检查后端健康检查：`prophet: true`
2. 检查后端日志：是否看到 `🔮 Step 5/5: Generating Prophet predictions...`
3. 清除缓存并重新分析

---

### 问题 3: 功能字段缺失

**症状**：某些功能或字段在生产环境不显示

**原因**：
- 前端版本不一致
- 数据映射错误
- 环境变量未设置

**修复**：
1. 清除 Vercel 构建缓存
2. 重新部署前端
3. 检查浏览器控制台错误
4. 验证环境变量

---

## 📊 数据对比表

### Localhost vs 生产环境

| 检查项 | Localhost | 生产环境 | 修复状态 |
|--------|-----------|---------|---------|
| 后端版本 | 3.1.0 | ❓ | ⬜ |
| 分析器类型 | LightweightContentAnalyzer | ❓ | ⬜ |
| 推荐引擎 | PredictiveRecommendationEngine | ❓ | ⬜ |
| Prophet 可用 | true | ❓ | ⬜ |
| Script Generator 可用 | true | ❓ | ⬜ |
| YouTube API 配置 | true | ❓ | ⬜ |
| 数据库连接 | ✅ | ❓ | ⬜ |
| Redis 连接 | ✅ | ❓ | ⬜ |

---

## 🎯 验证清单

修复完成后，验证以下内容：

- [ ] 后端健康检查返回 `version: "3.1.0"`
- [ ] `/debug/full-status` 显示所有功能可用
- [ ] 前端可以成功分析频道
- [ ] 所有数据字段都正确显示
- [ ] 数据值在合理范围内
- [ ] 7天趋势预测正常显示
- [ ] 预测观看数动态计算（不是固定值）
- [ ] 互联网热度基于真实或模拟数据（不是固定 50）

---

## 📞 如果问题仍然存在

请提供以下信息：

1. **后端健康检查响应**：
   ```bash
   curl https://你的-railway-后端-url.up.railway.app/health
   ```

2. **完整系统状态**：
   ```bash
   curl https://你的-railway-后端-url.up.railway.app/debug/full-status
   ```

3. **前端环境变量**（截图或列表）：
   - Vercel Dashboard → Settings → Environment Variables

4. **浏览器控制台错误**（如果有）

5. **后端部署日志**（Railway Dashboard）：
   - 最近一次部署的日志
   - 特别是分析请求的日志

6. **数据对比**：
   - Localhost 显示的数据（截图）
   - 生产环境显示的数据（截图）

---

**更新日期**：2026-01-17
