#!/bin/bash

# TrendForge - Localhost vs Production 对比脚本
# 用于诊断生产环境与 localhost 的差异

set -e

# 颜色定义
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

echo "🔍 TrendForge - Localhost vs Production 对比"
echo "=============================================="
echo ""

# 检查参数
if [ -z "$1" ]; then
    echo -e "${YELLOW}⚠️  请提供生产环境后端 URL${NC}"
    echo ""
    echo "用法:"
    echo "  ./compare_localhost_production.sh https://你的-railway-后端-url.up.railway.app"
    echo ""
    echo "示例:"
    echo "  ./compare_localhost_production.sh https://tf-mvp31.up.railway.app"
    exit 1
fi

PRODUCTION_URL="$1"
LOCALHOST_URL="http://localhost:8000"

echo -e "${BLUE}📊 对比配置:${NC}"
echo "  Localhost:  $LOCALHOST_URL"
echo "  生产环境:   $PRODUCTION_URL"
echo ""

# 函数：获取 JSON 并格式化
get_json() {
    local url="$1"
    local endpoint="$2"
    curl -s "${url}${endpoint}" 2>&1 | python3 -m json.tool 2>/dev/null || curl -s "${url}${endpoint}" 2>&1
}

# 函数：对比字段
compare_field() {
    local field="$1"
    local localhost_value="$2"
    local production_value="$3"
    
    if [ "$localhost_value" = "$production_value" ]; then
        echo -e "  ${GREEN}✅ ${field}: ${localhost_value}${NC}"
    else
        echo -e "  ${RED}❌ ${field}:${NC}"
        echo -e "     Localhost:  ${localhost_value}"
        echo -e "     生产环境:   ${production_value}"
    fi
}

# 1. 健康检查对比
echo -e "${BLUE}1️⃣ 健康检查对比${NC}"
echo "-------------------"

echo ""
echo "Localhost 健康检查:"
LOCALHOST_HEALTH=$(get_json "$LOCALHOST_URL" "/health")
echo "$LOCALHOST_HEALTH" | python3 -m json.tool 2>/dev/null || echo "$LOCALHOST_HEALTH"

echo ""
echo "生产环境健康检查:"
PRODUCTION_HEALTH=$(get_json "$PRODUCTION_URL" "/health")
echo "$PRODUCTION_HEALTH" | python3 -m json.tool 2>/dev/null || echo "$PRODUCTION_HEALTH"

# 提取关键字段
LOCALHOST_VERSION=$(echo "$LOCALHOST_HEALTH" | python3 -c "import sys, json; print(json.load(sys.stdin).get('version', 'N/A'))" 2>/dev/null || echo "N/A")
PRODUCTION_VERSION=$(echo "$PRODUCTION_HEALTH" | python3 -c "import sys, json; print(json.load(sys.stdin).get('version', 'N/A'))" 2>/dev/null || echo "N/A")

echo ""
echo -e "${YELLOW}📋 关键字段对比:${NC}"
compare_field "版本号" "$LOCALHOST_VERSION" "$PRODUCTION_VERSION"

# 2. 完整系统状态对比（如果可用）
echo ""
echo -e "${BLUE}2️⃣ 完整系统状态对比${NC}"
echo "-------------------"

echo ""
echo "Localhost 系统状态:"
LOCALHOST_STATUS=$(get_json "$LOCALHOST_URL" "/debug/full-status")
if echo "$LOCALHOST_STATUS" | grep -q "Not Found"; then
    echo -e "${YELLOW}⚠️  /debug/full-status 端点未找到（可能需要重启后端）${NC}"
else
    echo "$LOCALHOST_STATUS" | python3 -m json.tool 2>/dev/null || echo "$LOCALHOST_STATUS"
fi

echo ""
echo "生产环境系统状态:"
PRODUCTION_STATUS=$(get_json "$PRODUCTION_URL" "/debug/full-status")
if echo "$PRODUCTION_STATUS" | grep -q "Not Found"; then
    echo -e "${YELLOW}⚠️  /debug/full-status 端点未找到（可能需要重新部署）${NC}"
else
    echo "$PRODUCTION_STATUS" | python3 -m json.tool 2>/dev/null || echo "$PRODUCTION_STATUS"
fi

# 3. 分析器状态对比
echo ""
echo -e "${BLUE}3️⃣ 分析器状态对比${NC}"
echo "-------------------"

echo ""
echo "Localhost 分析器状态:"
LOCALHOST_ANALYZER=$(get_json "$LOCALHOST_URL" "/debug/analyzer")
if echo "$LOCALHOST_ANALYZER" | grep -q "Not Found"; then
    echo -e "${YELLOW}⚠️  /debug/analyzer 端点未找到${NC}"
else
    echo "$LOCALHOST_ANALYZER" | python3 -m json.tool 2>/dev/null || echo "$LOCALHOST_ANALYZER"
fi

echo ""
echo "生产环境分析器状态:"
PRODUCTION_ANALYZER=$(get_json "$PRODUCTION_URL" "/debug/analyzer")
if echo "$PRODUCTION_ANALYZER" | grep -q "Not Found"; then
    echo -e "${YELLOW}⚠️  /debug/analyzer 端点未找到${NC}"
else
    echo "$PRODUCTION_ANALYZER" | python3 -m json.tool 2>/dev/null || echo "$PRODUCTION_ANALYZER"
fi

# 4. 总结
echo ""
echo -e "${BLUE}📊 对比总结${NC}"
echo "-------------------"

if [ "$LOCALHOST_VERSION" != "$PRODUCTION_VERSION" ]; then
    echo -e "${RED}❌ 版本不一致！${NC}"
    echo "   Localhost:  $LOCALHOST_VERSION"
    echo "   生产环境:   $PRODUCTION_VERSION"
    echo ""
    echo "   建议：重新部署后端以确保版本一致"
else
    echo -e "${GREEN}✅ 版本一致: $LOCALHOST_VERSION${NC}"
fi

echo ""
echo -e "${YELLOW}💡 下一步操作:${NC}"
echo "  1. 如果版本不一致，重新部署后端"
echo "  2. 检查环境变量配置（Vercel 和 Railway）"
echo "  3. 清除数据库缓存并重新分析频道"
echo "  4. 对比数据字段和值"
echo ""
