# 🚨 Railway 强制禁用 Docker 构建器 - 紧急解决方案

## ❌ 当前问题

Railway 仍然使用 Docker 构建，导致 `pip: command not found` 错误。

错误信息显示：
```
Dockerfile:20
RUN  pip install -r requirements_v2.txt
/bin/bash: line 1: pip: command not found
```

这说明 Railway **仍然在使用 Docker 构建器**，而不是 NIXPACKS。

## ✅ 立即解决方案

### 方案 1：在 Railway Dashboard 中强制切换（最重要！）

**这是最关键的步骤，必须在 Railway Dashboard 中手动操作：**

1. **访问 Railway Dashboard**
   - https://railway.app/dashboard
   - 选择你的项目

2. **选择后端服务**
   - 点击后端服务（不是 PostgreSQL 或 Redis）

3. **进入 Settings**
   - 点击 "Settings" 标签页
   - 滚动到 "Build & Deploy" 部分

4. **检查 Builder 设置**
   - 找到 "Builder" 选项
   - **如果显示 "Docker" 或 "DOCKERFILE"，必须切换**
   - 点击下拉菜单
   - **选择 "NIXPACKS"**（不是 Docker，不是 DOCKERFILE）

5. **保存设置**
   - 点击 "Save" 或 "Update"
   - 等待保存完成

6. **触发新部署**
   - 点击 "Deploy" 或 "Redeploy"
   - 或者推送新的空提交到 GitHub

### 方案 2：临时重命名 Dockerfile

如果 Dashboard 设置后仍然使用 Docker，临时重命名 Dockerfile：

```bash
# 重命名 backend/Dockerfile（不要删除，以防需要）
mv backend/Dockerfile backend/Dockerfile.backup
git add backend/Dockerfile.backup
git commit -m "temp: Rename Dockerfile to force NIXPACKS"
git push origin main
```

### 方案 3：删除并重新创建服务

如果以上方法都不行：

1. **删除当前后端服务**
   - Railway Dashboard → 后端服务 → Settings → Delete Service

2. **重新创建服务**
   - 点击 "+ New" → "GitHub Repo"
   - 选择你的仓库
   - **在创建时，明确选择 "NIXPACKS" 构建器**
   - 不要选择 Docker 或 DOCKERFILE

3. **配置环境变量**
   - 重新添加所有环境变量

## 🔍 验证 NIXPACKS 是否生效

### 检查构建日志

在 Railway Dashboard → Deployments → 最新部署 → Logs：

**应该看到（NIXPACKS）：**
- ✅ "Detected Python project"
- ✅ "Using NIXPACKS builder"
- ✅ "Installing Python dependencies..."
- ✅ "Downloading spaCy model..."

**不应该看到（Docker）：**
- ❌ "Docker build"
- ❌ "Dockerfile:20"
- ❌ "FROM python:3.9-slim"
- ❌ "/bin/bash: line 1: pip: command not found"

## 📋 检查清单

在 Railway Dashboard 中确认：

- [ ] Settings → Build & Deploy → Builder = **"NIXPACKS"**（不是 Docker）
- [ ] 根目录没有 Dockerfile（已确认）
- [ ] `railway.json` 存在且 `"builder": "NIXPACKS"`
- [ ] `nixpacks.toml` 存在且配置正确
- [ ] `.railwayignore` 存在且包含 Dockerfile
- [ ] 已保存设置并触发新部署

## 🚨 如果仍然失败

### 使用 Railway CLI 强制设置

```bash
# 安装 Railway CLI
npm i -g @railway/cli

# 登录
railway login

# 链接项目
railway link

# 查看当前服务
railway service

# 设置构建器为 NIXPACKS
railway variables set RAILWAY_BUILDER=NIXPACKS

# 或者直接部署
railway up
```

### 联系 Railway 支持

如果所有方法都失败，可能是 Railway 平台的 bug。可以：
1. 在 Railway Dashboard 中提交支持工单
2. 或在 Railway Discord 社区寻求帮助

---

**最后更新**: 2026-01-16  
**优先级**: 🔴 紧急
