#!/bin/bash
# 启动前端开发服务器

echo "🚀 启动 TrendForge 前端开发服务器..."
echo ""

# 检查端口是否被占用
if lsof -Pi :3000 -sTCP:LISTEN -t >/dev/null ; then
    echo "⚠️  端口 3000 已被占用"
    echo "   正在尝试停止现有进程..."
    lsof -ti:3000 | xargs kill -9 2>/dev/null
    sleep 2
fi

# 确保依赖已安装
echo "📦 检查依赖..."
pnpm install --silent

# 生成 Prisma 客户端
echo "🔧 生成 Prisma 客户端..."
pnpm prisma generate --silent

# 启动开发服务器
echo "✅ 启动开发服务器..."
echo "🌐 访问: http://localhost:3000"
echo ""
pnpm dev

