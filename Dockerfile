# TrendForge Backend - Railway Dockerfile
# 完整版 NLTK 数据支持

FROM python:3.11-slim

WORKDIR /app

# 环境变量
ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PIP_NO_CACHE_DIR=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1 \
    NLTK_DATA=/usr/local/share/nltk_data

# 安装系统依赖
RUN apt-get update && \
    apt-get install -y --no-install-recommends gcc g++ && \
    rm -rf /var/lib/apt/lists/*

# 复制依赖文件
COPY backend/requirements_v2.txt backend/

# 安装 Python 依赖
RUN pip install --upgrade pip && \
    pip install --no-cache-dir -r backend/requirements_v2.txt

# 下载所有 NLTK 数据（一次性全部下载，避免运行时缺失）
RUN python -c "import nltk; \
    nltk.download('punkt', download_dir='/usr/local/share/nltk_data', quiet=False); \
    nltk.download('punkt_tab', download_dir='/usr/local/share/nltk_data', quiet=False); \
    nltk.download('stopwords', download_dir='/usr/local/share/nltk_data', quiet=False); \
    nltk.download('averaged_perceptron_tagger', download_dir='/usr/local/share/nltk_data', quiet=False); \
    nltk.download('averaged_perceptron_tagger_eng', download_dir='/usr/local/share/nltk_data', quiet=False); \
    nltk.download('wordnet', download_dir='/usr/local/share/nltk_data', quiet=False); \
    nltk.download('omw-1.4', download_dir='/usr/local/share/nltk_data', quiet=False); \
    print('✅ All NLTK data downloaded successfully')"

# 复制应用代码
COPY backend/ backend/

# 暴露端口
EXPOSE 8000

# 健康检查
HEALTHCHECK --interval=30s --timeout=10s --start-period=40s --retries=3 \
    CMD python -c "import requests; requests.get('http://localhost:8000/health', timeout=5)" || exit 1

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
