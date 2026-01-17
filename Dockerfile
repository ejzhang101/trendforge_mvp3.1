# TrendForge Backend - Railway Dockerfile
# 这个配置 100% 可靠，Railway 会完全按照这个来构建

FROM python:3.11-slim

# 设置工作目录
WORKDIR /app

# 设置环境变量
ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PIP_NO_CACHE_DIR=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1

# 安装系统依赖（最小化）
RUN apt-get update && \
    apt-get install -y --no-install-recommends gcc g++ && \
    rm -rf /var/lib/apt/lists/*

# 复制依赖文件
COPY backend/requirements_v2.txt backend/

# 安装 Python 依赖
RUN pip install --upgrade pip && \
    pip install --no-cache-dir -r backend/requirements_v2.txt

# 下载 NLTK 数据（包括 punkt_tab for NLTK 3.8.1+）
# 设置 NLTK_DATA 环境变量，确保数据下载到正确位置
ENV NLTK_DATA=/usr/local/share/nltk_data
RUN python -c "import nltk; nltk.download('punkt', quiet=True); nltk.download('punkt_tab', quiet=True); nltk.download('stopwords', quiet=True); nltk.download('averaged_perceptron_tagger', quiet=True); nltk.download('wordnet', quiet=True)" && \
    python -c "import nltk; nltk.data.path.append('/usr/local/share/nltk_data')"

# 复制应用代码
COPY backend/ backend/

# 暴露端口（Railway 会自动分配 $PORT）
EXPOSE 8000

# 健康检查（使用 curl 或跳过，因为 requests 可能未安装）
HEALTHCHECK --interval=30s --timeout=10s --start-period=40s --retries=3 \
    CMD python -c "import urllib.request; urllib.request.urlopen('http://localhost:8000/health', timeout=5)" || exit 1

# 启动命令
CMD cd backend && \
    gunicorn app_v2:app \
    --workers 1 \
    --worker-class uvicorn.workers.UvicornWorker \
    --bind 0.0.0.0:${PORT:-8000} \
    --timeout 120 \
    --access-logfile - \
    --error-logfile - \
    --log-level info
