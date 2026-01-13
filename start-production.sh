#!/bin/bash

# TrendForge Localhost 生产模式启动脚本

set -e

echo "🚀 TrendForge Localhost 生产部署"
echo "=================================="
echo ""

# 颜色定义
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

# 检查端口
check_port() {
    if lsof -Pi :$1 -sTCP:LISTEN -t >/dev/null 2>&1 ; then
        echo -e "${YELLOW}⚠️  端口 $1 已被占用，正在停止...${NC}"
        lsof -ti:$1 | xargs kill -9 2>/dev/null || true
        sleep 2
    fi
}

# 1. 停止现有服务
echo "🛑 停止现有服务..."
check_port 8000
check_port 3000
echo ""

# 2. 构建前端
echo "📦 构建前端生产版本..."
cd frontend

# 检查依赖
if [ ! -d "node_modules" ]; then
    echo "📥 安装前端依赖..."
    pnpm install
fi

# 生成 Prisma 客户端
echo "🔧 生成 Prisma 客户端..."
pnpm prisma generate

# 构建
echo "🏗️  构建 Next.js 应用..."
pnpm build

if [ $? -ne 0 ]; then
    echo -e "${RED}❌ 前端构建失败${NC}"
    exit 1
fi

echo -e "${GREEN}✅ 前端构建完成${NC}"
cd ..
echo ""

# 3. 启动后端（生产模式）
echo "🔧 启动后端服务（生产模式）..."
cd backend

# 检查虚拟环境
if [ ! -d "venv" ]; then
    echo -e "${RED}❌ Python 虚拟环境不存在${NC}"
    exit 1
fi

source venv/bin/activate

# 检查 gunicorn
if ! python -c "import gunicorn" 2>/dev/null; then
    echo "📥 安装 gunicorn..."
    pip install gunicorn
fi

# 启动后端（后台运行）
echo "🚀 启动后端服务..."
nohup python -m uvicorn app_v2:app \
    --host 0.0.0.0 \
    --port 8000 \
    --workers 2 \
    --log-level info \
    > /tmp/trendforge-backend.log 2>&1 &

BACKEND_PID=$!
echo "后端进程 ID: $BACKEND_PID"
cd ..
echo ""

# 等待后端启动
echo "⏳ 等待后端启动..."
sleep 5

# 检查后端健康状态
for i in {1..10}; do
    if curl -s http://localhost:8000/health > /dev/null 2>&1; then
        echo -e "${GREEN}✅ 后端服务已启动${NC}"
        break
    fi
    if [ $i -eq 10 ]; then
        echo -e "${RED}❌ 后端服务启动失败，请检查日志: /tmp/trendforge-backend.log${NC}"
        exit 1
    fi
    sleep 2
done

# 4. 启动前端（生产模式）
echo "🌐 启动前端服务（生产模式）..."
cd frontend

# 启动前端（后台运行）
echo "🚀 启动前端服务..."
nohup pnpm start > /tmp/trendforge-frontend.log 2>&1 &

FRONTEND_PID=$!
echo "前端进程 ID: $FRONTEND_PID"
cd ..
echo ""

# 等待前端启动
echo "⏳ 等待前端启动..."
sleep 5

# 检查前端状态
for i in {1..10}; do
    if curl -s http://localhost:3000 > /dev/null 2>&1; then
        echo -e "${GREEN}✅ 前端服务已启动${NC}"
        break
    fi
    if [ $i -eq 10 ]; then
        echo -e "${RED}❌ 前端服务启动失败，请检查日志: /tmp/trendforge-frontend.log${NC}"
        exit 1
    fi
    sleep 2
done

# 5. 显示状态
echo ""
echo "=================================="
echo -e "${GREEN}🎉 TrendForge 生产模式已启动！${NC}"
echo "=================================="
echo ""
echo "📍 访问地址："
echo "  前端: http://localhost:3000"
echo "  后端 API: http://localhost:8000"
echo "  API 文档: http://localhost:8000/docs"
echo "  健康检查: http://localhost:8000/health"
echo ""
echo "📊 服务状态："
echo "  后端进程 ID: $BACKEND_PID"
echo "  前端进程 ID: $FRONTEND_PID"
echo ""
echo "📝 日志文件："
echo "  后端日志: /tmp/trendforge-backend.log"
echo "  前端日志: /tmp/trendforge-frontend.log"
echo ""
echo "🛑 停止服务："
echo "  kill $BACKEND_PID $FRONTEND_PID"
echo "  或运行: ./stop-production.sh"
echo ""
echo "✅ 部署完成！"
