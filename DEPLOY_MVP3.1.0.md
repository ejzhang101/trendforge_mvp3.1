# 🚀 MVP 3.1.0 部署指南

**版本**: 3.1.0  
**日期**: 2026-01-14  
**新功能**: LLM 增强的智能脚本生成

---

## 📋 部署前准备

### ✅ 检查清单

- [x] 代码已提交到 Git（v3.1.0 标签）
- [x] 所有依赖已更新（包含 `openai>=1.3.0`）
- [x] 环境变量配置已更新
- [x] 配置文件已更新（`railway.json`, `vercel.json`）

---

## 🎯 部署方案：Vercel (前端) + Railway (后端)

### 第一步：后端部署到 Railway

#### 1. 访问 Railway Dashboard

1. 前往 https://railway.app
2. 登录你的账户
3. 选择现有的 TrendForge 项目（或创建新项目）

#### 2. 更新环境变量

在 Railway Dashboard → Variables 中添加/更新：

```bash
# 必需变量
TWITTER_BEARER_TOKEN=你的Twitter_Bearer_Token
SERPAPI_KEY=ae0f9c0cb85d9ad79a93f65b7d6296e18d751babc56f03b41ddd163e5ff02599
DATABASE_URL=你的PostgreSQL连接字符串
PORT=8000

# MVP 3.1.0 新增：LLM 脚本生成（可选但推荐）
OPENAI_API_KEY=sk-proj-你的OpenAI_API_Key

# 可选变量
REDDIT_CLIENT_ID=你的Reddit_Client_ID
REDDIT_CLIENT_SECRET=你的Reddit_Client_Secret
REDIS_URL=你的Redis连接URL（如果使用Redis）
```

**重要**：
- `OPENAI_API_KEY` 是可选的，如果不配置，脚本生成会使用模板方式（功能仍然可用）
- 如果配置了 `OPENAI_API_KEY`，脚本生成将使用 LLM 模式，生成更智能的内容

#### 3. 触发重新部署

1. 在 Railway Dashboard 中，点击 "Deployments"
2. 点击 "Redeploy" 或等待自动部署（如果已连接 GitHub）
3. 等待部署完成（通常 3-5 分钟）

#### 4. 验证后端部署

```bash
# 检查健康状态
curl https://your-backend.railway.app/health

# 应该返回：
# {
#   "status": "healthy",
#   "version": "3.1.0",
#   "capabilities": {
#     "script_generation": true,
#     ...
#   },
#   "services": {
#     "script_generator": true,
#     ...
#   }
# }
```

**检查点**：
- ✅ `version` 应该是 `"3.1.0"`
- ✅ `script_generation` 应该是 `true`
- ✅ 如果配置了 `OPENAI_API_KEY`，`script_generator` 应该是 `true`

#### 5. 获取后端 URL

- Railway 会提供一个公共 URL，例如：`https://your-app.railway.app`
- 复制此 URL，稍后用于前端配置

---

### 第二步：前端部署到 Vercel

#### 1. 访问 Vercel Dashboard

1. 前往 https://vercel.com
2. 登录你的账户
3. 选择现有的 TrendForge 项目（或导入新项目）

#### 2. 更新环境变量

在 Vercel Dashboard → Settings → Environment Variables 中添加/更新：

```bash
# 必需变量
DATABASE_URL=你的PostgreSQL连接字符串（与后端相同）
BACKEND_SERVICE_URL=https://your-backend.railway.app
YOUTUBE_API_KEY=你的YouTube_API_Key
NEXT_PUBLIC_APP_URL=https://your-app.vercel.app

# 可选变量
NODE_ENV=production
```

**重要**：
- `BACKEND_SERVICE_URL` 必须是后端在 Railway 上的 URL
- 确保 URL 以 `https://` 开头

#### 3. 触发重新部署

1. 在 Vercel Dashboard 中，点击 "Deployments"
2. 点击 "Redeploy" 或等待自动部署（如果已连接 GitHub）
3. 等待部署完成（通常 2-3 分钟）

#### 4. 验证前端部署

1. 访问 Vercel 提供的 URL
2. 检查页面是否正常加载
3. 测试完整分析流程
4. 测试脚本生成功能（在推荐话题详情弹窗中）

---

## 🔧 更新 CORS 配置（如果需要）

如果前端 URL 发生变化，需要更新后端的 CORS 配置。

在 `backend/app_v2.py` 中，确保包含前端域名：

```python
allowed_origins = [
    "http://localhost:3000",
    "https://*.vercel.app",
    "https://your-app.vercel.app"  # 添加你的实际域名
]
```

然后重新部署后端。

---

## 📊 部署后验证

### 1. 健康检查

**后端**：
```bash
curl https://your-backend.railway.app/health
```

**前端**：
- 访问 Vercel URL
- 检查控制台是否有错误

### 2. 功能测试

#### 测试 1: 频道分析
1. 输入一个 YouTube 频道标识符
2. 点击"开始分析"
3. 等待分析完成（30-60秒）
4. 检查结果页面是否正常显示

#### 测试 2: Prophet 预测
1. 在分析结果页面，检查推荐话题
2. 点击任意推荐话题
3. 切换到"7天趋势预测" Tab
4. 检查预测图表和置信度是否显示

#### 测试 3: LLM 脚本生成（MVP 3.1.0 新功能）
1. 在分析结果页面，点击任意推荐话题
2. 切换到"✍️ AI 脚本生成" Tab
3. 输入产品/服务描述（支持中英文）
4. 点击"生成脚本"
5. 检查是否生成了脚本内容

**预期结果**：
- 如果配置了 `OPENAI_API_KEY`：应该生成智能脚本（3-5秒）
- 如果未配置 `OPENAI_API_KEY`：应该使用模板生成脚本（< 1秒）

### 3. 性能检查

- **分析时间**：应在 60 秒内完成
- **脚本生成时间**：
  - LLM 模式：3-5 秒
  - 模板模式：< 1 秒
- **错误率**：检查 Vercel 和 Railway 的日志

---

## 🐛 常见问题

### 1. 脚本生成失败

**问题**：点击"生成脚本"后显示错误

**解决方案**：
- 检查后端日志，查看具体错误信息
- 如果使用 LLM 模式，确认 `OPENAI_API_KEY` 是否正确配置
- 检查 API Key 是否有效（余额是否充足）
- 如果 LLM 调用失败，系统会自动回退到模板模式

### 2. 后端版本不是 3.1.0

**问题**：健康检查显示版本不是 `3.1.0`

**解决方案**：
- 确认代码已更新到最新版本（v3.1.0 标签）
- 重新部署后端服务
- 检查 `backend/app_v2.py` 中的版本号

### 3. 前端无法连接后端

**问题**：前端显示 API 调用失败

**解决方案**：
- 检查 `BACKEND_SERVICE_URL` 环境变量是否正确
- 确认后端 CORS 配置包含前端域名
- 检查后端服务是否正在运行

### 4. LLM 功能未启用

**问题**：健康检查显示 `script_generator: false`

**解决方案**：
- 检查 `OPENAI_API_KEY` 环境变量是否配置
- 确认 API Key 格式正确（以 `sk-` 开头）
- 检查后端日志，查看初始化错误信息

---

## 📈 性能优化建议

### 1. 启用 Redis 缓存

如果尚未启用 Redis，建议添加 Redis 服务：
- 在 Railway 中添加 Redis 服务
- 配置 `REDIS_URL` 环境变量
- 这将显著提高社交趋势数据的响应速度

### 2. 监控 API 使用

- 监控 OpenAI API 的使用量和成本
- 设置使用量告警
- 考虑使用缓存减少重复调用

### 3. 数据库优化

- 定期清理旧的分析数据
- 优化数据库索引
- 监控数据库性能

---

## ✅ 部署完成检查

- [ ] 后端服务正常运行（版本 3.1.0）
- [ ] 前端服务正常运行
- [ ] 健康检查通过
- [ ] 频道分析功能正常
- [ ] Prophet 预测功能正常
- [ ] LLM 脚本生成功能正常（如果配置了 API Key）
- [ ] 环境变量配置正确
- [ ] CORS 配置正确
- [ ] 日志输出正常

---

## 🎉 部署成功！

恭喜！MVP 3.1.0 已成功部署上线。

**访问地址**：
- 前端：https://your-app.vercel.app
- 后端 API：https://your-backend.railway.app
- API 文档：https://your-backend.railway.app/docs

**新功能**：
- ✨ LLM 增强的智能脚本生成
- ✨ 中英文语义分析
- ✨ 个性化脚本内容

---

**最后更新**：2026-01-14  
**版本**：MVP 3.1.0 - Prophet + LLM Script Generation
