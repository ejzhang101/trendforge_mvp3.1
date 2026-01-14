# API Keys 配置说明

## 社交媒体趋势收集器需要以下 API Keys

### 1. Twitter API (X API) - 可选
如果你有 Twitter Bearer Token，请按以下步骤配置：

1. 访问 https://developer.twitter.com/en/portal/dashboard
2. 创建应用并获取 Bearer Token
3. 在 `backend/.env` 文件中添加：
   ```
   TWITTER_BEARER_TOKEN=your_bearer_token_here
   ```

**注意**: 如果没有配置，系统会使用模拟数据

### 2. Reddit API - 可选
如果你有 Reddit API credentials，请按以下步骤配置：

1. 访问 https://www.reddit.com/prefs/apps
2. 点击 "create another app..." 或 "create app"
3. 选择 "script" 类型
4. 获取 Client ID 和 Client Secret
5. 在 `backend/.env` 文件中添加：
   ```
   REDDIT_CLIENT_ID=your_client_id_here
   REDDIT_CLIENT_SECRET=your_client_secret_here
   ```

**注意**: 如果没有配置，系统会使用模拟数据

### 3. Google Trends - 无需配置
Google Trends 不需要 API keys，可以直接使用。

### 4. OpenAI API - 可选（用于智能脚本生成）
如果你想要使用 AI 语义分析和智能脚本生成功能，请配置 OpenAI API：

1. 访问 https://platform.openai.com/api-keys
2. 创建新的 API Key
3. 在 `backend/.env` 文件中添加：
   ```
   OPENAI_API_KEY=your_openai_api_key_here
   ```

**注意**: 如果没有配置，系统会使用模板方式生成脚本（功能仍然可用，但不够智能）

## 配置步骤

1. 在 `backend` 目录下创建 `.env` 文件（如果还没有）：
   ```bash
   cd backend
   touch .env
   ```

2. 添加你的 API keys 到 `.env` 文件：
   ```
   TWITTER_BEARER_TOKEN=your_twitter_bearer_token_here
   REDDIT_CLIENT_ID=your_reddit_client_id_here
   REDDIT_CLIENT_SECRET=your_reddit_client_secret_here
   ```

3. 重启后端服务器以加载新的环境变量

## 测试

即使没有配置 API keys，系统也会使用模拟数据，所以你可以先测试功能。配置 API keys 后，将获得真实的社交媒体数据。
