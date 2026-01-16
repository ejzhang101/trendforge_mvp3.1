# Vercel 部署修复指南

## 问题

Vercel 构建时出现错误：
```
sh: line 1: cd: frontend: No such file or directory
Error: Command "cd frontend && pnpm install" exited with 1
```

## 原因

Vercel Dashboard 中的手动设置可能覆盖了 `vercel.json` 配置。

## 解决方案

### 方法 1: 在 Vercel Dashboard 中手动设置（推荐）

1. **进入 Vercel Dashboard**
   - 访问 https://vercel.com/dashboard
   - 选择你的项目

2. **设置 Root Directory**
   - Settings → General
   - 找到 "Root Directory"
   - 点击 "Edit"
   - 输入: `frontend`
   - 点击 "Save"

3. **检查 Build & Development Settings**
   - Settings → Build & Development Settings
   - **Build Command**: 留空（或设置为 `pnpm build`）
   - **Install Command**: 留空（或设置为 `pnpm install`）
   - **Output Directory**: 留空（或设置为 `.next`）
   - **Framework Preset**: Next.js

4. **重新部署**
   - Deployments → 点击最新部署的 "..." → "Redeploy"
   - 或等待自动重新部署

### 方法 2: 使用 vercel.json（如果 Dashboard 设置正确）

确保 `vercel.json` 在根目录，内容如下：

```json
{
  "buildCommand": "pnpm install && pnpm build",
  "outputDirectory": ".next",
  "framework": "nextjs",
  "installCommand": "pnpm install",
  "devCommand": "pnpm dev",
  "rootDirectory": "frontend",
  "rewrites": [
    {
      "source": "/api/:path*",
      "destination": "/api/:path*"
    }
  ]
}
```

### 方法 3: 强制使用 vercel.json

如果 Dashboard 设置覆盖了 `vercel.json`，可以：

1. **删除 Dashboard 中的手动设置**
   - Settings → Build & Development Settings
   - 将所有自定义命令留空
   - 只设置 Root Directory = `frontend`

2. **或者使用 Vercel CLI**
   ```bash
   cd frontend
   vercel --prod
   ```

## 验证步骤

1. **检查 Root Directory**
   - Settings → General → Root Directory = `frontend` ✓

2. **检查构建命令**
   - 构建日志中应该显示：
     ```
     Running "install" command: `pnpm install`...
     ```
   - 而不是：
     ```
     Running "install" command: `cd frontend && pnpm install`...
     ```

3. **检查构建成功**
   - 构建日志应该显示：
     ```
     ✓ Built in X seconds
     ```

## 常见问题

### Q: 为什么 Vercel 还在使用旧的构建命令？

A: Vercel Dashboard 中的手动设置优先级高于 `vercel.json`。需要：
1. 在 Dashboard 中设置 Root Directory = `frontend`
2. 或者删除 Dashboard 中的自定义构建命令

### Q: 如何确认 Vercel 使用了正确的配置？

A: 查看构建日志：
- 如果显示 `cd frontend && ...` → Dashboard 设置覆盖了 vercel.json
- 如果显示 `pnpm install`（没有 cd frontend）→ 配置正确

### Q: 提交了新的 vercel.json 但 Vercel 没有更新？

A: 
1. 确认代码已推送到 GitHub
2. 在 Vercel Dashboard 中手动触发 "Redeploy"
3. 或等待 Vercel 自动检测（可能需要几分钟）

---

**最后更新**: 2026-01-16  
**版本**: MVP 3.1.0
