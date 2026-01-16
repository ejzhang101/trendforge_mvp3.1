# 手动部署到 Vercel - 完整指南

## 问题

如果自动化脚本无法运行（Node.js 不在 PATH 中），请按照以下步骤手动部署。

## 前置条件

### 1. 确保 Node.js 已安装

检查 Node.js 是否已安装：
```bash
node --version
npm --version
npx --version
```

如果命令不存在，安装 Node.js：

**使用 Homebrew (推荐):**
```bash
# Apple Silicon Mac (M1/M2/M3)
eval "$(/opt/homebrew/bin/brew shellenv)"
brew install node

# Intel Mac
eval "$(/usr/local/bin/brew shellenv)"
brew install node
```

**或从官网下载:**
- 访问 https://nodejs.org/
- 下载并安装 LTS 版本

### 2. 加载 Node.js 环境

在终端中执行（根据您的系统选择）：

```bash
# Apple Silicon Mac
eval "$(/opt/homebrew/bin/brew shellenv)"

# Intel Mac
eval "$(/usr/local/bin/brew shellenv)"

# 或加载 shell 配置
source ~/.zshrc  # macOS zsh
# 或
source ~/.bashrc  # bash

# 如果使用 nvm
source ~/.nvm/nvm.sh
nvm use node
```

## 部署步骤

### 步骤 1: 进入 frontend 目录

```bash
cd /Users/ejzhang/Documents/TrendForge/frontend
```

### 步骤 2: 使用 npx 部署（推荐，无需全局安装）

```bash
npx vercel --prod
```

### 步骤 3: 首次部署配置

如果是首次部署，Vercel CLI 会询问：

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

### 步骤 4: 登录 Vercel（如果需要）

如果提示需要登录：
```bash
npx vercel login
```

这会打开浏览器，让你登录 Vercel 账户。

## 环境变量设置

部署后，在 Vercel Dashboard 中设置环境变量：

1. **进入项目** → Settings → Environment Variables
2. **添加以下变量：**

```env
BACKEND_SERVICE_URL=https://[your-railway-backend-url]
NEXT_PUBLIC_BACKEND_SERVICE_URL=https://[your-railway-backend-url]
DATABASE_URL=postgresql://postgres:password@host:port/database
YOUTUBE_API_KEY=your_youtube_api_key
```

3. **重新部署**以应用环境变量：
   ```bash
   npx vercel --prod
   ```

## 验证部署

部署成功后，Vercel CLI 会显示：
```
✅ Production: https://your-project.vercel.app
```

访问该 URL 验证前端是否正常工作。

## 后续部署

之后只需要：
```bash
cd /Users/ejzhang/Documents/TrendForge/frontend
npx vercel --prod
```

## 故障排查

### 问题 1: "command not found: npx"

**解决方案：**
1. 确保 Node.js 已安装：`node --version`
2. 加载环境变量（见上面的"加载 Node.js 环境"部分）
3. 如果使用 nvm，确保已激活：`nvm use node`

### 问题 2: "Vercel CLI not found"

**解决方案：**
使用 `npx` 不需要全局安装，它会自动下载并使用 Vercel CLI。

### 问题 3: 环境变量未生效

**解决方案：**
1. 在 Vercel Dashboard → Settings → Environment Variables 中确认已设置
2. 重新部署：`npx vercel --prod`
3. 或在 Dashboard 中手动触发 "Redeploy"

### 问题 4: 构建失败

**检查：**
1. 查看构建日志：`npx vercel logs`
2. 确认 `package.json` 中的脚本正确
3. 确认所有依赖已安装：`npm install` 或 `pnpm install`

## 替代方案：使用 Vercel Dashboard

如果 CLI 部署遇到问题，可以使用 Vercel Dashboard：

1. **访问** https://vercel.com/dashboard
2. **导入项目** → 选择 GitHub 仓库
3. **配置设置**：
   - Root Directory: `frontend`
   - Build Command: 留空
   - Install Command: 留空
   - Output Directory: `.next`
4. **部署**

---

**最后更新**: 2026-01-16  
**版本**: MVP 3.1.0
