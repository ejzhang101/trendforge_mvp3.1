# Changelog

All notable changes to TrendForge will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

---

## [3.0.0] - 2026-01-14

### Added
- **Prophet 预测能力 (MVP 3.0)**:
  - `POST /api/v3/predict-trends` 7天趋势预测（趋势方向、峰值时机、置信区间、准确度指标）
  - `GET /api/v3/debug-runtime` 本地调试端点：验证运行时加载的预测代码与 python 环境
- **预测落库自动刷新**（解决旧数据仍显示低置信度的问题）:
  - `GET /api/analysis/[channelId]` 检测到旧预测低于阈值或算法版本变化时，自动调用后端重新生成并写回 DB
  - 同步更新 `ChannelTrend.recommendationData.prediction`，保证推荐卡片展示峰值信息
- **MVP 3.0 文档**:
  - `docs/ARCHITECTURE_V3.0.0.md`
  - `docs/MVP3.0.0_RELEASE_NOTES.md`
  - `docs/RUNTIME_LOGS_MVP3.0.0_LOCALHOST_2026-01-14.md`
- **UI/UX 优化**:
  - 将"7天趋势预测"整合到"AI 智能推荐话题"详情弹窗中，通过 Tab 切换查看
  - 详情弹窗新增 Tab 导航："详细信息"和"7天趋势预测"
  - 在"7天趋势预测" Tab 中显示完整的 `TrendPredictionChart` 组件（图表、置信区间、峰值时机、模型准确度）

### Changed
- **Prophet 置信度算法与阈值策略**:
  - 服务端置信度用于产品展示与行动建议，目标 **≥75%**
  - 新兴趋势识别阈值提升至 75%
- **前端展示稳定性**:
  - 修复 `peak_day`/`peak_score` 的空值渲染与条件判断，确保峰值信息稳定展示
  - 为结果页的预测刷新逻辑增加 in-flight 互斥锁与 30s 超时，避免 `/api/analysis/[channelId]` 造成“持续加载中”
- **产品文案**:
  - 首页 footer 更新为 `Powered by AI and love in TRT - MVP3.0`
- **UI 结构优化**:
  - 移除独立的"7天趋势预测"板块，避免与"AI 智能推荐话题"重复显示
  - 推荐详情弹窗采用 Tab 设计，提供更好的信息组织方式

### Fixed
- 修复"前端仍显示旧置信度（如 55%）"：
  - 原因为 DB 缓存/旧 fingerprint 数据未更新
  - 通过自动 refresh 机制确保前端读到最新预测
- 修复 React StrictMode 触发的双重数据获取导致结果页长时间 loading 的问题（使用 `useRef` guard 与预测刷新互斥锁）
- **修复推荐话题重复显示问题**：
  - 后端：在 `predictive_recommender.py` 和 `intelligent_recommender.py` 中添加关键词去重逻辑（保留匹配度最高的）
  - 前端：在显示推荐列表时进行二次去重，确保每个关键词只显示一次
  - 去重策略：关键词标准化（小写+去空格），保留匹配度/最终分数最高的推荐

---

## [2.0.1] - 2026-01-13

### Added
- **SerpAPI Integration**: Added `EnhancedSerpAPICollector` as alternative data source for social trends
  - Extracts Twitter and Reddit data from Google search results
  - Automatic fallback when other APIs fail
  - 20% weight in composite score calculation
- **Backtest Optimization**: Enhanced backtest analyzer to use at least 50 videos
  - Uses most recent 50 videos if channel has more than 50
  - Increased timeout to 60 seconds for 50+ videos
  - Fixed async/await issues (converted to sync functions)
- **Frontend Error Handling**: Improved error handling and display
  - Added error state management
  - Optional chaining (`?.`) for null safety
  - Better error messages and retry functionality
- **Documentation**: Comprehensive version and architecture documentation
  - `VERSION_2.0.1_SERPAPI.md` - Version details
  - `ARCHITECTURE_V2.0.1.md` - Architecture overview
  - `DEPLOYMENT_GUIDE.md` - Deployment instructions

### Changed
- **Weight Algorithm**: Updated social trend aggregation weights
  - Twitter: 30% → 25%
  - Reddit: 30% → 25%
  - Google: 40% → 30%
  - SerpAPI: 0% → 20% (new)
- **Backtest Requirements**: Minimum video count logic updated
  - Previously: All videos
  - Now: At least 50 videos (if available), uses most recent 50
- **Timeout Settings**: Adjusted timeouts for better performance
  - Backtest: 30s → 60s (for 50+ videos)
  - Social collection: 15s per platform

### Fixed
- Fixed async/await issues in `backtest_analyzer.py`
  - Converted `backtest_predictions` from async to sync
  - Converted `_backtest_single_video` from async to sync
  - Fixed `asyncio.to_thread` call in `app_v2.py`
- Fixed frontend client-side errors
  - Added optional chaining for `data.backtest` access
  - Fixed missing error state in analysis page
  - Improved error boundary handling

### Dependencies
- Added `google-search-results>=2.4.2` to `requirements_v2.txt`

---

## [2.0.0] - 2026-01-11

### Added
- MVP 2.0 core features
- Intelligent keyword extraction (TF-IDF + NER + KeyBERT)
- Deep content analysis
- Multi-platform trend collection (Twitter, Reddit, Google Trends)
- Intelligent recommendation engine
- AI title generation
- Historical video backtest

### Changed
- Rolled back from MVP 3.0 (Prophet removed)
- Optimized performance with timeouts and caching

---

## [1.0.0] - Initial Release

### Added
- Basic channel analysis
- Social media trend collection
- Recommendation generation

---

**Legend**:
- `Added` - New features
- `Changed` - Changes in existing functionality
- `Deprecated` - Soon-to-be removed features
- `Removed` - Removed features
- `Fixed` - Bug fixes
- `Security` - Security improvements
