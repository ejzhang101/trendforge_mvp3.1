# 🐳 Dockerfile 配置指南

## 📋 概述

本项目包含两个 Dockerfile：
- `backend/Dockerfile` - 后端服务容器配置
- `frontend/Dockerfile` - 前端应用容器配置

## ⚠️ 重要说明

### Render 部署（推荐）
- ✅ **不需要 Dockerfile**
- ✅ Render 使用 **Nixpacks** 自动构建 Python 项目
- ✅ 只需配置 Build Command 和 Start Command
- ✅ 参考 `DEPLOY_RENDER_MVP3.1.0.md` 获取详细说明

### Docker 部署（其他平台）
- ✅ 需要 Dockerfile
- ✅ 适用于 Docker、Kubernetes、AWS ECS、Google Cloud Run 等
- ✅ 本文档说明如何配置和使用

---

## 🔧 后端 Dockerfile 配置

### 文件位置
`backend/Dockerfile`

### 完整内容
```dockerfile
FROM python:3.9-slim

WORKDIR /app

# 安装系统依赖
RUN apt-get update && apt-get install -y \
    build-essential \
    curl \
    && rm -rf /var/lib/apt/lists/*

# 复制依赖文件（先复制依赖文件以利用 Docker 缓存）
COPY requirements_v2.txt .

# 安装 Python 依赖
RUN pip install --no-cache-dir -r requirements_v2.txt

# 下载 spaCy 模型
RUN python -m spacy download en_core_web_sm

# 复制应用代码
COPY . .

# 暴露端口（使用环境变量，支持动态端口）
EXPOSE 8000

# 设置环境变量
ENV PYTHONUNBUFFERED=1
ENV PORT=8000

# 启动命令（使用环境变量 PORT，兼容 Render/Railway）
CMD python -m uvicorn app_v2:app --host 0.0.0.0 --port ${PORT:-8000}
```

### 配置说明

#### 1. 基础镜像
```dockerfile
FROM python:3.9-slim
```
- 使用 Python 3.9 官方精简镜像
- `slim` 版本减少镜像大小

#### 2. 工作目录
```dockerfile
WORKDIR /app
```
- 设置容器内工作目录为 `/app`

#### 3. 系统依赖
```dockerfile
RUN apt-get update && apt-get install -y \
    build-essential \
    curl \
    && rm -rf /var/lib/apt/lists/*
```
- `build-essential`: 编译 C 扩展所需（Prophet、NumPy 等）
- `curl`: 下载工具
- 清理 apt 缓存以减小镜像大小

#### 4. Python 依赖安装
```dockerfile
COPY requirements_v2.txt .
RUN pip install --no-cache-dir -r requirements_v2.txt
```
- 先复制依赖文件（利用 Docker 层缓存）
- 使用 `--no-cache-dir` 减小镜像大小

#### 5. spaCy 模型
```dockerfile
RUN python -m spacy download en_core_web_sm
```
- 下载 spaCy 英文模型（NLP 分析必需）
- 约 12.8 MB，构建时下载

#### 6. 应用代码
```dockerfile
COPY . .
```
- 复制所有应用代码到容器

#### 7. 端口配置
```dockerfile
EXPOSE 8000
ENV PORT=8000
```
- 暴露端口 8000
- 设置默认端口环境变量
- 支持通过 `-e PORT=8080` 动态修改

#### 8. 启动命令
```dockerfile
CMD python -m uvicorn app_v2:app --host 0.0.0.0 --port ${PORT:-8000}
```
- 使用 uvicorn 启动 FastAPI 应用
- `${PORT:-8000}` 支持环境变量，默认 8000
- 兼容 Render、Railway 等平台的动态端口

---

## 🚀 使用 Dockerfile

### 1. 构建镜像

```bash
cd backend
docker build -t trendforge-backend:latest .
```

### 2. 运行容器

```bash
# 基本运行
docker run -p 8000:8000 trendforge-backend:latest

# 带环境变量
docker run -p 8000:8000 \
  -e DATABASE_URL=postgresql://... \
  -e REDIS_URL=redis://... \
  -e TWITTER_BEARER_TOKEN=... \
  -e OPENAI_API_KEY=... \
  trendforge-backend:latest

# 使用自定义端口
docker run -p 8080:8080 \
  -e PORT=8080 \
  trendforge-backend:latest
```

### 3. 使用 docker-compose

项目根目录的 `docker-compose.yml`：

```yaml
version: '3.8'

services:
  backend:
    build:
      context: ./backend
      dockerfile: Dockerfile
    ports:
      - "8000:8000"
    environment:
      - TWITTER_BEARER_TOKEN=${TWITTER_BEARER_TOKEN}
      - REDDIT_CLIENT_ID=${REDDIT_CLIENT_ID}
      - REDDIT_CLIENT_SECRET=${REDDIT_CLIENT_SECRET}
      - DATABASE_URL=${DATABASE_URL}
      - REDIS_URL=${REDIS_URL}
      - OPENAI_API_KEY=${OPENAI_API_KEY}
      - SERPAPI_KEY=${SERPAPI_KEY}
    volumes:
      - ./backend:/app
    restart: unless-stopped
```

启动：
```bash
docker-compose up -d
```

---

## 📦 前端 Dockerfile 配置

### 文件位置
`frontend/Dockerfile`

### 多阶段构建说明

前端 Dockerfile 使用多阶段构建优化镜像大小：

1. **deps 阶段**: 安装依赖
2. **builder 阶段**: 构建 Next.js 应用
3. **runner 阶段**: 运行生产服务器

### 使用说明

```bash
cd frontend
docker build -t trendforge-frontend:latest .
docker run -p 3000:3000 trendforge-frontend:latest
```

---

## 🔍 Dockerfile 优化建议

### 1. 利用层缓存
- ✅ 先复制 `requirements_v2.txt`，再安装依赖
- ✅ 最后复制应用代码
- ✅ 代码变更时只需重建最后一层

### 2. 减小镜像大小
- ✅ 使用 `--no-cache-dir` 安装 pip 包
- ✅ 清理 apt 缓存
- ✅ 使用 `slim` 基础镜像

### 3. 安全性
- ✅ 使用非 root 用户运行（可选）
- ✅ 定期更新基础镜像
- ✅ 不在 Dockerfile 中硬编码密钥

### 4. 生产环境优化
- ✅ 使用多阶段构建（前端已实现）
- ✅ 设置 `PYTHONUNBUFFERED=1` 确保日志实时输出
- ✅ 使用环境变量配置端口

---

## 🐛 常见问题

### 1. 构建失败：找不到 requirements_v2.txt
**原因**: 构建上下文不正确

**解决**:
```bash
# 确保在 backend 目录下构建
cd backend
docker build -t trendforge-backend:latest .

# 或指定上下文
docker build -f backend/Dockerfile -t trendforge-backend:latest backend/
```

### 2. spaCy 模型下载失败
**原因**: 网络问题或构建时未安装 spaCy

**解决**:
- 确保 `requirements_v2.txt` 包含 `spacy>=3.7.0`
- 检查网络连接
- 可以预先下载模型并复制到镜像

### 3. 端口冲突
**原因**: 主机端口已被占用

**解决**:
```bash
# 使用其他端口
docker run -p 8080:8000 trendforge-backend:latest
```

### 4. 环境变量未生效
**原因**: 环境变量未正确传递

**解决**:
```bash
# 使用 -e 传递环境变量
docker run -p 8000:8000 \
  -e DATABASE_URL=postgresql://... \
  trendforge-backend:latest

# 或使用 .env 文件
docker run -p 8000:8000 --env-file .env trendforge-backend:latest
```

---

## 📚 相关文档

- `DEPLOY_RENDER_MVP3.1.0.md` - Render 部署指南（不需要 Dockerfile）
- `DEPLOYMENT.md` - 完整部署指南
- `docker-compose.yml` - Docker Compose 配置

---

**最后更新**: 2026-01-14  
**版本**: MVP 3.1.0
