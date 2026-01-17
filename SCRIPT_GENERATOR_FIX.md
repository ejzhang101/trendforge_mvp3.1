# 脚本生成功能修复指南

**问题**: 脚本生成失败，显示 "Load failed" 错误

## 🔍 问题诊断

### 后端状态检查

✅ **Script Generator**: 已启用  
✅ **OpenAI API Key**: 已配置

### 可能原因

1. **前端环境变量未配置**
   - `NEXT_PUBLIC_BACKEND_SERVICE_URL` 可能未在 Vercel 中设置
   - 前端组件直接调用后端，需要正确的后端 URL

2. **CORS 问题**
   - 前端直接调用后端可能被 CORS 阻止

3. **网络连接问题**
   - 前端无法访问后端 URL

## 🔧 修复方案

### 方案 1: 配置前端环境变量（推荐）

在 Vercel Dashboard 中配置：

1. 打开 Vercel 项目设置
2. 进入 **Settings** → **Environment Variables**
3. 添加环境变量：
   ```
   NEXT_PUBLIC_BACKEND_SERVICE_URL=https://tf-mvp31.up.railway.app
   ```
4. 重新部署前端

### 方案 2: 使用前端 API 路由代理（更安全）

修改 `ScriptGenerator.tsx`，通过前端 API 路由调用后端，而不是直接调用。

**优点**:
- 不需要暴露后端 URL 到前端
- 避免 CORS 问题
- 统一错误处理

**实现步骤**:

1. 创建前端 API 路由：`frontend/app/api/generate-scripts/route.ts`

```typescript
import { NextRequest, NextResponse } from 'next/server';

export async function POST(request: NextRequest) {
  try {
    const body = await request.json();
    
    const backendUrl = process.env.BACKEND_SERVICE_URL || 'http://localhost:8000';
    const backendBaseUrl = backendUrl.startsWith('http') 
      ? backendUrl 
      : `https://${backendUrl}`;
    
    const response = await fetch(`${backendBaseUrl}/api/v3/generate-scripts`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(body),
    });
    
    if (!response.ok) {
      const errorText = await response.text();
      return NextResponse.json(
        { success: false, error: errorText },
        { status: response.status }
      );
    }
    
    const data = await response.json();
    return NextResponse.json(data);
  } catch (error: any) {
    console.error('Script generation error:', error);
    return NextResponse.json(
      { success: false, error: error.message },
      { status: 500 }
    );
  }
}
```

2. 修改 `ScriptGenerator.tsx`，使用前端 API 路由：

```typescript
// 修改前
const response = await fetch(`${backendBaseUrl}/api/v3/generate-scripts`, {
  // ...
});

// 修改后
const response = await fetch('/api/generate-scripts', {
  method: 'POST',
  headers: { 'Content-Type': 'application/json' },
  body: JSON.stringify({
    user_prompt: userPrompt,
    channel_analysis: {
      // ...
    },
    recommendations: recommendations.map((rec: any) => ({
      // ...
    })),
    count: 3
  })
});
```

### 方案 3: 检查并修复 CORS 配置

确保后端 CORS 配置允许前端域名：

在 `backend/app_v2.py` 中检查：

```python
allowed_origins = [
    "http://localhost:3000",
    "https://*.vercel.app",
    # 添加您的 Vercel 域名
]
```

## 📋 验证步骤

### 1. 检查前端环境变量

在浏览器控制台执行：

```javascript
console.log('Backend URL:', process.env.NEXT_PUBLIC_BACKEND_SERVICE_URL);
```

如果显示 `undefined`，说明环境变量未配置。

### 2. 测试后端 API

```bash
curl -X POST https://tf-mvp31.up.railway.app/api/v3/generate-scripts \
  -H "Content-Type: application/json" \
  -d '{
    "user_prompt": "测试产品描述",
    "channel_analysis": {
      "topics": [],
      "content_style": {},
      "target_audience": {},
      "high_performers": {}
    },
    "recommendations": [],
    "count": 1
  }'
```

### 3. 检查浏览器网络请求

1. 打开浏览器开发者工具（F12）
2. 切换到 **Network** 标签
3. 尝试生成脚本
4. 查看失败的请求：
   - 请求 URL 是否正确
   - 响应状态码
   - 错误信息

## 🐛 常见错误

### 错误 1: "Failed to fetch"

**原因**: 网络连接问题或 CORS 问题

**解决**:
- 检查后端 URL 是否正确
- 检查 CORS 配置
- 使用前端 API 路由代理

### 错误 2: "Script generator not available"

**原因**: 后端脚本生成器未初始化

**解决**:
- 检查后端日志
- 验证 `SCRIPT_GENERATOR_AVAILABLE` 是否为 `True`
- 检查 OpenAI API 密钥是否正确

### 错误 3: "OpenAI API error"

**原因**: OpenAI API 调用失败

**解决**:
- 检查 `OPENAI_API_KEY` 是否正确
- 检查 API 配额是否用完
- 查看后端日志中的详细错误信息

## ✅ 修复后的验证

修复后，应该能够：
1. ✅ 输入产品描述
2. ✅ 点击"生成脚本"按钮
3. ✅ 看到"生成中..."状态
4. ✅ 成功生成脚本并显示结果
5. ✅ 没有 "Load failed" 错误

---

**更新日期**: 2026-01-17
