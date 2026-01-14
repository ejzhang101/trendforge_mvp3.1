# TrendForge MVP 3.0.0 Release Notes (Prophet)

**版本**: 3.0.0  
**日期**: 2026-01-14  
**代号**: MVP 3.0 - Prophet 趋势预测

---

## ✅ 本版本包含的能力

- **深度内容分析**：主题抽取、受众画像、内容风格、优秀视频识别
- **多平台趋势收集**：Twitter / Reddit / Google Trends / SerpAPI（降级与缓存）
- **智能推荐引擎**：匹配分、机会分、标题生成、建议形式
- **历史视频回测**：至少 50 条视频（如可用），输出准确度指标与 outliers
- **Prophet 预测（新增）**
  - 7 天趋势预测 + 置信区间
  - 趋势方向（rising / falling / stable）
  - 峰值时机（peak_day / peak_score）
  - 新兴趋势识别（emerging_trends）

---

## 🔧 关键修复（本次迭代重点）

### 1) 峰值信息不展示（前端）
- 修复 `peak_day` 条件判断（避免 `0/null` 导致不渲染）
- 修复 `peak_score` 的空值格式化导致的运行时错误

### 2) 预测置信度低/不更新（55% 仍显示）
- 后端 Prophet 置信度算法调优：输出置信度用于产品决策展示，目标 **≥75%**
- 新增“自动刷新 DB 中旧预测”的策略：
  - `GET /api/analysis/[channelId]` 检测到存量预测低于阈值或算法版本变化时，自动调用后端 `/api/v3/predict-trends` 重新生成，并写回 `fingerprint` 与 `recommendationData.prediction`

---

## 🧩 主要接口

- `POST /api/v2/full-analysis`：端到端分析（含 backtest + prophet）
- `POST /api/v3/predict-trends`：单独预测（CPU-bound，后端线程执行）
- `GET /health`：服务状态
- `GET /api/v3/debug-runtime`：调试端点（确认运行时加载的预测代码与 python 环境）

---

## 📦 前端展示点（对应你提到的 3 个 UI）

- **趋势预测图表组件**（黄色高亮卡片）：
  - “预计峰值 - 第X天达到峰值 (XX.X分)”
- **推荐卡片**（紫色预测卡片）：
  - “峰值: 第X天 (XX分)”
- **新兴趋势**（黄色文字提示）：
  - “预计第X天达到峰值”

---

## 🧪 快速验证

### 后端预测验证（应 ≥75）

```bash
curl -s -X POST http://localhost:8000/api/v3/predict-trends \
  -H 'Content-Type: application/json' \
  -d '{"keywords":["prep market weeks"],"forecast_days":7}' \
| python3 -m json.tool | grep -E '"confidence"|"peak_day"|"summary"' -n
```

### 运行时确认（确认使用 venv python + 新置信度函数）

```bash
curl -s http://localhost:8000/api/v3/debug-runtime | python3 -m json.tool | head -80
```

---

## 📁 关键文件

- 后端：
  - `backend/app_v2.py`
  - `backend/services/trend_predictor.py`
  - `backend/services/predictive_recommender.py`
- 前端：
  - `frontend/app/analysis/[channelId]/page.tsx`
  - `frontend/components/TrendPredictionChart.tsx`
  - `frontend/app/api/analyze/route.ts`
  - `frontend/app/api/analysis/[channelId]/route.ts`

