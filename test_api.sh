#!/bin/bash

echo "🔍 Testing TrendForge API Endpoints..."
echo ""

# Test 1: Health Check
echo "1️⃣ Testing Health Endpoint..."
HEALTH_RESPONSE=$(curl -s http://localhost:8000/health)
if echo "$HEALTH_RESPONSE" | grep -q "healthy"; then
    echo "✅ Health check: PASSED"
    echo "$HEALTH_RESPONSE" | python3 -m json.tool | head -15
else
    echo "❌ Health check: FAILED"
    echo "$HEALTH_RESPONSE"
fi
echo ""

# Test 2: Root Endpoint
echo "2️⃣ Testing Root Endpoint..."
ROOT_RESPONSE=$(curl -s http://localhost:8000/)
if echo "$ROOT_RESPONSE" | grep -q "version"; then
    echo "✅ Root endpoint: PASSED"
    echo "$ROOT_RESPONSE" | python3 -m json.tool | head -10
else
    echo "❌ Root endpoint: FAILED"
    echo "$ROOT_RESPONSE"
fi
echo ""

# Test 3: Frontend Check
echo "3️⃣ Testing Frontend..."
FRONTEND_RESPONSE=$(curl -s -o /dev/null -w "%{http_code}" http://localhost:3000)
if [ "$FRONTEND_RESPONSE" = "200" ]; then
    echo "✅ Frontend: PASSED (HTTP $FRONTEND_RESPONSE)"
else
    echo "❌ Frontend: FAILED (HTTP $FRONTEND_RESPONSE)"
fi
echo ""

# Test 4: Backend Port Check
echo "4️⃣ Checking Backend Port..."
if lsof -ti:8000 > /dev/null 2>&1; then
    echo "✅ Backend port 8000: LISTENING"
else
    echo "❌ Backend port 8000: NOT LISTENING"
fi
echo ""

# Test 5: Frontend Port Check
echo "5️⃣ Checking Frontend Port..."
if lsof -ti:3000 > /dev/null 2>&1; then
    echo "✅ Frontend port 3000: LISTENING"
else
    echo "❌ Frontend port 3000: NOT LISTENING"
fi
echo ""

echo "📊 Test Summary Complete"
