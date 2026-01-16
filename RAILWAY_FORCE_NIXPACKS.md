# 🔧 强制 Railway 使用 NIXPACKS 的完整解决方案

## ❌ 问题

Railway 仍然使用 Docker 构建，导致 `pip: command not found` 错误。

## ✅ 完整解决方案

### 步骤 1: 在 Railway Dashboard 中手动设置

**这是最重要的步骤！**

1. **访问 Railway Dashboard**
   - 前往 https://railway.app/dashboard
   - 选择你的项目

2. **选择后端服务**
   - 点击后端服务（不是 PostgreSQL 或 Redis）

3. **进入 Settings**
   - 点击 "Settings" 标签页

4. **找到 Build & Deploy 部分**
   - 滚动到 "Build & Deploy" 部分

5. **检查 Builder 设置**
   - 找到 "Builder" 选项
   - **必须选择 "NIXPACKS"**（不是 Docker）
   - 如果显示 "Docker"，点击下拉菜单，选择 "NIXPACKS"

6. **保存设置**
   - 点击 "Save" 或 "Update"
   - 等待设置保存完成

7. **触发新部署**
   - 点击 "Deploy" 或 "Redeploy"
   - 或者推送新的代码到 GitHub

### 步骤 2: 验证配置文件

确保以下文件存在且正确：

#### railway.json
```json
{
  "$schema": "https://railway.app/railway.schema.json",
  "build": {
    "builder": "NIXPACKS",
    "buildCommand": "cd backend && pip install -r requirements_v2.txt && python -m spacy download en_core_web_sm"
  },
  "deploy": {
    "startCommand": "cd backend && python -m uvicorn app_v2:app --host 0.0.0.0 --port $PORT"
  }
}
```

#### nixpacks.toml
```toml
# Nixpacks configuration for Railway
[phases.setup]
nixPkgs = ["python39", "pip"]

[phases.install]
cmds = [
  "cd backend",
  "pip install -r requirements_v2.txt",
  "python -m spacy download en_core_web_sm"
]

[start]
cmd = "cd backend && python -m uvicorn app_v2:app --host 0.0.0.0 --port $PORT"
```

#### .railwayignore
```
Dockerfile
dockerfile
docker-compose.yml
docker-compose.yaml
```

### 步骤 3: 删除或重命名 Dockerfile（如果存在根目录）

如果根目录有 Dockerfile，Railway 可能会自动检测：

```bash
# 检查根目录是否有 Dockerfile
ls -la Dockerfile

# 如果有，重命名它（不要删除，以防需要）
mv Dockerfile Dockerfile.backup
```

### 步骤 4: 重新部署

1. **在 Railway Dashboard 中**：
   - 点击 "Deploy" 或 "Redeploy"
   - 或者等待 GitHub 推送触发自动部署

2. **查看构建日志**：
   - 在 "Deployments" 标签页查看最新部署
   - 确认日志显示 NIXPACKS 构建过程
   - 不应看到 Docker 构建步骤

### 步骤 5: 验证构建成功

构建日志应该显示：
- ✅ "Detected Python project"
- ✅ "Installing dependencies..."
- ✅ "Downloading spaCy model..."
- ✅ "Starting application..."

不应显示：
- ❌ "Docker build"
- ❌ "pip: command not found"
- ❌ "Dockerfile:15"

## 🚨 如果问题仍然存在

### 方案 A: 删除并重新创建服务

1. **删除当前服务**：
   - 在 Railway Dashboard 中
   - 选择后端服务
   - 点击 "Settings" → "Delete Service"

2. **重新创建服务**：
   - 点击 "+ New" → "GitHub Repo"
   - 选择你的仓库
   - **在创建时明确选择 "NIXPACKS" 构建器**
   - 不要选择 Docker

### 方案 B: 使用 Railway CLI

```bash
# 安装 Railway CLI
npm i -g @railway/cli

# 登录
railway login

# 链接项目
railway link

# 设置构建器为 NIXPACKS
railway variables set RAILWAY_BUILDER=NIXPACKS

# 部署
railway up
```

## 📝 检查清单

- [ ] Railway Dashboard → Settings → Builder 设置为 "NIXPACKS"
- [ ] `railway.json` 存在且 `"builder": "NIXPACKS"`
- [ ] `nixpacks.toml` 存在且配置正确
- [ ] `.railwayignore` 存在且包含 Dockerfile
- [ ] 根目录没有 Dockerfile（或已重命名）
- [ ] 所有配置文件已推送到 GitHub
- [ ] 已触发新部署
- [ ] 构建日志显示 NIXPACKS（不是 Docker）

## 🔍 调试技巧

### 查看构建日志

在 Railway Dashboard → Deployments → 最新部署 → Logs：

1. **查找构建器信息**：
   - 应该看到 "Using NIXPACKS builder"
   - 不应该看到 "Using Docker builder"

2. **查找 Python 环境**：
   - 应该看到 Python 版本信息
   - 应该看到 pip 安装过程

3. **查找错误**：
   - 如果看到 "pip: command not found"，说明仍在使用 Docker
   - 如果看到 "Dockerfile:15"，说明仍在使用 Docker

---

**最后更新**: 2026-01-16  
**版本**: MVP 3.1.0
