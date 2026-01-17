# Vercel 前端数据一致性修复 - MVP 3.1

## 问题描述

部署到 Vercel 的前端显示的数据与 MVP 3.1 版本不一致：
- ❌ 7天趋势预测不准确
- ❌ 视频关键词不准确
- ❌ 预测观看数不准确
- ❌ 互联网热度不准确
- ❌ trend关键词不准确

## 根本原因

1. **后端推荐数据生成问题**：当没有社交媒体趋势时，后端生成的基础推荐数据格式不一致
2. **字段映射问题**：后端返回 `snake_case`，前端期望 `camelCase`
3. **数据计算问题**：`viral_potential` 和 `predicted_views` 被硬编码，没有动态计算

## 已完成的修复

### 1. 后端修复 (`backend/app_v2.py`)

**问题**：当没有社交媒体趋势时，手动生成的推荐数据格式不一致

**修复**：
- ✅ 使用 `predictive_recommender` 生成推荐（确保格式一致）
- ✅ 创建模拟社交趋势数据，基于频道主题分数
- ✅ 动态计算 `viral_potential`：`50 + (topic_score * 30)` (50-80 范围)
- ✅ 动态计算 `predicted_views`：`avg_views * (0.8 + topic_score * 0.4)`
- ✅ 确保所有字段都正确生成

**代码位置**：`backend/app_v2.py` 第 510-600 行

### 2. 前端数据映射

**验证**：前端代码已正确映射字段名
- ✅ `viral_potential` → `viralPotential`
- ✅ `predicted_performance` → `predictedPerformance`
- ✅ `match_score` → `matchScore`
- ✅ `trend_predictions` → `trendPredictions`

**代码位置**：
- `frontend/app/api/analyze/route.ts` 第 320-338 行
- `frontend/app/api/analysis/[channelId]/route.ts` 第 220-340 行

## 验证步骤

### 1. 检查 Vercel 环境变量

在 Vercel Dashboard 中验证：

```bash
BACKEND_SERVICE_URL=https://你的-railway-后端-url.up.railway.app
```

**重要**：确保 URL 包含 `https://` 协议

### 2. 检查后端部署状态

访问后端健康检查端点：
```
https://你的-railway-后端-url.up.railway.app/health
```

应该看到：
```json
{
  "status": "healthy",
  "version": "3.1.0",
  "features": {
    "prophet": true,
    "script_generator": true
  }
}
```

### 3. 测试完整数据流

1. **前端发起分析请求**
   - 访问：`https://你的-vercel-前端-url.vercel.app`
   - 输入 YouTube 频道 ID
   - 点击"分析"

2. **检查后端日志**
   - 在 Railway Dashboard 查看部署日志
   - 确认看到：
     ```
     ✅ Using content_analyzer: LightweightContentAnalyzer
     🔮 Step 5/5: Generating Prophet predictions...
     ✅ Generated X recommendations
     ```

3. **检查前端显示**
   - 确认推荐卡片显示：
     - ✅ 互联网热度（viralPotential）
     - ✅ 预测观看数（predictedPerformance.predicted_views）
     - ✅ 7天趋势预测（prediction）
     - ✅ 趋势关键词（keyword）

## 数据字段对照表

| 后端字段 (snake_case) | 前端字段 (camelCase) | 说明 |
|---------------------|---------------------|------|
| `viral_potential` | `viralPotential` | 互联网热度 (0-100) |
| `predicted_performance.predicted_views` | `predictedPerformance.predicted_views` | 预测观看数 |
| `predicted_performance.tier` | `predictedPerformance.tier` | 表现等级 (excellent/good/moderate) |
| `match_score` | `matchScore` | 匹配分数 (0-100) |
| `trend_predictions` | `trendPredictions` | 7天趋势预测数组 |
| `emerging_trends` | `emergingTrends` | 新兴趋势数组 |
| `prediction.trend_direction` | `prediction.trendDirection` | 趋势方向 (rising/falling/stable) |
| `prediction.peak_day` | `prediction.peakDay` | 峰值时机（天数） |

## 常见问题排查

### 问题 1：数据仍然不准确

**可能原因**：
- Vercel 缓存了旧版本
- 后端 URL 配置错误

**解决方案**：
1. 清除 Vercel 构建缓存
2. 重新部署前端
3. 验证 `BACKEND_SERVICE_URL` 环境变量

### 问题 2：7天趋势预测不显示

**可能原因**：
- Prophet 未启用
- 后端未返回 `trend_predictions`

**解决方案**：
1. 检查后端健康检查端点，确认 `prophet: true`
2. 检查后端日志，确认看到 "🔮 Step 5/5: Generating Prophet predictions..."
3. 检查前端控制台，查看 `trendPredictions` 数组

### 问题 3：预测观看数固定为 12000 或 8000

**可能原因**：
- 使用了旧数据（缓存）

**解决方案**：
1. 清除数据库缓存（删除该频道的分析记录）
2. 重新分析频道
3. 检查 `predicted_views` 是否为动态计算的值

## 部署检查清单

- [ ] Vercel 环境变量 `BACKEND_SERVICE_URL` 已设置
- [ ] Railway 后端已部署并运行
- [ ] 后端健康检查返回 `prophet: true`
- [ ] 前端已重新部署（清除缓存）
- [ ] 测试分析功能，确认所有字段正确显示

## 相关文件

- `backend/app_v2.py` - 后端主应用
- `backend/services/predictive_recommender.py` - 推荐引擎
- `frontend/app/api/analyze/route.ts` - 前端分析 API
- `frontend/app/api/analysis/[channelId]/route.ts` - 前端数据获取 API
- `frontend/app/analysis/[channelId]/page.tsx` - 前端分析页面

## 更新日期

2026-01-14 - MVP 3.1 数据一致性修复
