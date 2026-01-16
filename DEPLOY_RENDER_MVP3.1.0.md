# 🚀 MVP 3.1.0 部署指南 - Render 后端

**版本**: 3.1.0  
**日期**: 2026-01-14  
**部署方案**: Vercel (前端) + Render (后端) + Railway (PostgreSQL + Redis)

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
│  Render (后端)  │
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

## 🎯 部署步骤

### 第一步：配置 Railway PostgreSQL 和 Redis

#### 1. 创建 PostgreSQL 数据库（Railway）

1. **访问 Railway**
   - 前往 https://railway.app
   - 登录你的账户

2. **创建新项目或使用现有项目**
   - 点击 "New Project"
   - 选择 "New Database" → "PostgreSQL"

3. **获取数据库连接信息**
   - Railway 会自动创建数据库
   - 在数据库服务的 "Variables" 标签页，找到 `DATABASE_URL`
   - 复制完整的连接字符串，格式如下：
     ```
     postgresql://postgres:password@hostname.railway.app:port/railway
     ```

#### 2. 创建 Redis 服务（Railway）

1. **添加 Redis 服务**
   - 在同一个 Railway 项目中，点击 "+ New"
   - 选择 "Database" → "Add Redis"

2. **获取 Redis 连接信息**
   - Railway 会自动创建 Redis 实例
   - 在 Redis 服务的 "Variables" 标签页，找到 `REDIS_URL` 或 `REDISCLOUD_URL`
   - **重要**：如果看到 `redis.railway.internal`，这是内部域名，在 Render 上无法访问
   - **解决方案**：查找公共域名版本的 URL（格式：`redis://default:password@ballast.proxy.rlwy.net:port`）
   - 示例（内部域名，不可用）：
     ```
     redis://default:password@redis.railway.internal:6379
     ```
   - 示例（公共域名，可用）：
     ```
     redis://default:eGYxYOZczvIoDKPjMVwlArItcyekdkwj@ballast.proxy.rlwy.net:15033
     ```

3. **验证 Redis 连接**
   ```bash
   # 使用 redis-cli 测试连接（本地）
   redis-cli -u redis://:password@hostname.railway.app:port ping
   # 应该返回: PONG
   ```

---

### 第二步：部署后端到 Render

#### 1. 准备 Render 项目

1. **访问 Render**
   - 前往 https://render.com
   - 登录或注册账户

2. **创建新 Web Service**
   - 点击 "New +" → "Web Service"
   - 选择 "Build and deploy from a Git repository"
   - 连接你的 GitHub 仓库

#### 2. 配置构建和启动命令

在 Render Dashboard 的配置页面：

**Build Command**:
```bash
cd backend && pip install -r requirements_v2.txt && python -m spacy download en_core_web_sm
```

**Start Command**:
```bash
cd backend && python -m uvicorn app_v2:app --host 0.0.0.0 --port $PORT
```

**Environment**:
- 选择 `Python 3`

**Root Directory**:
- 留空（Render 会从仓库根目录开始）

#### 3. 配置环境变量

在 Render Dashboard → Environment Variables 中添加：

```bash
# 必需变量
PORT=10000
DATABASE_URL=postgresql://postgres:JUsqimUhdhHSOJhJyWpdPMbhyAokKNaq@caboose.proxy.rlwy.net:31013/railway
REDIS_URL=redis://default:eGYxYOZczvIoDKPjMVwlArItcyekdkwj@ballast.proxy.rlwy.net:15033

# API Keys
TWITTER_BEARER_TOKEN=你的Twitter_Bearer_Token
SERPAPI_KEY=ae0f9c0cb85d9ad79a93f65b7d6296e18d751babc56f03b41ddd163e5ff02599
YOUTUBE_API_KEY=AIzaSyBoIIM1_PHpMFnCyk5KtvnYGKfVnzJQ2lc

# MVP 3.1.0 新增：LLM 脚本生成（可选但推荐）
OPENAI_API_KEY=你的OpenAI_API_Key

# 可选变量
REDDIT_CLIENT_ID=你的Reddit_Client_ID
REDDIT_CLIENT_SECRET=你的Reddit_Client_Secret

# CORS 配置（可选，如果需要自定义）
ALLOWED_ORIGINS=https://your-app.vercel.app
```

**重要提示**：
- `PORT` 在 Render 中通常是 `10000`，但 Render 会自动设置 `$PORT` 环境变量
- `DATABASE_URL` 从 Railway PostgreSQL 服务获取
- `REDIS_URL` 从 Railway Redis 服务获取
- `OPENAI_API_KEY` 是可选的，如果不配置，脚本生成会使用模板方式

#### 4. 配置自动部署

1. **自动部署设置**
   - 在 Render Dashboard → Settings → Auto-Deploy
   - 选择 "Yes" 启用自动部署
   - 选择要部署的分支（通常是 `main` 或 `master`）

2. **部署触发**
   - Render 会在每次 Git push 时自动部署
   - 也可以手动点击 "Manual Deploy"

#### 5. 获取后端 URL

- Render 会提供一个公共 URL，例如：`https://your-app.onrender.com`
- 复制此 URL，稍后用于前端配置

#### 6. 验证后端部署

```bash
# 检查健康状态
curl https://your-app.onrender.com/health

# 应该返回：
# {
#   "status": "healthy",
#   "version": "3.1.0",
#   "capabilities": {
#     "script_generation": true,
#     "caching": true,
#     ...
#   },
#   "services": {
#     "cache": true,
#     "script_generator": true,
#     ...
#   }
# }
```

**检查点**：
- ✅ `version` 应该是 `"3.1.0"`
- ✅ `script_generation` 应该是 `true`
- ✅ `cache` 应该是 `true`（如果 Redis 配置正确）
- ✅ 如果配置了 `OPENAI_API_KEY`，`script_generator` 应该是 `true`

---

### 第三步：部署前端到 Vercel

#### 1. 访问 Vercel Dashboard

1. 前往 https://vercel.com
2. 登录你的账户
3. 选择现有的 TrendForge 项目（或导入新项目）

#### 2. 更新环境变量

在 Vercel Dashboard → Settings → Environment Variables 中添加/更新：

```bash
# 必需变量
DATABASE_URL=postgresql://postgres:JUsqimUhdhHSOJhJyWpdPMbhyAokKNaq@caboose.proxy.rlwy.net:31013/railway
BACKEND_SERVICE_URL=https://your-app.onrender.com
YOUTUBE_API_KEY=AIzaSyBoIIM1_PHpMFnCyk5KtvnYGKfVnzJQ2lc
NEXT_PUBLIC_APP_URL=https://your-app.vercel.app

# 可选变量
NODE_ENV=production
```

**重要**：
- `BACKEND_SERVICE_URL` 必须是后端在 Render 上的 URL
- `DATABASE_URL` 与后端使用相同的 Railway PostgreSQL 连接字符串

#### 3. 触发重新部署

1. 在 Vercel Dashboard 中，点击 "Deployments"
2. 点击 "Redeploy" 或等待自动部署
3. 等待部署完成（通常 2-3 分钟）

---

## 🔧 Redis 配置详解

### Railway Redis 连接字符串格式

Railway 提供的 Redis URL 通常有以下格式：

```
redis://default:password@hostname.railway.app:port
```

或者：

```
redis://:password@hostname.railway.app:port
```

### 在 Render 中配置 REDIS_URL

1. **获取 Redis URL**
   - 在 Railway Dashboard → Redis 服务 → Variables
   - 找到 `REDIS_URL` 或 `REDISCLOUD_URL`
   - 复制完整的连接字符串

2. **添加到 Render 环境变量**
   - 在 Render Dashboard → Environment Variables
   - 添加 `REDIS_URL`，值为从 Railway 复制的连接字符串

3. **验证 Redis 连接**

   在 Render 的日志中，应该看到：
   ```
   ✅ Redis cache connected
   ```

   或者在健康检查中：
   ```json
   {
     "services": {
       "cache": true
     }
   }
   ```

### Redis 连接测试

如果需要在本地测试 Redis 连接：

```bash
# 使用 redis-cli
redis-cli -u redis://default:eGYxYOZczvIoDKPjMVwlArItcyekdkwj@ballast.proxy.rlwy.net:15033 ping

# 或使用 Python
python -c "
import redis
r = redis.from_url('redis://default:eGYxYOZczvIoDKPjMVwlArItcyekdkwj@ballast.proxy.rlwy.net:15033')
print(r.ping())  # 应该输出: True
"
```

---

## 📊 部署后验证

### 1. 健康检查

**后端（Render）**：
```bash
curl https://your-app.onrender.com/health
```

**检查项**：
- ✅ `status`: `"healthy"`
- ✅ `version`: `"3.1.0"`
- ✅ `services.cache`: `true`（如果 Redis 配置正确）
- ✅ `services.script_generator`: `true`（如果配置了 OpenAI API Key）

### 2. 功能测试

#### 测试 1: 频道分析
1. 访问前端 URL
2. 输入 YouTube 频道标识符
3. 点击"开始分析"
4. 等待分析完成（30-60秒）
5. 检查结果页面

#### 测试 2: Redis 缓存
1. 执行一次完整的频道分析
2. 立即再次分析同一个频道
3. 第二次分析应该更快（使用缓存）
4. 检查后端日志，应该看到缓存命中

#### 测试 3: LLM 脚本生成
1. 在分析结果页面，点击推荐话题
2. 切换到"✍️ AI 脚本生成" Tab
3. 输入产品描述
4. 点击"生成脚本"
5. 检查是否生成了脚本内容

### 3. 性能检查

- **分析时间**：应在 60 秒内完成
- **缓存命中率**：第二次分析应明显更快
- **脚本生成时间**：
  - LLM 模式：3-5 秒
  - 模板模式：< 1 秒

---

## 🐛 常见问题

### 1. Redis 连接失败

**问题**：健康检查显示 `cache: false`

**解决方案**：
- 检查 `REDIS_URL` 环境变量是否正确
- 确认 Redis URL 格式正确（包含密码和端口）
- 检查 Railway Redis 服务是否运行
- 查看 Render 日志，查找 Redis 连接错误

### 2. 后端无法连接数据库

**问题**：数据库连接失败

**解决方案**：
- 检查 `DATABASE_URL` 环境变量
- 确认 Railway PostgreSQL 服务正在运行
- 检查数据库连接字符串格式
- 确认数据库允许外部连接

### 3. Render 部署失败

**问题**：构建或启动失败

**解决方案**：
- 检查构建命令是否正确
- 确认 `requirements_v2.txt` 包含所有依赖
- 查看 Render 构建日志
- 确认 Python 版本兼容（3.9+）

### 4. 前端无法连接后端

**问题**：API 调用失败

**解决方案**：
- 检查 `BACKEND_SERVICE_URL` 环境变量
- 确认后端 CORS 配置包含前端域名
- 检查 Render 服务是否正在运行
- 查看浏览器控制台错误信息

---

## 🔐 安全配置

### 1. 环境变量安全

- ✅ 所有敏感信息存储在环境变量中
- ✅ 不要将 `.env` 文件提交到 Git
- ✅ 使用 Render 和 Vercel 的环境变量管理
- ✅ 定期轮换 API 密钥

### 2. CORS 配置

后端已配置 CORS，允许来自 Vercel 域名的请求。如果需要添加自定义域名，在 Render 环境变量中添加：

```bash
ALLOWED_ORIGINS=https://your-app.vercel.app,https://your-custom-domain.com
```

### 3. 数据库安全

- ✅ 使用强密码
- ✅ 限制数据库访问 IP（如果可能）
- ✅ 定期备份数据库
- ✅ 监控数据库访问日志

---

## 📈 性能优化

### 1. Render 配置优化

- **实例类型**：选择适合的实例类型（Starter 或 Standard）
- **自动扩缩容**：启用自动扩缩容以应对流量高峰
- **健康检查**：配置健康检查端点 `/health`

### 2. Redis 缓存优化

- ✅ 已启用 Redis 缓存
- ✅ 社交趋势数据缓存 1 小时
- ✅ 频道分析数据缓存 24 小时
- 监控缓存命中率

### 3. 数据库优化

- 定期清理旧数据
- 优化数据库索引
- 监控查询性能
- 考虑使用连接池

---

## ✅ 部署完成检查清单

- [ ] Railway PostgreSQL 数据库已创建并运行
- [ ] Railway Redis 服务已创建并运行
- [ ] Render 后端服务已部署（版本 3.1.0）
- [ ] 所有环境变量已配置
- [ ] Redis 连接正常（`cache: true`）
- [ ] 数据库连接正常
- [ ] Vercel 前端服务已部署
- [ ] 健康检查通过
- [ ] 频道分析功能正常
- [ ] Prophet 预测功能正常
- [ ] LLM 脚本生成功能正常（如果配置了 API Key）
- [ ] Redis 缓存正常工作

---

## 🎉 部署成功！

恭喜！MVP 3.1.0 已成功部署到 Render。

**访问地址**：
- 前端：https://your-app.vercel.app
- 后端 API：https://your-app.onrender.com
- API 文档：https://your-app.onrender.com/docs

**服务状态**：
- ✅ PostgreSQL：Railway
- ✅ Redis：Railway
- ✅ 后端：Render
- ✅ 前端：Vercel

---

**最后更新**：2026-01-14  
**版本**：MVP 3.1.0 - Prophet + LLM Script Generation  
**部署平台**：Render (后端) + Vercel (前端) + Railway (数据库 + Redis)
