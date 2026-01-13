# 🚀 TrendForge MVP 2.0 - 快速开始指南

## 📋 系统状态

✅ **所有服务运行正常！**

- 后端：`http://localhost:8000` ✅
- 前端：`http://localhost:3000` ✅
- 数据库：PostgreSQL ✅
- API 文档：`http://localhost:8000/docs` ✅

## 🎯 快速测试

### 1. 通过前端界面测试（推荐）

```bash
# 1. 打开浏览器访问
http://localhost:3000

# 2. 输入频道标识符（例如）：
UCX6OQ3DkcsbYNE6H8uQQuVA  # MrBeast
@MrBeast                   # 用户名格式
c/MrBeast                  # 自定义 URL

# 3. 点击"开始分析"
# 4. 等待 30-60 秒
# 5. 查看详细分析结果
```

### 2. 通过 API 测试

```bash
# 完整分析（推荐）
curl -X POST http://localhost:8000/api/v2/full-analysis \
  -H "Content-Type: application/json" \
  -d '{
    "videos": [
      {
        "videoId": "dQw4w9WgXcQ",
        "title": "Example Video",
        "description": "Example description",
        "publishedAt": "2024-01-01T00:00:00Z",
        "viewCount": 1000000,
        "likeCount": 50000,
        "commentCount": 1000
      }
    ],
    "channel_data": {
      "channelId": "UCX6OQ3DkcsbYNE6H8uQQuVA",
      "title": "Test Channel",
      "subscriberCount": 1000000,
      "videoCount": 100,
      "viewCount": 100000000
    },
    "geo": "US",
    "analyze_transcripts": false,
    "max_recommendations": 10
  }'
```

## 📊 主要 API 端点

### 1. 健康检查
```bash
GET http://localhost:8000/health
```

### 2. 频道分析
```bash
POST http://localhost:8000/api/v2/analyze-channel
```

### 3. 社交趋势收集
```bash
POST http://localhost:8000/api/v2/collect-social-trends
```

### 4. 生成推荐
```bash
POST http://localhost:8000/api/v2/generate-recommendations
```

### 5. 生成标题
```bash
POST http://localhost:8000/api/v2/generate-titles
```

### 6. 完整分析（推荐）
```bash
POST http://localhost:8000/api/v2/full-analysis
```

## 🔧 常用命令

### 启动服务

```bash
# 终端 1: 后端
cd backend
source venv/bin/activate
python app_v2.py

# 终端 2: 前端
cd frontend
pnpm dev
```

### 检查服务状态

```bash
# 检查后端
curl http://localhost:8000/health

# 检查前端
curl http://localhost:3000
```

### 查看 API 文档

```bash
# 打开浏览器访问
http://localhost:8000/docs
```

## 📁 项目结构

```
TrendForge/
├── backend/
│   ├── app_v2.py              # 主应用文件
│   ├── services/               # 服务模块
│   │   ├── enhanced_youtube_analyzer.py
│   │   ├── social_media_collector.py
│   │   └── intelligent_recommender.py
│   ├── requirements_v2.txt     # Python 依赖
│   └── .env                    # 环境变量（可选）
├── frontend/
│   ├── app/
│   │   ├── page.tsx            # 首页
│   │   ├── api/
│   │   │   ├── analyze/        # 分析 API
│   │   │   └── analysis/       # 结果查询 API
│   │   └── analysis/           # 分析结果页面
│   ├── prisma/
│   │   └── schema.prisma       # 数据库模型
│   └── .env                    # 环境变量
└── DEPLOYMENT_CHECKLIST.md     # 部署检查清单
```

## 🎨 功能特性

### ✅ 已实现

1. **智能关键词提取**
   - TF-IDF + 词性标注 + NER + KeyBERT

2. **深度内容分析**
   - 字幕提取（可选）
   - 主题建模
   - 情感分析

3. **多平台趋势**
   - Twitter/X
   - Reddit
   - Google Trends

4. **智能推荐**
   - 4 维度评分系统
   - 匹配度计算

5. **AI 标题生成**
   - 每个话题 3 个标题变体
   - CTR 预测

## ⚙️ 配置选项

### 性能优化

```python
# 在 API 请求中设置
{
  "analyze_transcripts": false,  # 禁用字幕分析（更快）
  "max_recommendations": 5        # 减少推荐数量
}
```

### 环境变量

必需：
- `DATABASE_URL` - PostgreSQL 连接字符串
- `YOUTUBE_API_KEY` - YouTube Data API Key
- `BACKEND_SERVICE_URL` - 后端服务 URL

可选：
- `TWITTER_BEARER_TOKEN` - Twitter API Token
- `REDDIT_CLIENT_ID` - Reddit API Client ID
- `REDDIT_CLIENT_SECRET` - Reddit API Secret

## 🐛 故障排除

### 后端无法启动
```bash
# 检查虚拟环境
cd backend
source venv/bin/activate
python --version

# 检查依赖
pip list | grep fastapi
```

### 前端无法启动
```bash
# 检查 Node.js
node --version
pnpm --version

# 重新安装依赖
cd frontend
pnpm install
```

### 数据库连接失败
```bash
# 检查环境变量
cat frontend/.env | grep DATABASE_URL

# 测试连接
cd frontend
pnpm prisma db push
```

## 📞 获取帮助

1. 查看 API 文档：`http://localhost:8000/docs`
2. 查看部署清单：`DEPLOYMENT_CHECKLIST.md`
3. 检查日志：查看终端输出

---

**最后更新：** 2026-01-11  
**版本：** MVP 2.0
