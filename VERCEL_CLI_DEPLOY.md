# Vercel CLI 部署指南

## 前提条件

确保已安装 Node.js 和 npm/pnpm。

## 安装 Vercel CLI

### 方法 1: 使用 npm
```bash
npm i -g vercel
```

### 方法 2: 使用 pnpm
```bash
pnpm add -g vercel
```

### 方法 3: 使用 npx（无需全局安装）
```bash
npx vercel --prod
```

## 部署步骤

### 1. 打开终端并进入 frontend 目录

```bash
cd /Users/ejzhang/Documents/TrendForge/frontend
```

### 2. 登录 Vercel（首次使用）

```bash
vercel login
```

这会打开浏览器，让你登录 Vercel 账户。

### 3. 部署到生产环境

```bash
vercel --prod
```

### 4. 首次部署配置

如果是首次部署，Vercel CLI 会询问：

```
? Set up and deploy "~/TrendForge/frontend"? [Y/n] y
? Which scope do you want to deploy to? [选择你的账户]
? Link to existing project? [Y/n] n
? What's your project's name? trendforge-frontend
? In which directory is your code located? ./
```

**重要配置：**
- **Root Directory**: 输入 `./`（因为已经在 frontend 目录中）
- **Build Command**: 留空或输入 `pnpm build`
- **Output Directory**: `.next`
- **Install Command**: 留空或输入 `pnpm install`

### 5. 后续部署

之后只需要：
```bash
cd frontend
vercel --prod
```

## 环境变量设置

如果需要在部署时设置环境变量：

```bash
# 方法 1: 在 Vercel Dashboard 中设置
# Settings → Environment Variables

# 方法 2: 使用 CLI
vercel env add BACKEND_SERVICE_URL production
# 然后输入值

# 方法 3: 使用 .env.local（本地开发）
# 在 frontend/.env.local 中添加
```

## 验证部署

部署成功后，Vercel CLI 会显示：
```
✅ Production: https://your-project.vercel.app
```

## 常见问题

### Q: 找不到 npm/vercel 命令？

A: 可能需要：
1. 加载 shell 配置：
   ```bash
   source ~/.zshrc  # 或 ~/.bashrc
   ```

2. 如果使用 nvm：
   ```bash
   source ~/.nvm/nvm.sh
   nvm use node
   ```

3. 如果使用 Homebrew：
   ```bash
   eval "$(/opt/homebrew/bin/brew shellenv)"
   ```

### Q: 如何链接到现有项目？

A: 
```bash
vercel link
# 选择现有项目
```

### Q: 如何查看部署日志？

A:
```bash
vercel logs
```

### Q: 如何回滚到之前的部署？

A: 在 Vercel Dashboard → Deployments → 选择之前的部署 → "Promote to Production"

---

**最后更新**: 2026-01-16  
**版本**: MVP 3.1.0
