# 智能脚本生成器 - LLM 增强版

## 概述

脚本生成器已增强为支持 AI 语义分析和智能脚本生成。系统会自动检测是否配置了 OpenAI API，如果可用则使用 LLM 生成更智能的脚本，否则回退到模板方式。

## 功能特性

### 1. AI 语义分析（LLM 模式）
- **中英文支持**：自动识别并处理中文和英文输入
- **结构化提取**：从用户输入中提取：
  - 产品/服务类型
  - 目标客户群体
  - 核心优势/卖点
  - 使用场景
  - 行业领域
  - 产品名称

### 2. 智能脚本生成（LLM 模式）
- **上下文感知**：结合频道分析、推荐话题、产品信息生成脚本
- **个性化内容**：根据频道风格和目标受众定制脚本
- **自然语言生成**：使用 GPT-4o-mini 生成流畅、专业的脚本内容

### 3. 回退机制
- 如果未配置 OpenAI API，系统自动使用模板方式生成脚本
- 如果 LLM 调用失败，自动回退到模板方式
- 确保功能始终可用

## 配置步骤

### 1. 安装依赖

```bash
cd backend
source venv/bin/activate
pip install "openai>=1.3.0"
```

### 2. 配置 API Key

在 `backend/.env` 文件中添加：

```bash
OPENAI_API_KEY=your_openai_api_key_here
```

获取 API Key：
1. 访问 https://platform.openai.com/api-keys
2. 创建新的 API Key
3. 复制到 `.env` 文件

### 3. 重启后端服务

```bash
# 停止当前服务
lsof -tiTCP:8000 -sTCP:LISTEN | xargs kill -9

# 启动服务
cd backend
source venv/bin/activate
python app_v2.py
```

## 使用方式

### 前端使用

1. 在分析页面，点击任意推荐话题
2. 在弹窗中切换到 "✍️ AI 脚本生成" 标签
3. 输入产品/服务描述（支持中英文）
4. 点击 "生成脚本" 按钮

### API 调用

```bash
curl -X POST http://localhost:8000/api/v3/generate-scripts \
  -H "Content-Type: application/json" \
  -d '{
    "user_prompt": "我们是B端电商企业，主要向企业客户销售电子产品",
    "channel_analysis": {
      "topics": [{"topic": "tech", "score": 0.8}],
      "content_style": {"primary_style": "educational"},
      "target_audience": {"primary_age_group": "25-35岁"},
      "high_performers": {"avg_views": 10000}
    },
    "recommendations": [
      {"keyword": "tech", "match_score": 75, "viral_potential": 60}
    ],
    "count": 3
  }'
```

## 工作流程

### LLM 模式（已配置 API Key）

1. **语义分析阶段**：
   - 使用 GPT-4o-mini 分析用户输入
   - 提取结构化产品信息
   - 支持中英文混合输入

2. **脚本生成阶段**：
   - 结合频道分析、推荐话题、产品信息
   - 使用 GPT-4o-mini 生成完整脚本
   - 包含标题、Hook、主体内容、CTA 等

3. **质量保证**：
   - 验证生成内容的完整性
   - 如果 LLM 返回格式错误，自动回退到模板

### 模板模式（未配置 API Key）

1. **基础解析**：
   - 使用关键词提取
   - 使用预定义模板

2. **模板填充**：
   - 根据频道风格选择模板
   - 填充产品信息和话题关键词

## 性能优化

- **模型选择**：使用 `gpt-4o-mini` 以降低成本和提高速度
- **Token 限制**：语义分析 500 tokens，脚本生成 2000 tokens
- **错误处理**：完善的错误处理和回退机制
- **缓存友好**：解析结果可缓存，减少重复调用

## 示例

### 中文输入示例

```
我们是B端电商企业，主要向企业客户销售电子产品（如办公设备、智能硬件），
目标客户是中小企业的采购部门，产品优势是批量采购优惠、企业级服务支持、快速交付
```

**LLM 解析结果**：
```json
{
  "product_type": "B2B电商平台",
  "target_customers": "中小企业的采购部门",
  "key_advantages": ["批量采购优惠", "企业级服务支持", "快速交付"],
  "use_cases": "企业批量采购办公设备和智能硬件",
  "industry": "B2B电商",
  "product_name": ""
}
```

### 英文输入示例

```
We are a B2B e-commerce platform selling electronic products to enterprise clients.
Our target customers are procurement departments of SMEs. Key advantages include bulk
purchase discounts, enterprise-grade support, and fast delivery.
```

**LLM 解析结果**：
```json
{
  "product_type": "B2B e-commerce platform",
  "target_customers": "procurement departments of SMEs",
  "key_advantages": ["bulk purchase discounts", "enterprise-grade support", "fast delivery"],
  "use_cases": "Enterprise bulk purchasing of electronic products",
  "industry": "B2B e-commerce",
  "product_name": ""
}
```

## 故障排除

### LLM 未初始化

**症状**：日志显示 "⚠️ OPENAI_API_KEY not found"

**解决**：
1. 检查 `.env` 文件是否存在
2. 确认 `OPENAI_API_KEY` 已正确配置
3. 重启后端服务

### LLM 调用失败

**症状**：脚本生成失败，回退到模板

**解决**：
1. 检查 API Key 是否有效
2. 检查网络连接
3. 查看后端日志了解具体错误

### JSON 解析错误

**症状**：日志显示 "⚠️ LLM returned invalid JSON"

**解决**：
- 系统会自动回退到模板方式
- 这是正常的容错机制，不影响功能使用

## 成本估算

使用 `gpt-4o-mini` 的成本：
- 语义分析：约 $0.00015 / 请求（500 tokens）
- 脚本生成：约 $0.0006 / 请求（2000 tokens）
- 总计：约 $0.00075 / 脚本生成请求

**注意**：实际成本取决于实际使用的 tokens 数量。

## 更新日志

- **2026-01-14**: 初始版本，支持 LLM 语义分析和智能脚本生成
- 支持中英文输入
- 自动回退机制
- 完善的错误处理
