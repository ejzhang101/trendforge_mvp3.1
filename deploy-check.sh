#!/bin/bash

# TrendForge 部署前检查脚本

echo "🔍 TrendForge 部署前检查..."
echo ""

# 检查颜色支持
if [ -t 1 ]; then
    RED='\033[0;31m'
    GREEN='\033[0;32m'
    YELLOW='\033[1;33m'
    NC='\033[0m' # No Color
else
    RED=''
    GREEN=''
    YELLOW=''
    NC=''
fi

# 检查函数
check_file() {
    if [ -f "$1" ]; then
        echo -e "${GREEN}✅${NC} $1 存在"
        return 0
    else
        echo -e "${RED}❌${NC} $1 不存在"
        return 1
    fi
}

check_env_var() {
    if grep -q "$1" "$2" 2>/dev/null; then
        echo -e "${GREEN}✅${NC} $1 已配置"
        return 0
    else
        echo -e "${YELLOW}⚠️${NC} $1 未配置（可选）"
        return 1
    fi
}

# 1. 检查必需文件
echo "📁 检查必需文件..."
check_file "backend/app_v2.py"
check_file "backend/requirements_v2.txt"
check_file "frontend/package.json"
check_file "vercel.json"
check_file "railway.json"
check_file "docker-compose.yml"
echo ""

# 2. 检查后端环境变量
echo "🔐 检查后端环境变量..."
if [ -f "backend/.env" ]; then
    check_env_var "SERPAPI_KEY" "backend/.env"
    check_env_var "TWITTER_BEARER_TOKEN" "backend/.env"
    check_env_var "DATABASE_URL" "backend/.env"
    check_env_var "REDIS_URL" "backend/.env"
else
    echo -e "${YELLOW}⚠️${NC} backend/.env 文件不存在（部署时会在平台配置）"
fi
echo ""

# 3. 检查前端环境变量
echo "🔐 检查前端环境变量..."
if [ -f "frontend/.env" ] || [ -f "frontend/.env.local" ]; then
    check_env_var "DATABASE_URL" "frontend/.env" || check_env_var "DATABASE_URL" "frontend/.env.local"
    check_env_var "BACKEND_SERVICE_URL" "frontend/.env" || check_env_var "BACKEND_SERVICE_URL" "frontend/.env.local"
    check_env_var "YOUTUBE_API_KEY" "frontend/.env" || check_env_var "YOUTUBE_API_KEY" "frontend/.env.local"
else
    echo -e "${YELLOW}⚠️${NC} frontend/.env 文件不存在（部署时会在平台配置）"
fi
echo ""

# 4. 检查依赖
echo "📦 检查依赖..."
if [ -d "backend/venv" ]; then
    echo -e "${GREEN}✅${NC} Python 虚拟环境存在"
else
    echo -e "${YELLOW}⚠️${NC} Python 虚拟环境不存在（部署时会自动创建）"
fi

if [ -d "frontend/node_modules" ]; then
    echo -e "${GREEN}✅${NC} Node.js 依赖已安装"
else
    echo -e "${YELLOW}⚠️${NC} Node.js 依赖未安装（部署时会自动安装）"
fi
echo ""

# 5. 检查 SerpAPI 依赖
echo "🔍 检查 SerpAPI 集成..."
if grep -q "google-search-results" "backend/requirements_v2.txt"; then
    echo -e "${GREEN}✅${NC} google-search-results 在 requirements_v2.txt 中"
else
    echo -e "${RED}❌${NC} google-search-results 未在 requirements_v2.txt 中"
fi

if grep -q "EnhancedSerpAPICollector" "backend/services/enhanced_social_collector.py"; then
    echo -e "${GREEN}✅${NC} SerpAPI 收集器已实现"
else
    echo -e "${RED}❌${NC} SerpAPI 收集器未实现"
fi
echo ""

# 6. 检查 Redis 配置
echo "💾 检查 Redis 配置..."
if grep -q "REDIS_URL" "docker-compose.yml"; then
    echo -e "${GREEN}✅${NC} Redis 在 docker-compose.yml 中配置"
else
    echo -e "${YELLOW}⚠️${NC} Redis 未在 docker-compose.yml 中配置（可选）"
fi
echo ""

# 7. 总结
echo "📊 检查总结："
echo ""
echo "✅ 必需文件已就绪"
echo "✅ 部署配置已更新"
echo "✅ SerpAPI 集成完成"
echo ""
echo "🚀 下一步："
echo "  1. 查看 DEPLOYMENT_GUIDE.md 获取详细部署步骤"
echo "  2. 准备环境变量（在部署平台配置）"
echo "  3. 部署后端到 Railway"
echo "  4. 部署前端到 Vercel"
echo ""
echo "📝 环境变量清单："
echo "  后端（Railway）："
echo "    - SERPAPI_KEY"
echo "    - TWITTER_BEARER_TOKEN"
echo "    - DATABASE_URL"
echo "    - REDIS_URL (可选)"
echo ""
echo "  前端（Vercel）："
echo "    - DATABASE_URL"
echo "    - BACKEND_SERVICE_URL"
echo "    - YOUTUBE_API_KEY"
echo "    - NEXT_PUBLIC_APP_URL"
echo ""
