# 🚀 TrendForge 部署上线指南

## 📋 部署前检查清单

### ✅ 代码准备
- [x] 所有功能已实现并测试
- [x] SerpAPI 集成完成
- [x] Redis 缓存配置完成
- [x] 环境变量已配置
- [x] 依赖包已更新（包含 `google-search-results`）

### ✅ 配置文件
- [x] `vercel.json` - 前端部署配置
- [x] `railway.json` - 后端部署配置
- [x] `docker-compose.yml` - Docker 部署配置
- [x] `backend/Dockerfile` - 后端容器配置
- [x] `frontend/Dockerfile` - 前端容器配置

## 🎯 推荐部署方案：Vercel (前端) + Railway (后端)

### 第一步：后端部署到 Railway

#### 1. 准备 Railway 项目

1. **访问 Railway**
   - 前往 https://railway.app
   - 登录或注册账户

2. **创建新项目**
   - 点击 "New Project"
   - 选择 "Deploy from GitHub repo"
   - 连接你的 GitHub 仓库

3. **配置环境变量**
   
   在 Railway Dashboard → Variables 中添加：

   ```bash
   # 必需变量
   TWITTER_BEARER_TOKEN=你的Twitter_Bearer_Token
   SERPAPI_KEY=ae0f9c0cb85d9ad79a93f65b7d6296e18d751babc56f03b41ddd163e5ff02599
   DATABASE_URL=你的PostgreSQL连接字符串
   PORT=8000
   
   # MVP 3.1.0 新增：LLM 脚本生成（可选但推荐）
   OPENAI_API_KEY=你的OpenAI_API_Key
   
   # 可选变量（如果配置了）
   REDDIT_CLIENT_ID=你的Reddit_Client_ID
   REDDIT_CLIENT_SECRET=你的Reddit_Client_Secret
   REDIS_URL=你的Redis连接URL（如果使用Redis）
   ```

4. **配置 PostgreSQL 数据库**
   - 在 Railway 项目中添加 PostgreSQL 服务
   - Railway 会自动提供 `DATABASE_URL`
   - 复制该 URL 到环境变量

5. **配置 Redis（可选但推荐）**
   - 在 Railway 项目中添加 Redis 服务
   - 复制 Redis URL 到环境变量 `REDIS_URL`

6. **部署设置**
   - Railway 会自动检测 `railway.json` 配置
   - 构建命令：`cd backend && pip install -r requirements_v2.txt && python -m spacy download en_core_web_sm`
   - 启动命令：`cd backend && python -m uvicorn app_v2:app --host 0.0.0.0 --port $PORT`

7. **获取后端 URL**
   - 部署完成后，Railway 会提供一个公共 URL
   - 例如：`https://your-app.railway.app`
   - 复制此 URL，稍后用于前端配置

#### 2. 验证后端部署

```bash
# 检查健康状态
curl https://your-app.railway.app/health

# 应该返回：
# {
#   "status": "healthy",
#   "services": {
#     "serpapi": true,
#     "cache": true,
#     ...
#   }
# }
```

### 第二步：前端部署到 Vercel

#### 1. 准备 Vercel 项目

1. **访问 Vercel**
   - 前往 https://vercel.com
   - 登录或注册账户

2. **导入项目**
   - 点击 "Add New Project"
   - 选择 "Import Git Repository"
   - 连接你的 GitHub 仓库

3. **配置项目设置**
   - Framework Preset: Next.js
   - Root Directory: `frontend`
   - Build Command: `pnpm install && pnpm build`
   - Output Directory: `.next`

4. **配置环境变量**
   
   在 Vercel Dashboard → Settings → Environment Variables 中添加：

   ```bash
   # 必需变量
   DATABASE_URL=你的PostgreSQL连接字符串（与后端相同）
   BACKEND_SERVICE_URL=https://your-app.railway.app
   YOUTUBE_API_KEY=你的YouTube_API_Key
   NEXT_PUBLIC_APP_URL=https://your-app.vercel.app
   
   # 可选变量
   NODE_ENV=production
   ```

5. **部署**
   - 点击 "Deploy"
   - Vercel 会自动构建和部署
   - 等待部署完成（通常 2-5 分钟）

#### 2. 配置数据库迁移

部署完成后，需要在 Vercel 中运行数据库迁移：

1. **使用 Vercel CLI**（推荐）
   ```bash
   # 安装 Vercel CLI
   npm i -g vercel
   
   # 登录
   vercel login
   
   # 链接项目
   cd frontend
   vercel link
   
   # 运行数据库迁移
   vercel env pull .env.local
   pnpm prisma db push
   ```

2. **或使用 Vercel 的 Post Deploy Hook**
   - 在 `vercel.json` 中添加：
   ```json
   {
     "buildCommand": "cd frontend && pnpm install && pnpm build",
     "installCommand": "cd frontend && pnpm install",
     "framework": "nextjs",
     "outputDirectory": "frontend/.next",
     "hooks": {
       "postDeploy": "cd frontend && pnpm prisma db push"
     }
   }
   ```

#### 3. 验证前端部署

- 访问 Vercel 提供的 URL
- 测试完整分析流程
- 检查控制台是否有错误

## 🔧 替代部署方案

### 方案 2: Docker 部署

#### 1. 更新环境变量

创建 `.env` 文件（不要提交到 Git）：

```bash
# 后端环境变量
TWITTER_BEARER_TOKEN=你的Token
SERPAPI_KEY=ae0f9c0cb85d9ad79a93f65b7d6296e18d751babc56f03b41ddd163e5ff02599
REDIS_URL=redis://localhost:6379
DATABASE_URL=postgresql://user:password@localhost:5432/trendforge

# 前端环境变量
BACKEND_SERVICE_URL=http://localhost:8000
YOUTUBE_API_KEY=你的Key
NEXT_PUBLIC_APP_URL=http://localhost:3000
```

#### 2. 构建和启动

```bash
# 构建镜像
docker-compose build

# 启动服务
docker-compose up -d

# 查看日志
docker-compose logs -f

# 停止服务
docker-compose down
```

### 方案 3: 本地生产部署

#### 后端

```bash
cd backend
source venv/bin/activate

# 安装生产依赖
pip install gunicorn

# 使用 gunicorn 启动（多进程）
gunicorn app_v2:app \
  -w 4 \
  -k uvicorn.workers.UvicornWorker \
  -b 0.0.0.0:8000 \
  --timeout 300 \
  --access-logfile - \
  --error-logfile -
```

#### 前端

```bash
cd frontend

# 构建
pnpm build

# 启动生产服务器
pnpm start
```

## 📊 部署后验证

### 1. 健康检查

```bash
# 后端健康检查
curl https://your-backend.railway.app/health

# 应该返回：
# {
#   "status": "healthy",
#   "services": {
#     "serpapi": true,
#     "cache": true,
#     "twitter": true,
#     "google_trends": true
#   }
# }
```

### 2. 功能测试

1. **访问前端**
   - 打开 Vercel 提供的 URL
   - 检查页面是否正常加载

2. **测试分析功能**
   - 输入一个 YouTube 频道标识符
   - 点击"开始分析"
   - 等待分析完成（30-60秒）
   - 检查结果页面是否正常显示

3. **检查 API 调用**
   - 打开浏览器开发者工具
   - 查看 Network 标签
   - 确认 API 调用成功

### 3. 性能监控

- **响应时间**：完整分析应在 60 秒内完成
- **错误率**：检查 Vercel 和 Railway 的日志
- **资源使用**：监控 Railway 的 CPU 和内存使用

## 🔐 安全配置

### 1. 环境变量安全

- ✅ 所有敏感信息存储在环境变量中
- ✅ 不要将 `.env` 文件提交到 Git
- ✅ 使用 Vercel 和 Railway 的环境变量管理

### 2. CORS 配置

后端已配置 CORS，允许来自 Vercel 域名的请求：

```python
allowed_origins = [
    "http://localhost:3000",
    "https://*.vercel.app",
    "https://your-app.vercel.app"  # 添加你的实际域名
]
```

### 3. API 密钥保护

- ✅ API 密钥存储在环境变量中
- ✅ 前端不直接访问敏感 API
- ✅ 所有 API 调用通过后端代理

## 🐛 常见问题

### 1. 后端部署失败

**问题**：构建失败或启动失败

**解决方案**：
- 检查 `requirements_v2.txt` 是否包含所有依赖
- 确认 `railway.json` 配置正确
- 查看 Railway 日志找出具体错误

### 2. 前端构建失败

**问题**：Vercel 构建失败

**解决方案**：
- 检查 `package.json` 中的依赖
- 确认 `vercel.json` 配置正确
- 查看 Vercel 构建日志

### 3. 数据库连接失败

**问题**：无法连接到 PostgreSQL

**解决方案**：
- 确认 `DATABASE_URL` 环境变量正确
- 检查数据库是否在运行
- 确认网络连接和防火墙设置

### 4. API 调用失败

**问题**：前端无法调用后端 API

**解决方案**：
- 确认 `BACKEND_SERVICE_URL` 环境变量正确
- 检查 CORS 配置
- 确认后端服务正在运行

## 📈 部署后优化

### 1. 性能优化

- [ ] 启用 Redis 缓存（如果尚未启用）
- [ ] 配置 CDN（Vercel 自动提供）
- [ ] 优化数据库查询
- [ ] 添加响应缓存

### 2. 监控和日志

- [ ] 配置错误监控（如 Sentry）
- [ ] 设置性能监控
- [ ] 配置日志聚合
- [ ] 设置告警通知

### 3. 扩展性

- [ ] 配置自动扩缩容
- [ ] 优化数据库索引
- [ ] 考虑使用消息队列（如 Celery）
- [ ] 实现负载均衡

## ✅ 部署完成检查

- [ ] 后端服务正常运行
- [ ] 前端服务正常运行
- [ ] 数据库连接正常
- [ ] 所有 API 端点可访问
- [ ] 完整分析流程测试通过
- [ ] 健康检查通过
- [ ] 环境变量配置正确
- [ ] 日志输出正常
- [ ] 错误处理正常

## 🎉 部署成功！

恭喜！你的 TrendForge 应用已成功部署上线。

**访问地址：**
- 前端：https://your-app.vercel.app
- 后端 API：https://your-app.railway.app
- API 文档：https://your-app.railway.app/docs

---

**最后更新**：2026-01-13  
**版本**：MVP 2.0 with SerpAPI Integration
