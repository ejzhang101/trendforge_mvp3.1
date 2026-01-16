# 🚨 Vercel 部署紧急修复

## 问题

即使更新了 `vercel.json`，Vercel 仍然执行：
```
cd frontend && pnpm install
```

## 根本原因

**Vercel Dashboard 中的手动设置优先级最高**，会完全覆盖 `vercel.json`。

## ✅ 立即解决方案（必须在 Dashboard 中操作）

### 步骤 1: 删除所有自定义构建命令

1. **进入 Vercel Dashboard**
   - https://vercel.com/dashboard
   - 选择你的项目

2. **Settings → Build & Development Settings**
   - 找到 "Build Command"
   - **完全删除** 或设置为空（留空）
   - 找到 "Install Command"  
   - **完全删除** 或设置为空（留空）
   - 找到 "Output Directory"
   - 设置为 `.next` 或留空
   - **保存**

### 步骤 2: 设置 Root Directory（关键！）

1. **Settings → General**
   - 滚动到 "Root Directory"
   - 点击 "Edit" 或 "Override"
   - **输入**: `frontend`（不要有斜杠）
   - 点击 "Save"

2. **验证设置**
   - 确认显示: `Root Directory: frontend`

### 步骤 3: 清除缓存并重新部署

1. **Deployments → 最新部署**
   - 点击 "..." 菜单
   - 选择 "Redeploy"
   - **勾选**: "Use existing Build Cache" = **取消勾选**（清除缓存）
   - 点击 "Redeploy"

## 🔍 验证配置

部署后，检查构建日志：

**✅ 正确的日志应该显示：**
```
Running "install" command: `pnpm install`...
Running "build" command: `pnpm build`...
```

**❌ 错误的日志（如果仍然看到）：**
```
Running "install" command: `cd frontend && pnpm install`...
```

## 🎯 如果仍然失败

### 方法 A: 使用 Vercel CLI（推荐）

```bash
# 在项目根目录
cd frontend
vercel --prod

# 或者指定根目录
vercel --prod --cwd frontend
```

### 方法 B: 创建新项目

1. 在 Vercel Dashboard 中删除当前项目
2. 重新连接 GitHub 仓库
3. **在首次部署时**：
   - Root Directory: `frontend`
   - 不要设置任何自定义构建命令
   - 让 Vercel 自动检测 Next.js

### 方法 C: 移动 frontend 到根目录（不推荐）

如果以上方法都不行，可以考虑：
1. 将 `frontend/` 下的所有文件移动到根目录
2. 更新 `.gitignore` 和路径引用
3. 重新部署

## 📋 检查清单

在 Vercel Dashboard 中确认：

- [ ] Settings → General → Root Directory = `frontend`
- [ ] Settings → Build & Development Settings → Build Command = **空**（或删除）
- [ ] Settings → Build & Development Settings → Install Command = **空**（或删除）
- [ ] Settings → Build & Development Settings → Output Directory = `.next` 或 **空**
- [ ] 已清除构建缓存并重新部署

## 💡 为什么会出现这个问题？

1. **首次部署时**可能手动设置了构建命令
2. Vercel Dashboard 设置优先级：**Dashboard > vercel.json > 自动检测**
3. 即使更新了 `vercel.json`，Dashboard 中的设置仍然生效

## 🚀 快速修复命令（如果使用 CLI）

```bash
# 安装 Vercel CLI（如果还没有）
npm i -g vercel

# 在 frontend 目录部署
cd frontend
vercel --prod
```

---

**最后更新**: 2026-01-16  
**优先级**: 🔴 紧急
