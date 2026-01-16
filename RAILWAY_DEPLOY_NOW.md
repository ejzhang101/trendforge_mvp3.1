# 🚀 Railway 立即部署指南

## ✅ 当前配置状态

根据你的 Dashboard 截图，配置已经正确：
- ✅ Builder: Nixpacks
- ✅ Custom Build Command: 已设置
- ✅ Custom Start Command: 已设置

## 🚀 立即部署步骤

### 步骤 1: 触发新部署

1. **在 Railway Dashboard 中**：
   - 点击 "Deployments" 标签页
   - 点击 "Deploy" 或 "Redeploy" 按钮
   - 或者等待 GitHub 推送自动触发

### 步骤 2: 查看构建日志

1. **在 Deployments 页面**：
   - 点击最新的部署
   - 查看构建日志

2. **验证使用 NIXPACKS**：
   - 应该看到 "Using NIXPACKS builder"
   - 应该看到 "Detected Python project"
   - 应该看到执行 Build Command
   - 应该看到安装依赖的过程

3. **不应该看到**：
   - ❌ "Docker build"
   - ❌ "Dockerfile:20"
   - ❌ "pip: command not found"

### 步骤 3: 验证部署成功

部署完成后，测试健康检查：

```bash
curl https://your-app.railway.app/health
```

应该返回：
```json
{
  "status": "healthy",
  "version": "3.1.0",
  "services": {
    "cache": true,
    "prophet": true,
    "script_generator": true
  }
}
```

---

## 🐛 如果仍然使用 Docker

如果触发新部署后，构建日志仍然显示 Docker 构建：

### 方案 1: 清除并重新部署

1. **删除当前部署**：
   - Deployments → 选择失败的部署 → Delete

2. **触发全新部署**：
   - 点击 "Deploy" 创建新部署

### 方案 2: 删除并重新创建服务（推荐）

如果方案 1 不起作用：

1. **删除当前后端服务**：
   - Settings → 滚动到底部 → "Danger" 部分
   - 点击 "Delete Service"
   - 确认删除

2. **重新创建服务**：
   - 在项目中点击 "+ New"
   - 选择 "GitHub Repo"
   - 选择 `ejzhang101/trendforge_mvp3.1`
   - **在创建时，明确选择 "Nixpacks" 作为 Builder**
   - 不要选择 Docker

3. **配置环境变量**：
   - 重新添加所有环境变量：
     - `DATABASE_URL`
     - `REDIS_URL`
     - `TWITTER_BEARER_TOKEN`
     - `SERPAPI_KEY`
     - `YOUTUBE_API_KEY`
     - `OPENAI_API_KEY`
     - 等等

4. **设置 Build 和 Start Commands**：
   - Build Command: `cd backend && pip install -r requirements_v2.txt && python -m spacy download en_core_web_sm`
   - Start Command: `cd backend && python -m uvicorn app_v2:app --host 0.0.0.0 --port $PORT`

5. **触发部署**：
   - 保存设置后，触发新部署

---

## 📋 部署检查清单

部署前确认：
- [ ] Builder 设置为 Nixpacks
- [ ] Build Command 完整且正确
- [ ] Start Command 完整且正确
- [ ] Root Directory 留空
- [ ] 所有环境变量已配置
- [ ] 已触发新部署

部署后验证：
- [ ] 构建日志显示 NIXPACKS（不是 Docker）
- [ ] 构建成功完成
- [ ] 应用启动成功
- [ ] 健康检查返回正常

---

## 🎯 预期结果

成功部署后，你应该看到：

1. **构建日志**：
   ```
   Using NIXPACKS builder
   Detected Python project
   Installing dependencies...
   Downloading spaCy model...
   Starting application...
   ```

2. **健康检查**：
   ```json
   {
     "status": "healthy",
     "version": "3.1.0"
   }
   ```

3. **服务状态**：
   - 所有服务正常运行
   - 可以访问 API 端点

---

**最后更新**: 2026-01-16  
**状态**: 配置已就绪，等待部署
