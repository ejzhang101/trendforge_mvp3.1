# TrendForge AI

**版本**: 2.0.1-quickfix  
**最后更新**: 2026-01-13

---

## 📋 项目简介

TrendForge 是一个基于深度内容分析和社交趋势的 YouTube 频道内容推荐系统。通过 AI 驱动的分析，帮助内容创作者发现热门话题、优化内容策略，并预测视频表现。

### 核心功能

✅ **智能关键词提取** - TF-IDF + NER + KeyBERT  
✅ **深度内容分析** - 频道风格、受众分析、高表现视频  
✅ **多平台趋势收集** - Twitter + Reddit + Google Trends + SerpAPI  
✅ **智能推荐引擎** - 综合匹配分数算法  
✅ **AI 标题生成** - 多种策略的标题变体  
✅ **历史视频回测** - 预测算法准确度评估（至少50个视频）

---

## 🚀 快速开始

### 前置要求

- Python 3.9+
- Node.js 18+ (推荐使用 nvm)
- PostgreSQL 数据库
- Redis (可选，用于缓存)

### 安装步骤

#### 1. 克隆仓库

```bash
git clone <repository-url>
cd TrendForge
```

#### 2. 后端设置

```bash
cd backend
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
pip install -r requirements_v2.txt
python -m spacy download en_core_web_sm
```

#### 3. 前端设置

```bash
cd frontend
pnpm install
pnpm prisma generate
```

#### 4. 环境变量配置

**后端** (`backend/.env`):
```bash
TWITTER_BEARER_TOKEN=你的Token
SERPAPI_KEY=ae0f9c0cb85d9ad79a93f65b7d6296e18d751babc56f03b41ddd163e5ff02599
DATABASE_URL=postgresql://...
REDIS_URL=redis://localhost:6379  # 可选
```

**前端** (`frontend/.env`):
```bash
DATABASE_URL=postgresql://...
BACKEND_SERVICE_URL=http://localhost:8000
YOUTUBE_API_KEY=你的Key
```

#### 5. 数据库设置

```bash
cd frontend
pnpm prisma db push
```

#### 6. 启动服务

**后端**:
```bash
cd backend
source venv/bin/activate
python app_v2.py
```

**前端**:
```bash
cd frontend
pnpm dev
```

访问: http://localhost:3000

---

## 📚 文档

- [版本说明](VERSION_2.0.1_SERPAPI.md) - v2.0.1 详细功能说明
- [架构文档](ARCHITECTURE_V2.0.1.md) - 系统架构和技术栈
- [部署指南](DEPLOYMENT_GUIDE.md) - 生产环境部署步骤
- [变更日志](CHANGELOG.md) - 版本历史记录
- [算法文档](ALGORITHM_DOCUMENTATION.md) - 算法详细说明

---

## 🏗️ 技术栈

### 后端
- FastAPI
- Python 3.9+
- spaCy, NLTK, KeyBERT (NLP)
- scikit-learn, XGBoost, LightGBM (ML)
- Tweepy, PRAW, Pytrends, google-search-results (APIs)
- Redis (缓存)

### 前端
- Next.js 14 (App Router)
- TypeScript
- Tailwind CSS
- Prisma ORM
- Recharts

---

## 📊 版本信息

**当前版本**: v2.0.1-quickfix

**主要特性**:
- SerpAPI 集成（替代数据源）
- 回测优化（至少50个视频）
- 前端错误处理改进
- 权重算法更新

查看 [CHANGELOG.md](CHANGELOG.md) 了解详细变更。

---

## 🔧 开发

### 代码规范

- Python: 遵循 `.cursorrules` 中的规范
- TypeScript: 遵循 Next.js 最佳实践
- 提交信息: 使用语义化提交格式

### 测试

```bash
# 后端健康检查
curl http://localhost:8000/health

# 前端构建测试
cd frontend
pnpm build
```

---

## 📝 许可证

[添加许可证信息]

---

## 👥 贡献

[添加贡献指南]

---

**维护者**: TrendForge 开发团队
