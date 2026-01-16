# 🚀 MVP 3.1.0 部署指南 - Railway 后端

**版本**: 3.1.0  
**日期**: 2026-01-16  
**部署方案**: Vercel (前端) + Railway (后端 + PostgreSQL + Redis)

---

## 📋 架构概览

```
┌─────────────────┐
│  Vercel (前端)  │
│  Next.js 14     │
└────────┬────────┘
         │ HTTPS
         ▼
┌─────────────────┐
│ Railway (后端)  │
│  FastAPI 3.1.0  │
└────────┬────────┘
         │
    ┌────┴────┐
    ▼         ▼
┌─────────┐ ┌─────────┐
│Railway  │ │Railway  │
│PostgreSQL│ │  Redis  │
└─────────┘ └─────────┘
```

---

## 🎯 第一步：准备 Railway 项目

### 1. 创建 Railway 账户

1. **访问 Railway**
   - 前往 https://railway.app
   - 点击 "Start a New Project"
   - 使用 GitHub 账户登录（推荐）

2. **验证账户**
   - 完成邮箱验证
   - 选择免费计划或付费计划

---

## 🗄️ 第二步：创建 PostgreSQL 数据库

### 1. 添加 PostgreSQL 服务

1. **在 Railway Dashboard 中**：
   - 点击 "New Project"
   - 选择 "Empty Project"
   - 点击 "+ New" → "Database" → "Add PostgreSQL"

2. **获取数据库连接信息**：
   - Railway 会自动创建 PostgreSQL 实例
   - 在 PostgreSQL 服务的 "Variables" 标签页，找到 `DATABASE_URL`
   - 复制完整的连接字符串
   - 示例格式：
     ```
     postgresql://postgres:password@hostname.proxy.rlwy.net:port/railway
     ```

3. **验证数据库连接**（可选）：
   ```bash
   # 使用 psql 测试连接
   psql postgresql://postgres:password@hostname.proxy.rlwy.net:port/railway
   ```

---

## 🔴 第三步：创建 Redis 缓存服务

### 1. 添加 Redis 服务

1. **在同一个 Railway 项目中**：
   - 点击 "+ New" → "Database" → "Add Redis"

2. **获取 Redis 连接信息**：
   - Railway 会自动创建 Redis 实例
   - 在 Redis 服务的 "Variables" 标签页，找到 `REDIS_URL` 或 `REDISCLOUD_URL`
   - **重要**：如果看到 `redis.railway.internal`，这是内部域名
   - **解决方案**：查找公共域名版本的 URL（格式：`redis://default:password@ballast.proxy.rlwy.net:port`）
   - 示例（内部域名，不可用）：
     ```
     redis://default:password@redis.railway.internal:6379
     ```
   - 示例（公共域名，可用）：
     ```
     redis://default:eGYxYOZczvIoDKPjMVwlArItcyekdkwj@ballast.proxy.rlwy.net:15033
     ```

3. **验证 Redis 连接**（可选）：
   ```bash
   # 使用 redis-cli 测试连接
   redis-cli -u redis://default:password@ballast.proxy.rlwy.net:15033 ping
   # 应该返回: PONG
   ```

---

## 🚀 第四步：部署后端到 Railway

### 1. 添加后端服务

1. **在 Railway Dashboard 中**：
   - 在同一个项目中，点击 "+ New" → "GitHub Repo"
   - 选择你的 GitHub 仓库（`ejzhang101/trendforge_mvp3.1`）
   - Railway 会自动检测项目类型

2. **配置服务设置**：
   - Railway 会自动读取 `railway.json` 配置文件
   - 如果未自动检测，手动设置：
     - **Root Directory**: 留空（Railway 从仓库根目录开始）
     - **Build Command**: `cd backend && pip install -r requirements_v2.txt && python -m spacy download en_core_web_sm`
     - **Start Command**: `cd backend && python -m uvicorn app_v2:app --host 0.0.0.0 --port $PORT`

### 2. 验证 railway.json 配置

确保项目根目录有 `railway.json` 文件：

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
  },
  "env": {
    "PORT": "8000"
  }
}
```

### 3. 配置环境变量

在 Railway Dashboard → 后端服务 → Variables 中添加：

```bash
# 必需变量
PORT=8000
DATABASE_URL=postgresql://postgres:JUsqimUhdhHSOJhJyWpdPMbhyAokKNaq@caboose.proxy.rlwy.net:31013/railway
REDIS_URL=redis://default:eGYxYOZczvIoDKPjMVwlArItcyekdkwj@ballast.proxy.rlwy.net:15033

# API Keys
TWITTER_BEARER_TOKEN=你的Twitter_Bearer_Token
SERPAPI_KEY=ae0f9c0cb85d9ad79a93f65b7d6296e18d751babc56f03b41ddd163e5ff02599
YOUTUBE_API_KEY=AIzaSyBoIIM1_PHpMFnCyk5KtvnYGKfVnzJQ2lc
OPENAI_API_KEY=你的OpenAI_API_Key

# 可选变量（如果配置了）
REDDIT_CLIENT_ID=你的Reddit_Client_ID
REDDIT_CLIENT_SECRET=你的Reddit_Client_Secret
```

**重要提示**：
- `PORT` 变量 Railway 会自动设置，但可以手动指定
- `DATABASE_URL` 从 PostgreSQL 服务获取
- `REDIS_URL` 从 Redis 服务获取（使用公共域名版本）
- 所有 API Keys 需要手动配置

### 4. 连接服务依赖

1. **在 Railway Dashboard 中**：
   - 选择后端服务
   - 在 "Settings" 标签页，找到 "Service Dependencies"
   - 添加 PostgreSQL 服务作为依赖
   - 添加 Redis 服务作为依赖
   - 这样 Railway 会确保数据库和缓存服务先启动

### 5. 配置公共域名

1. **生成公共 URL**：
   - 在后端服务的 "Settings" 标签页
   - 找到 "Networking" 部分
   - 点击 "Generate Domain" 或 "Custom Domain"
   - Railway 会生成一个公共 URL，例如：`https://your-app.railway.app`
   - 复制此 URL，稍后用于前端配置

---

## 📊 第五步：验证部署

### 1. 检查构建日志

1. **在 Railway Dashboard 中**：
   - 选择后端服务
   - 点击 "Deployments" 标签页
   - 查看最新的部署日志
   - 确认构建成功，没有错误

2. **检查构建步骤**：
   - ✅ 依赖安装成功
   - ✅ spaCy 模型下载成功
   - ✅ 应用启动成功

### 2. 健康检查

```bash
# 使用 curl 测试健康检查端点
curl https://your-app.railway.app/health

# 应该返回：
# {
#   "status": "healthy",
#   "version": "3.1.0",
#   "services": {
#     "twitter": true,
#     "reddit": false,
#     "google_trends": true,
#     "serpapi": true,
#     "cache": true,
#     "prophet": true,
#     "script_generator": true
#   },
#   "capabilities": {
#     "nlp_analysis": true,
#     "social_media": true,
#     "intelligent_recommendations": true,
#     "time_series_prediction": true,
#     "script_generation": true
#   }
# }
```

### 3. 功能测试

#### 测试 1: 频道分析
```bash
# 测试分析端点（需要提供有效的请求体）
curl -X POST https://your-app.railway.app/api/v2/full-analysis \
  -H "Content-Type: application/json" \
  -d '{"videos": [...], "channel_data": {...}}'
```

#### 测试 2: Redis 缓存
- 查看健康检查响应中的 `"cache": true`
- 如果为 `false`，检查 `REDIS_URL` 配置

#### 测试 3: 数据库连接
- 查看部署日志，确认没有数据库连接错误
- 如果使用 Prisma，运行数据库迁移

---

## 🔧 第六步：配置前端（Vercel）

### 1. 更新前端环境变量

在 Vercel Dashboard → Settings → Environment Variables 中更新：

```bash
# 更新后端 URL
BACKEND_SERVICE_URL=https://your-app.railway.app

# 其他变量保持不变
DATABASE_URL=postgresql://postgres:JUsqimUhdhHSOJhJyWpdPMbhyAokKNaq@caboose.proxy.rlwy.net:31013/railway
YOUTUBE_API_KEY=AIzaSyBoIIM1_PHpMFnCyk5KtvnYGKfVnzJQ2lc
NEXT_PUBLIC_APP_URL=https://your-app.vercel.app
```

### 2. 重新部署前端

- 在 Vercel Dashboard 中，触发新的部署
- 或推送代码到 GitHub，Vercel 会自动部署

---

## 🐛 常见问题

### 1. 构建失败：找不到 requirements_v2.txt

**原因**: 构建上下文不正确

**解决方案**：
- 确保 `railway.json` 中的 `buildCommand` 包含 `cd backend`
- 检查 `backend/requirements_v2.txt` 文件是否存在
- 查看构建日志，确认工作目录

### 2. spaCy 模型下载失败

**原因**: 网络问题或构建超时

**解决方案**：
- 检查构建日志中的错误信息
- 确保 `requirements_v2.txt` 包含 `spacy>=3.7.0`
- 如果持续失败，可以尝试在构建命令中添加重试逻辑

### 3. Redis 连接失败

**原因**: 使用了内部域名或 URL 格式错误

**解决方案**：
- 确保使用公共域名版本的 Redis URL（`ballast.proxy.rlwy.net`）
- 检查 `REDIS_URL` 环境变量格式
- 验证 Redis 服务正在运行

### 4. 数据库连接失败

**原因**: `DATABASE_URL` 配置错误或数据库未启动

**解决方案**：
- 检查 `DATABASE_URL` 环境变量
- 确认 PostgreSQL 服务正在运行
- 验证数据库连接字符串格式
- 检查服务依赖配置

### 5. 端口冲突

**原因**: `PORT` 环境变量未正确设置

**解决方案**：
- Railway 会自动设置 `$PORT` 环境变量
- 确保启动命令使用 `$PORT` 而不是硬编码端口
- 检查 `railway.json` 中的 `startCommand`

### 6. 服务无法访问

**原因**: 未配置公共域名或网络设置错误

**解决方案**：
- 在 Railway Dashboard → Settings → Networking
- 生成公共域名或配置自定义域名
- 检查防火墙和网络设置

---

## 📝 部署检查清单

### Railway 后端
- [ ] Railway 账户已创建
- [ ] PostgreSQL 数据库已创建并运行
- [ ] Redis 服务已创建并运行（使用公共域名 URL）
- [ ] 后端服务已部署
- [ ] `railway.json` 配置正确
- [ ] 所有环境变量已配置
- [ ] 服务依赖已配置（PostgreSQL、Redis）
- [ ] 公共域名已生成
- [ ] 健康检查通过
- [ ] Redis 连接正常（`cache: true`）
- [ ] 数据库连接正常

### Vercel 前端
- [ ] `BACKEND_SERVICE_URL` 已更新为 Railway URL
- [ ] 所有环境变量已配置
- [ ] 前端已重新部署
- [ ] 前端可以正常访问后端 API

### 功能验证
- [ ] 频道分析功能正常
- [ ] 社交趋势收集正常
- [ ] AI 推荐功能正常
- [ ] Prophet 预测功能正常（如果启用）
- [ ] 脚本生成功能正常（如果配置了 OpenAI API Key）
- [ ] Redis 缓存正常工作

---

## 🔄 更新和维护

### 更新代码

1. **推送代码到 GitHub**：
   ```bash
   git add .
   git commit -m "Update: description"
   git push origin main
   ```

2. **Railway 自动部署**：
   - Railway 会自动检测 GitHub 推送
   - 触发新的构建和部署
   - 查看部署日志确认成功

### 查看日志

1. **在 Railway Dashboard 中**：
   - 选择后端服务
   - 点击 "Deployments" 标签页
   - 选择最新的部署
   - 查看构建日志和运行时日志

### 回滚部署

1. **在 Railway Dashboard 中**：
   - 选择后端服务
   - 点击 "Deployments" 标签页
   - 找到之前的成功部署
   - 点击 "Redeploy" 按钮

---

## 📚 相关文档

- `railway.json` - Railway 配置文件
- `DEPLOYMENT_CONFIG.md` - 环境变量配置参考
- `DEPLOYMENT_GUIDE.md` - 通用部署指南
- `DOCKERFILE_GUIDE.md` - Docker 部署指南（如果使用 Docker）

---

## 🎯 快速参考

### Railway 服务 URL
- **后端**: `https://your-app.railway.app`
- **健康检查**: `https://your-app.railway.app/health`

### 环境变量模板
```bash
PORT=8000
DATABASE_URL=postgresql://postgres:password@hostname.proxy.rlwy.net:port/railway
REDIS_URL=redis://default:password@ballast.proxy.rlwy.net:port
TWITTER_BEARER_TOKEN=your_token
SERPAPI_KEY=your_key
YOUTUBE_API_KEY=your_key
OPENAI_API_KEY=your_key
```

### 构建和启动命令
```bash
# Build Command
cd backend && pip install -r requirements_v2.txt && python -m spacy download en_core_web_sm

# Start Command
cd backend && python -m uvicorn app_v2:app --host 0.0.0.0 --port $PORT
```

---

**最后更新**: 2026-01-16  
**版本**: MVP 3.1.0  
**维护者**: TrendForge 开发团队
