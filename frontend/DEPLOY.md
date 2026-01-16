# Vercel CLI 快速部署指南

## 🚀 快速开始

### 方法 1: 使用部署脚本（推荐）

```bash
cd frontend
./deploy-vercel.sh
```

### 方法 2: 手动部署

```bash
# 1. 进入 frontend 目录
cd frontend

# 2. 安装 Vercel CLI（如果还没有）
npm i -g vercel
# 或
pnpm add -g vercel

# 3. 登录 Vercel（首次使用）
vercel login

# 4. 部署到生产环境
vercel --prod
```

## 📋 首次部署配置

当 Vercel CLI 询问配置时：

```
? Set up and deploy "~/TrendForge/frontend"? [Y/n] y
? Which scope do you want to deploy to? [选择你的账户]
? Link to existing project? [Y/n] n
? What's your project's name? trendforge-frontend
? In which directory is your code located? ./
```

**重要配置：**
- **Root Directory**: `./`（因为已经在 frontend 目录中）
- **Build Command**: 留空（Vercel 会自动检测 Next.js）
- **Output Directory**: `.next`（自动检测）
- **Install Command**: 留空（自动检测）

## 🔧 环境变量设置

部署后，在 Vercel Dashboard 中设置环境变量：

1. **进入项目** → Settings → Environment Variables
2. **添加以下变量：**

```env
BACKEND_SERVICE_URL=https://[your-railway-backend-url]
NEXT_PUBLIC_BACKEND_SERVICE_URL=https://[your-railway-backend-url]
DATABASE_URL=postgresql://...
YOUTUBE_API_KEY=...
```

3. **重新部署**以应用环境变量

## ✅ 验证部署

部署成功后，Vercel CLI 会显示：
```
✅ Production: https://your-project.vercel.app
```

访问该 URL 验证前端是否正常工作。

## 🔄 后续部署

之后只需要：
```bash
cd frontend
vercel --prod
```

## 🐛 故障排查

### 问题 1: "command not found: vercel"

**解决方案：**
```bash
# 重新安装
npm i -g vercel

# 或使用 npx（无需全局安装）
npx vercel --prod
```

### 问题 2: "command not found: npm"

**解决方案：**
```bash
# 加载 shell 配置
source ~/.zshrc  # macOS zsh
# 或
source ~/.bashrc  # bash

# 如果使用 nvm
source ~/.nvm/nvm.sh
nvm use node
```

### 问题 3: 环境变量未生效

**解决方案：**
1. 在 Vercel Dashboard → Settings → Environment Variables 中确认已设置
2. 重新部署：`vercel --prod`
3. 或在 Dashboard 中手动触发 "Redeploy"

### 问题 4: 构建失败

**检查：**
1. 查看构建日志：`vercel logs`
2. 确认 `package.json` 中的脚本正确
3. 确认所有依赖已安装

## 📚 相关文档

- `../VERCEL_CLI_DEPLOY.md` - 详细 CLI 部署指南
- `../VERCEL_DEPLOY_FIX.md` - Dashboard 配置修复
- `../VERCEL_URGENT_FIX.md` - 紧急修复指南

---

**最后更新**: 2026-01-16  
**版本**: MVP 3.1.0
