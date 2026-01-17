#!/bin/bash
# 测试 ML 功能是否正常工作

echo "=== 🧪 测试 MVP 3.1 ML 功能 ==="
echo ""

# 检查后端是否运行
BACKEND_URL="${BACKEND_URL:-http://localhost:8000}"

echo "1. 检查健康状态..."
HEALTH=$(curl -s "$BACKEND_URL/health" 2>/dev/null)

if [ $? -ne 0 ]; then
    echo "❌ 后端服务未运行，请先启动: cd backend && python app_v2.py"
    exit 1
fi

echo "✅ 后端服务运行中"
echo ""

# 检查 ML 模块状态
echo "2. 检查 ML 模块状态..."
ML_PREDICTOR=$(echo "$HEALTH" | grep -o '"ml_predictor":[^,]*' | cut -d: -f2)
SEMANTIC_ANALYZER=$(echo "$HEALTH" | grep -o '"semantic_analyzer":[^,]*' | cut -d: -f2)

echo "   ML Predictor: $ML_PREDICTOR"
echo "   Semantic Analyzer: $SEMANTIC_ANALYZER"
echo ""

if [ "$ML_PREDICTOR" = "true" ] && [ "$SEMANTIC_ANALYZER" = "true" ]; then
    echo "✅ ML 功能已启用！"
    echo ""
    echo "3. 测试 API（使用 ML 功能）..."
    
    # 测试 API（简化版）
    TEST_RESPONSE=$(curl -s -X POST "$BACKEND_URL/api/v2/full-analysis" \
        -H "Content-Type: application/json" \
        -d '{
            "videos": [{"videoId": "test", "title": "AI Tutorial", "viewCount": 1000, "publishedAt": "2024-01-01"}],
            "channel_data": {"subscriberCount": 10000},
            "use_ml_prediction": true,
            "use_semantic_keywords": true,
            "max_recommendations": 1
        }' 2>/dev/null)
    
    if echo "$TEST_RESPONSE" | grep -q "success"; then
        echo "✅ API 测试成功！"
        echo ""
        echo "📊 ML 功能已正常工作"
        echo "   - XGBoost 预测: 可用"
        echo "   - KeyBERT 语义分析: 可用"
    else
        echo "⚠️  API 测试失败，但 ML 模块已加载"
        echo "   响应: $(echo "$TEST_RESPONSE" | head -c 200)"
    fi
else
    echo "⚠️  ML 功能未完全启用"
    echo "   请检查依赖是否正确安装"
fi

echo ""
echo "=== 测试完成 ==="
