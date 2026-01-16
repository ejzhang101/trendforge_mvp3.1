#!/bin/bash
# Vercel CLI 部署脚本

echo "=== 🚀 Vercel CLI 部署脚本 ==="
echo ""

# 检查是否在 frontend 目录
if [ ! -f "package.json" ]; then
    echo "❌ 错误: 请在 frontend 目录中运行此脚本"
    exit 1
fi

echo "📋 当前目录: $(pwd)"
echo ""

# 检查 Node.js
if ! command -v node &> /dev/null; then
    echo "⚠️  Node.js 未找到，尝试加载环境..."
    
    # 尝试加载 Homebrew (Apple Silicon)
    if [ -f /opt/homebrew/bin/brew ]; then
        eval "$(/opt/homebrew/bin/brew shellenv)"
    fi
    
    # 尝试加载 Homebrew (Intel)
    if [ -f /usr/local/bin/brew ]; then
        eval "$(/usr/local/bin/brew shellenv)"
    fi
    
    # 尝试加载 nvm
    if [ -f ~/.nvm/nvm.sh ]; then
        source ~/.nvm/nvm.sh
        nvm use node 2>/dev/null || true
    fi
    
    # 尝试加载 zshrc/bashrc
    if [ -f ~/.zshrc ]; then
        source ~/.zshrc 2>/dev/null || true
    fi
    if [ -f ~/.bashrc ]; then
        source ~/.bashrc 2>/dev/null || true
    fi
fi

# 检查 Vercel CLI
if ! command -v vercel &> /dev/null; then
    echo "📦 安装 Vercel CLI..."
    if command -v npm &> /dev/null; then
        npm i -g vercel
    elif command -v pnpm &> /dev/null; then
        pnpm add -g vercel
    else
        echo "❌ 错误: 未找到 npm 或 pnpm"
        echo "请先安装 Node.js: https://nodejs.org/"
        exit 1
    fi
fi

echo "✅ Vercel CLI 已就绪"
echo ""

# 登录检查
echo "🔐 检查 Vercel 登录状态..."
if ! vercel whoami &> /dev/null; then
    echo "请先登录 Vercel:"
    vercel login
fi

echo ""
echo "🚀 开始部署到生产环境..."
echo ""

# 部署
vercel --prod

echo ""
echo "✅ 部署完成！"
