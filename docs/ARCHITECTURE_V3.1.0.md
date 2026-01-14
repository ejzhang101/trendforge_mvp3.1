# TrendForge Architecture v3.1.0 (MVP 3.1 - Prophet + LLM Script Generation)

**版本**: 3.1.0  
**日期**: 2026-01-14

---

## 🏗️ 系统架构（MVP 3.1）

### 整体架构图

```
┌────────────────────────────────────────────────────────────────────────┐
│                        Frontend (Next.js 14)                           │
│  ┌───────────────────┐  ┌──────────────────────────┐                  │
│  │ Home Page         │  │ Analysis Page             │                  │
│  │ /                 │  │ /analysis/[channelId]     │                  │
│  └─────────┬─────────┘  └─────────────┬────────────┘                  │
│            │                           │                               │
│            │  POST /api/analyze        │ GET /api/analysis/[channelId] │
│            └───────────────┬───────────┴───────────────┬──────────────┘
│                            │                           │
│                     Prisma DB (PostgreSQL)             │
│                   Channel.fingerprint.v2_analysis       │
│                 ChannelTrend.recommendationData         │
└────────────────────────────┼───────────────────────────┘
                             │ HTTP/REST
┌────────────────────────────┼───────────────────────────┐
│                   Backend (FastAPI)                     │
│  ┌───────────────────────────────────────────────────┐  │
│  │ POST /api/v2/full-analysis                        │  │
│  │   ├─ Step 1: Deep Channel Analysis                │  │
│  │   ├─ Step 2: Social Media Trends Collection       │  │
│  │   ├─ Step 3: Intelligent Recommendations          │  │
│  │   ├─ Step 4: Title Generation                     │  │
│  │   ├─ Step 5: Prophet Predictions (MVP 3.0)        │  │
│  │   └─ Step 6: Backtest Analysis (MVP 2.0)          │  │
│  └───────────────────────────────────────────────────┘  │
│  ┌───────────────────────────────────────────────────┐  │
│  │ POST /api/v3/generate-scripts (MVP 3.1)           │  │
│  │   ├─ LLM Semantic Analysis (OpenAI GPT-4o-mini)   │  │
│  │   ├─ Intelligent Script Generation                │  │
│  │   └─ Performance Prediction                       │  │
│  └───────────────────────────────────────────────────┘  │
│  ┌───────────────────────────────────────────────────┐  │
│  │ Services Layer                                    │  │
│  │   ├─ EnhancedContentAnalyzer                     │  │
│  │   ├─ EnhancedSocialMediaAggregator               │  │
│  │   ├─ PredictiveRecommendationEngine (MVP 3.0)     │  │
│  │   ├─ TrendPredictor (Prophet)                     │  │
│  │   ├─ BacktestAnalyzer (MVP 2.0)                   │  │
│  │   └─ ScriptGeneratorEngine (MVP 3.1) ⭐ NEW      │  │
│  └───────────────────────────────────────────────────┘  │
└───────────────────────────────────────────────────────────┘
```

---

## 🆕 MVP 3.1 新增功能

### 1. LLM 增强的智能脚本生成

#### 架构组件

```
ScriptGeneratorEngine
├─ LLM Client (OpenAI GPT-4o-mini)
│  ├─ Semantic Analysis
│  │  └─ Extract: product_type, target_customers, key_advantages, etc.
│  └─ Script Generation
│     └─ Generate: title, hook, main_content, cta, key_points
├─ Template Fallback
│  └─ Template-based generation (when LLM unavailable)
└─ Error Handling
   └─ Auto-fallback on LLM failures
```

#### 工作流程

1. **用户输入** → 产品/服务描述（支持中英文）
2. **语义分析**:
   - LLM 模式：使用 GPT-4o-mini 提取结构化信息
   - 模板模式：基础关键词提取
3. **脚本生成**:
   - LLM 模式：结合频道分析、推荐话题、产品信息生成个性化脚本
   - 模板模式：使用预定义模板填充
4. **性能预测** → 预测播放量、互动率、综合评分
5. **返回结果** → 多个脚本变体 + 推荐理由

#### 数据流

```
User Prompt (中英文)
    ↓
_parse_user_prompt()
    ├─ LLM Mode: _parse_with_llm() → GPT-4o-mini
    │  └─ Extract structured info (JSON)
    └─ Fallback: _parse_basic() → Keyword extraction
    ↓
Product Info (Dict)
    ↓
_generate_single_script()
    ├─ LLM Mode: _generate_script_with_llm() → GPT-4o-mini
    │  └─ Generate full script (JSON)
    └─ Fallback: _generate_script_content() → Template
    ↓
Script Object
    ├─ title, duration, structure
    ├─ hook (content, techniques, visual_suggestion)
    ├─ main_content (sections with title, duration, content, engagement)
    ├─ cta (content, techniques, placement)
    └─ key_points
    ↓
Performance Prediction
    └─ predicted_views, engagement_rate, composite_score
```

---

## 📊 技术栈（MVP 3.1）

### 后端
- **Python 3.9+**
- **FastAPI** - Web 框架
- **OpenAI API** (gpt-4o-mini) - LLM 脚本生成 ⭐ NEW
- **Prophet** - 时间序列预测
- **spaCy, NLTK, KeyBERT** - NLP 分析
- **scikit-learn, XGBoost, LightGBM** - ML 模型
- **Redis** - 缓存
- **PostgreSQL** (via Prisma) - 数据库

### 前端
- **Next.js 14** (App Router)
- **TypeScript**
- **React 18**
- **Tailwind CSS**
- **Recharts** - 数据可视化
- **Lucide React** - 图标

---

## 🔑 核心 API 端点

### MVP 3.1 新增

#### `POST /api/v3/generate-scripts`

**功能**: 生成智能视频脚本

**请求体**:
```json
{
  "user_prompt": "产品/服务描述（支持中英文）",
  "channel_analysis": {
    "topics": [...],
    "content_style": {...},
    "target_audience": {...},
    "high_performers": {...}
  },
  "recommendations": [
    {
      "keyword": "...",
      "match_score": 75,
      "viral_potential": 60,
      ...
    }
  ],
  "count": 3
}
```

**响应**:
```json
{
  "success": true,
  "scripts": [
    {
      "id": "script_1",
      "title": "...",
      "keyword": "...",
      "template_type": "...",
      "script": {
        "title": "...",
        "duration": "8-10分钟",
        "structure": "...",
        "hook": {...},
        "main_content": {...},
        "cta": {...},
        "key_points": [...]
      },
      "predicted_performance": {...},
      "reasoning": {...}
    }
  ],
  "count": 3,
  "generated_at": "2026-01-14T..."
}
```

---

## 🔧 配置要求

### 环境变量

```bash
# OpenAI API (MVP 3.1 - 可选)
OPENAI_API_KEY=sk-proj-...

# 其他 API Keys
TWITTER_BEARER_TOKEN=...
REDDIT_CLIENT_ID=...
REDDIT_CLIENT_SECRET=...
SERPAPI_KEY=...
REDIS_URL=redis://localhost:6379
DATABASE_URL=postgresql://...
```

### 依赖安装

```bash
cd backend
source venv/bin/activate
pip install -r requirements_v2.txt
# 包含: openai>=1.3.0
```

---

## 🚀 部署说明

### 本地开发

```bash
# 后端
cd backend
source venv/bin/activate
python app_v2.py

# 前端
cd frontend
pnpm dev
```

### 生产环境

```bash
# 后端
gunicorn app_v2:app --workers 4 --bind 0.0.0.0:8000

# 前端
pnpm build && pnpm start
```

---

## 📈 性能指标

### LLM 脚本生成
- **响应时间**: 3-5 秒（LLM 模式），< 1 秒（模板模式）
- **成本**: 约 $0.00075 / 请求（GPT-4o-mini）
- **Token 使用**: 
  - 语义分析: ~500 tokens
  - 脚本生成: ~2000 tokens

### 系统整体
- **分析时间**: 30-60 秒（完整分析）
- **缓存命中率**: 60-80%（社交趋势数据）
- **API 限流**: 自动处理，使用缓存和模拟数据

---

## 🔄 版本历史

- **v3.1.0** (2026-01-14): LLM 增强的智能脚本生成
- **v3.0.0** (2026-01-14): Prophet 时间序列预测
- **v2.0.1** (2026-01-13): 快速修复版本
- **v2.0.0** (2026-01-12): 深度内容分析和智能推荐

---

## 📚 相关文档

- `backend/SCRIPT_GENERATOR_LLM.md` - LLM 脚本生成器使用说明
- `backend/API_KEYS_SETUP.md` - API Keys 配置指南
- `docs/MVP3.0.0_RELEASE_NOTES.md` - MVP 3.0 发布说明
- `CHANGELOG.md` - 完整变更日志
