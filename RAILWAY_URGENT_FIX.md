# 🚨 Railway Docker 构建问题 - 紧急修复方案

## ❌ 当前问题

即使重命名了 Dockerfile，Railway **仍然使用 Docker 构建器**。

错误信息：
```
Dockerfile:20
RUN  pip install -r requirements_v2.txt
/bin/bash: line 1: pip: command not found
```

## 🔍 根本原因

Railway 可能：
1. **缓存了旧的构建配置**
2. **Dashboard 中的 Builder 设置仍然是 Docker**
3. **服务需要完全重新创建**

## ✅ 立即解决方案（按优先级）

### 方案 1：在 Railway Dashboard 中强制切换 Builder（最重要！）

**这是最关键的步骤，必须在 Dashboard 中手动操作：**

1. **访问 Railway Dashboard**
   - https://railway.app/dashboard
   - 选择项目 `trendforge_mvp3.1`

2. **选择后端服务**
   - 点击后端服务（不是 PostgreSQL 或 Redis）

3. **进入 Settings → Build**
   - 点击 "Settings" 标签页
   - 在右侧导航栏点击 "Build"

4. **检查 Builder 下拉菜单**
   - 找到 "Builder" 选项
   - **当前可能显示 "Docker" 或 "DOCKERFILE"**
   - **必须点击下拉菜单，选择 "Nixpacks"**
   - 不要选择 "Docker" 或 "DOCKERFILE"

5. **保存设置**
   - 点击页面上的 "Save" 按钮
   - 等待保存完成

6. **触发新部署**
   - 点击 "Deployments" 标签页
   - 点击 "Deploy" 或 "Redeploy"
   - 或者推送一个空提交到 GitHub

### 方案 2：删除并重新创建服务

如果方案 1 不起作用：

1. **删除当前后端服务**
   - Railway Dashboard → 后端服务 → Settings
   - 滚动到底部，找到 "Danger" 部分
   - 点击 "Delete Service"
   - 确认删除

2. **重新创建服务**
   - 在项目中点击 "+ New"
   - 选择 "GitHub Repo"
   - 选择 `ejzhang101/trendforge_mvp3.1`
   - **在创建过程中，明确选择 "Nixpacks" 作为 Builder**
   - 不要选择 Docker

3. **配置环境变量**
   - 重新添加所有环境变量（从之前的配置中复制）

4. **设置 Build 和 Start Commands**
   - Build Command: `cd backend && pip install -r requirements_v2.txt && python -m spacy download en_core_web_sm`
   - Start Command: `cd backend && python -m uvicorn app_v2:app --host 0.0.0.0 --port $PORT`

### 方案 3：使用 Railway CLI 强制设置

```bash
# 安装 Railway CLI
npm i -g @railway/cli

# 登录
railway login

# 链接项目
railway link

# 查看当前服务
railway service

# 设置构建器（如果 CLI 支持）
railway variables set RAILWAY_BUILDER=NIXPACKS

# 或者直接部署
railway up
```

## 🔍 验证 Builder 设置

### 在 Railway Dashboard 中检查

1. **Settings → Build**
   - Builder 下拉菜单应该显示 **"Nixpacks"**
   - 不应该显示 "Docker" 或 "DOCKERFILE"

2. **查看构建日志**
   - Deployments → 最新部署 → Logs
   - 应该看到 "Using NIXPACKS builder"
   - 不应该看到 "Docker build" 或 "Dockerfile:20"

## 📋 检查清单

在尝试新部署前，确认：

- [ ] Railway Dashboard → Settings → Build → Builder = **"Nixpacks"**（不是 Docker）
- [ ] 已保存 Builder 设置
- [ ] `backend/Dockerfile` 已重命名为 `Dockerfile.backup`
- [ ] `.railwayignore` 已更新
- [ ] `railway.json` 存在且 `"builder": "NIXPACKS"`
- [ ] `nixpacks.toml` 存在且配置正确

## 🚨 如果所有方法都失败

如果以上所有方法都不起作用，可能是 Railway 平台的 bug 或配置问题。可以：

1. **联系 Railway 支持**
   - 在 Railway Dashboard 中提交支持工单
   - 说明 Builder 设置无法切换的问题

2. **在 Railway Discord 社区寻求帮助**
   - 描述问题和已尝试的解决方案

3. **考虑使用 Render 作为替代**
   - Render 对 Nixpacks 的支持更稳定
   - 参考 `DEPLOY_RENDER_MVP3.1.0.md`

---

**最后更新**: 2026-01-16  
**优先级**: 🔴🔴🔴 紧急  
**状态**: 等待用户在 Dashboard 中手动切换 Builder
