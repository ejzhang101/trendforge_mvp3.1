# 🚀 TrendForge 部署指南

## 📋 部署概览

TrendForge 是一个全栈应用，包含：
- **后端**：FastAPI (Python) - 运行在 `http://localhost:8000`
- **前端**：Next.js (TypeScript) - 运行在 `http://localhost:3000`
- **数据库**：PostgreSQL (Railway)

## 🎯 部署选项

### 选项 1: Vercel (前端) + Railway (后端) - 推荐

#### 前端部署 (Vercel)

1. **准备部署**
   ```bash
   cd frontend
   pnpm build  # 确保构建成功
   ```

2. **部署到 Vercel**
   ```bash
   # 安装 Vercel CLI
   npm i -g vercel
   
   # 登录 Vercel
   vercel login
   
   # 部署
   cd frontend
   vercel
   
   # 生产环境部署
   vercel --prod
   ```

3. **环境变量配置 (Vercel Dashboard)**
   - 访问 https://vercel.com/dashboard
   - 选择项目 → Settings → Environment Variables
   - 添加以下变量：
     ```
     DATABASE_URL=postgresql://postgres:...@caboose.proxy.rlwy.net:31013/railway
     BACKEND_SERVICE_URL=https://your-backend-url.railway.app
     YOUTUBE_API_KEY=AIzaSyBoIIM1_PHpMFnCyk5KtvnYGKfVnzJQ2lc
     NEXT_PUBLIC_APP_URL=https://your-app.vercel.app
     ```

4. **创建 `vercel.json` 配置文件**
   ```json
   {
     "buildCommand": "cd frontend && pnpm install && pnpm build",
     "outputDirectory": "frontend/.next",
     "framework": "nextjs",
     "installCommand": "cd frontend && pnpm install"
   }
   ```

#### 后端部署 (Railway)

1. **准备部署文件**
   ```bash
   cd backend
   ```

2. **创建 `Procfile`** (如果使用 Railway)
   ```
   web: cd backend && source venv/bin/activate && python app_v2.py
   ```
   或者使用 Railway 的配置：
   ```json
   {
     "build": {
       "builder": "NIXPACKS"
     },
     "deploy": {
       "startCommand": "cd backend && python -m uvicorn app_v2:app --host 0.0.0.0 --port $PORT"
     }
   }
   ```

3. **创建 `railway.json`** (可选)
   ```json
   {
     "$schema": "https://railway.app/railway.schema.json",
     "build": {
       "builder": "NIXPACKS",
       "buildCommand": "cd backend && pip install -r requirements_v2.txt && python -m spacy download en_core_web_sm"
     },
     "deploy": {
       "startCommand": "cd backend && python -m uvicorn app_v2:app --host 0.0.0.0 --port $PORT",
       "restartPolicyType": "ON_FAILURE",
       "restartPolicyMaxRetries": 10
     }
   }
   ```

4. **环境变量配置 (Railway Dashboard)**
   - 访问 https://railway.app/dashboard
   - 选择项目 → Variables
   - 添加以下变量：
     ```
     TWITTER_BEARER_TOKEN=AAAAAAAAAAAAAAAAAAAAAM1%2F6wEAAAAAQN3FzEVmrO5hB4S2gHftxysFitE%3DwZvqP0Vpj1WxpiqBjyqRrB7DEyNM37nJQ2wwqHnDWEQDJ8RVo2
     REDDIT_CLIENT_ID=
     REDDIT_CLIENT_SECRET=
     DATABASE_URL=postgresql://postgres:...@caboose.proxy.rlwy.net:31013/railway
     PORT=8000
     ```

5. **部署步骤**
   - 在 Railway 创建新项目
   - 连接 GitHub 仓库（或直接部署）
   - Railway 会自动检测 Python 项目并构建
   - 确保设置正确的启动命令

### 选项 2: Docker 部署

#### 创建 Dockerfile

**后端 Dockerfile** (`backend/Dockerfile`):
```dockerfile
FROM python:3.9-slim

WORKDIR /app

# 安装系统依赖
RUN apt-get update && apt-get install -y \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

# 复制依赖文件
COPY requirements_v2.txt .

# 安装 Python 依赖
RUN pip install --no-cache-dir -r requirements_v2.txt

# 下载 spaCy 模型
RUN python -m spacy download en_core_web_sm

# 复制应用代码
COPY . .

# 暴露端口
EXPOSE 8000

# 启动命令
CMD ["python", "-m", "uvicorn", "app_v2:app", "--host", "0.0.0.0", "--port", "8000"]
```

**前端 Dockerfile** (`frontend/Dockerfile`):
```dockerfile
FROM node:18-alpine AS base

# 安装 pnpm
RUN npm install -g pnpm

FROM base AS deps
WORKDIR /app
COPY frontend/package.json frontend/pnpm-lock.yaml ./
RUN pnpm install --frozen-lockfile

FROM base AS builder
WORKDIR /app
COPY --from=deps /app/node_modules ./node_modules
COPY frontend .
RUN pnpm build

FROM base AS runner
WORKDIR /app
ENV NODE_ENV production
COPY --from=builder /app/public ./public
COPY --from=builder /app/.next/standalone ./
COPY --from=builder /app/.next/static ./.next/static

EXPOSE 3000
ENV PORT 3000

CMD ["node", "server.js"]
```

**docker-compose.yml** (根目录):
```yaml
version: '3.8'

services:
  backend:
    build:
      context: ./backend
      dockerfile: Dockerfile
    ports:
      - "8000:8000"
    environment:
      - TWITTER_BEARER_TOKEN=${TWITTER_BEARER_TOKEN}
      - REDDIT_CLIENT_ID=${REDDIT_CLIENT_ID}
      - REDDIT_CLIENT_SECRET=${REDDIT_CLIENT_SECRET}
      - DATABASE_URL=${DATABASE_URL}
    volumes:
      - ./backend:/app
    restart: unless-stopped

  frontend:
    build:
      context: ./frontend
      dockerfile: Dockerfile
    ports:
      - "3000:3000"
    environment:
      - DATABASE_URL=${DATABASE_URL}
      - BACKEND_SERVICE_URL=http://backend:8000
      - YOUTUBE_API_KEY=${YOUTUBE_API_KEY}
      - NEXT_PUBLIC_APP_URL=http://localhost:3000
    depends_on:
      - backend
    restart: unless-stopped
```

#### 使用 Docker 部署

```bash
# 构建和启动
docker-compose up -d

# 查看日志
docker-compose logs -f

# 停止
docker-compose down
```

### 选项 3: 本地生产部署

#### 后端部署

```bash
cd backend

# 1. 激活虚拟环境
source venv/bin/activate

# 2. 安装依赖
pip install -r requirements_v2.txt

# 3. 使用 gunicorn 或 uvicorn 生产模式
pip install gunicorn
gunicorn app_v2:app -w 4 -k uvicorn.workers.UvicornWorker -b 0.0.0.0:8000

# 或使用 uvicorn
uvicorn app_v2:app --host 0.0.0.0 --port 8000 --workers 4
```

#### 前端部署

```bash
cd frontend

# 1. 安装依赖
pnpm install

# 2. 构建
pnpm build

# 3. 启动生产服务器
pnpm start
```

## 🔧 部署前检查清单

### 后端检查

- [ ] 所有环境变量已配置
- [ ] `requirements_v2.txt` 包含所有依赖
- [ ] spaCy 模型已下载 (`en_core_web_sm`)
- [ ] API 密钥已配置（Twitter, Reddit, YouTube）
- [ ] 数据库连接正常
- [ ] CORS 配置正确（允许前端域名）

### 前端检查

- [ ] 所有环境变量已配置
- [ ] `package.json` 依赖完整
- [ ] Prisma schema 已同步 (`pnpm prisma db push`)
- [ ] 构建成功 (`pnpm build`)
- [ ] 后端 URL 配置正确

### 数据库检查

- [ ] PostgreSQL 数据库可访问
- [ ] 数据库迁移已完成
- [ ] 连接字符串正确

## 🌐 生产环境配置

### 后端 CORS 配置

在 `backend/app_v2.py` 中更新 CORS：

```python
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:3000",
        "https://your-app.vercel.app",  # 添加生产域名
        "https://*.vercel.app"  # 允许所有 Vercel 子域名
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
```

### 前端环境变量

创建 `frontend/.env.production`:
```
DATABASE_URL=postgresql://postgres:...@caboose.proxy.rlwy.net:31013/railway
BACKEND_SERVICE_URL=https://your-backend-url.railway.app
YOUTUBE_API_KEY=AIzaSyBoIIM1_PHpMFnCyk5KtvnYGKfVnzJQ2lc
NEXT_PUBLIC_APP_URL=https://your-app.vercel.app
```

## 📝 部署步骤总结

### Vercel + Railway 部署流程

1. **部署后端到 Railway**
   ```bash
   # 1. 在 Railway 创建新项目
   # 2. 连接 GitHub 仓库
   # 3. 设置环境变量
   # 4. 部署
   ```

2. **部署前端到 Vercel**
   ```bash
   # 1. 在 Vercel 创建新项目
   # 2. 连接 GitHub 仓库
   # 3. 设置环境变量（包括后端 URL）
   # 4. 部署
   ```

3. **更新 CORS 配置**
   - 在后端添加前端生产域名到 CORS 允许列表

4. **测试**
   - 访问前端 URL
   - 测试频道分析功能
   - 检查 API 连接

## 🐛 常见问题

### 1. 后端无法连接数据库
- 检查 `DATABASE_URL` 环境变量
- 确认数据库允许外部连接
- 检查防火墙设置

### 2. 前端无法连接后端
- 检查 `BACKEND_SERVICE_URL` 环境变量
- 确认后端 CORS 配置
- 检查后端服务是否运行

### 3. 构建失败
- 检查依赖是否完整
- 查看构建日志
- 确认 Node.js/Python 版本

### 4. API 密钥错误
- 检查环境变量是否正确设置
- 确认 API 密钥有效
- 检查 URL 编码（Twitter token）

## 📞 支持

如有问题，请检查：
- 部署日志
- 环境变量配置
- 服务健康检查端点：`/health`
