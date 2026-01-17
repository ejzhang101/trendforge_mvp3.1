# Vercel 环境变量配置修复指南

## 问题

前端连接后端失败，错误信息：
```
Failed to parse URL from tf-mvp31.up.railway.app/api/v2/full-analysis
```

## 原因

后端服务 URL 环境变量缺少协议（`https://`）。

## 解决方案

### 方法 1: 在 Vercel Dashboard 中设置正确的 URL（推荐）

1. **进入 Vercel Dashboard**
   - 访问 https://vercel.com/dashboard
   - 选择你的项目

2. **设置环境变量**
   - Settings → Environment Variables
   - 找到或添加 `BACKEND_SERVICE_URL`
   - **确保值包含 `https://`**：
     ```
     https://tf-mvp31.up.railway.app
     ```
   - 不是：
     ```
     tf-mvp31.up.railway.app  ❌
     ```

3. **同样设置 `NEXT_PUBLIC_BACKEND_SERVICE_URL`**
   ```
   https://tf-mvp31.up.railway.app
   ```

4. **重新部署**
   - Deployments → 最新部署 → "..." → "Redeploy"
   - 或等待自动重新部署

### 方法 2: 代码已自动修复（备用方案）

代码已经更新，会自动检测并添加 `https://` 协议（如果缺失）。

但是，**最佳实践是在环境变量中直接设置完整的 URL**。

## 环境变量检查清单

在 Vercel Dashboard → Settings → Environment Variables 中确认：

- [ ] `BACKEND_SERVICE_URL` = `https://tf-mvp31.up.railway.app`（包含 https://）
- [ ] `NEXT_PUBLIC_BACKEND_SERVICE_URL` = `https://tf-mvp31.up.railway.app`（包含 https://）
- [ ] `DATABASE_URL` = `postgresql://...`
- [ ] `YOUTUBE_API_KEY` = `...`

## 验证

部署后，检查浏览器控制台：
- 应该不再有 "Failed to parse URL" 错误
- 后端 API 调用应该成功

## 代码修复详情

已更新以下文件，自动添加协议（如果缺失）：
- `frontend/app/api/analyze/route.ts`
- `frontend/app/api/analysis/[channelId]/route.ts`
- `frontend/components/ScriptGenerator.tsx`

---

**最后更新**: 2026-01-16  
**版本**: MVP 3.1.0
