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
