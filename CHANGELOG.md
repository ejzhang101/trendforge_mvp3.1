# Changelog

All notable changes to TrendForge will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

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
