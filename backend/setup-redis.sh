#!/bin/bash

echo "🚀 配置 Redis 缓存..."
echo ""

# 检查 Homebrew
if ! command -v brew &> /dev/null; then
    echo "📦 安装 Homebrew..."
    /bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"
    
    # 添加 Homebrew 到 PATH（如果在新架构 Mac 上）
    if [ -f /opt/homebrew/bin/brew ]; then
        eval "$(/opt/homebrew/bin/brew shellenv)"
    fi
fi

# 安装 Redis
if ! command -v redis-cli &> /dev/null; then
    echo "📦 安装 Redis..."
    brew install redis
else
    echo "✅ Redis 已安装"
fi

# 启动 Redis
echo "🔄 启动 Redis 服务..."
brew services start redis 2>/dev/null || redis-server --daemonize yes

# 等待 Redis 启动
sleep 2

# 验证 Redis
if redis-cli ping 2>/dev/null | grep -q "PONG"; then
    echo "✅ Redis 运行正常"
else
    echo "❌ Redis 启动失败，请手动检查"
    echo "   尝试运行: redis-server"
    exit 1
fi

# 配置 .env
cd "$(dirname "$0")"
if [ -f .env ]; then
    if ! grep -q "REDIS_URL" .env; then
        echo "" >> .env
        echo "# Redis 缓存配置" >> .env
        echo "REDIS_URL=redis://localhost:6379" >> .env
        echo "✅ .env 已更新"
    else
        echo "ℹ️ REDIS_URL 已存在于 .env"
    fi
else
    echo "📝 创建 .env 文件..."
    echo "REDIS_URL=redis://localhost:6379" > .env
    echo "✅ .env 已创建"
fi

echo ""
echo "🎉 Redis 配置完成！"
echo ""
echo "下一步："
echo "  1. 重启后端服务: python app_v2.py"
echo "  2. 验证连接: curl http://localhost:8000/health | python3 -m json.tool | grep cache"
echo ""
echo "预期结果: \"cache\": true"
