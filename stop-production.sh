#!/bin/bash

# TrendForge 生产模式停止脚本

echo "🛑 停止 TrendForge 生产服务..."
echo ""

# 停止后端
if lsof -Pi :8000 -sTCP:LISTEN -t >/dev/null 2>&1 ; then
    echo "停止后端服务 (端口 8000)..."
    lsof -ti:8000 | xargs kill -9 2>/dev/null
    sleep 1
    echo "✅ 后端服务已停止"
else
    echo "⚠️  后端服务未运行"
fi

# 停止前端
if lsof -Pi :3000 -sTCP:LISTEN -t >/dev/null 2>&1 ; then
    echo "停止前端服务 (端口 3000)..."
    lsof -ti:3000 | xargs kill -9 2>/dev/null
    sleep 1
    echo "✅ 前端服务已停止"
else
    echo "⚠️  前端服务未运行"
fi

echo ""
echo "✅ 所有服务已停止"
