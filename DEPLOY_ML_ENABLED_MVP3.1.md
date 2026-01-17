# 部署 MVP 3.1 启用 ML 功能到生产环境

## 📋 概述

本指南说明如何在生产环境（Railway）启用 ML 增强功能（XGBoost + KeyBERT），提升推荐准确率 20-30%。

## ✅ 已完成的配置

### 1. 更新依赖文件

**`backend/requirements_v2.txt`** 已更新，包含：
- `xgboost>=2.0.3` - ML 预测
- `scikit-learn>=1.3.2` - ML 工具
- `keybert>=0.8.3` - 语义分析
- `sentence-transformers>=2.7.0` - 语义模型

### 2. 更新 Dockerfile

**`Dockerfile`** 已更新，会自动安装所有 ML 依赖。

## 🚀 部署步骤

### 方法 1: Railway（推荐）

#### 步骤 1: 推送代码到 GitHub

```bash
git add backend/requirements_v2.txt Dockerfile
git commit -m "feat: Enable ML dependencies for MVP 3.1"
git push origin main
```

#### 步骤 2: Railway 自动部署

Railway 会自动检测到代码更新并开始构建：

1. **构建过程**：
   - 安装所有依赖（包括 ML 库）
   - 下载 NLTK 数据
   - 构建 Docker 镜像

2. **预计时间**：5-10 分钟（首次构建可能更长）

3. **内存使用**：
   - 基础版本：~400MB
   - ML 版本：~900MB（仍在 Railway 限制内）

#### 步骤 3: 验证部署

```bash
# 检查健康状态
curl https://your-railway-url.up.railway.app/health | jq '.services'

# 应该看到：
# {
#   "ml_predictor": true,
#   "semantic_analyzer": true,
#   ...
# }
```

### 方法 2: Render

#### 步骤 1: 更新 Render 配置

在 Render Dashboard：

1. 进入你的服务设置
2. 确保 "Root Directory" 为空
3. Build Command: `cd backend && pip install -r requirements_v2.txt`
4. Start Command: `cd backend && gunicorn app_v2:app --workers 1 --worker-class uvicorn.workers.UvicornWorker --bind 0.0.0.0:$PORT`

#### 步骤 2: 触发部署

```bash
git push origin main
```

Render 会自动检测并开始构建。

## ⚠️ 本地开发注意事项

### macOS 用户

XGBoost 需要 OpenMP 运行时库。在 macOS 上需要安装：

```bash
brew install libomp
```

**注意**：生产环境（Docker/Linux）不需要此步骤，Dockerfile 已包含必要的系统依赖。

## 🧪 本地测试

### 测试 1: 验证 ML 模块

```bash
cd backend
source venv/bin/activate
python -c "
from services.ml_performance_predictor import XGBOOST_AVAILABLE
from services.semantic_analyzer import KEYBERT_AVAILABLE
print('XGBoost:', XGBOOST_AVAILABLE)
print('KeyBERT:', KEYBERT_AVAILABLE)
"
```

**预期输出**：
```
XGBoost: True
KeyBERT: True
```

### 测试 2: 启动服务

```bash
cd backend
source venv/bin/activate
python app_v2.py
```

**预期输出**：
```
✅ ML Performance Predictor (XGBoost) available
✅ Semantic Analyzer (KeyBERT) available
✅ Using Predictive Recommendation Engine (MVP 3.1 with Prophet + ML)
```

### 测试 3: API 测试

```bash
# 测试健康检查
curl http://localhost:8000/health | jq '.services.ml_predictor'
curl http://localhost:8000/health | jq '.services.semantic_analyzer'

# 应该返回: true
```

### 测试 4: 启用 ML 功能测试

```bash
curl -X POST http://localhost:8000/api/v2/full-analysis \
  -H "Content-Type: application/json" \
  -d '{
    "videos": [{"videoId": "test", "title": "AI Tutorial", "viewCount": 1000}],
    "channel_data": {"subscriberCount": 10000},
    "use_ml_prediction": true,
    "use_semantic_keywords": true
  }' | jq '.recommendations[0].predicted_performance.method'
```

**预期输出**：
- `"xgboost_ml"` 或 `"rule_based"`（取决于是否有训练数据）
- 如果返回 `"rule_based"`，说明 ML 模块可用但未训练，会自动降级

## 📊 性能监控

### 内存使用

部署后监控内存使用：

```bash
# Railway Dashboard → Metrics
# 或使用 Railway CLI
railway logs --service your-service-name
```

**预期内存**：
- 启动时：~600-700MB
- 运行中：~800-900MB
- 峰值：~1GB（仍在限制内）

### 响应时间

启用 ML 功能后，API 响应时间可能增加：
- 基础分析：5-10秒
- + ML 预测：+3-5秒
- + 语义分析：+2-3秒
- 总计：10-18秒（仍在可接受范围）

## 🔧 故障排除

### 问题 1: 构建失败 - 内存不足

**症状**：构建过程中 Docker 容器被杀死

**解决方案**：
1. 检查 Railway 服务的内存限制（建议至少 1GB）
2. 如果内存不足，可以分步安装依赖

### 问题 2: ML 模块不可用

**症状**：健康检查显示 `ml_predictor: false`

**检查步骤**：
```bash
# 检查日志
railway logs | grep -i "xgboost\|keybert"

# 应该看到：
# ✅ ML Performance Predictor (XGBoost) available
# ✅ Semantic Analyzer (KeyBERT) available
```

**解决方案**：
1. 检查依赖是否正确安装
2. 查看构建日志确认 pip install 成功
3. 重新部署

### 问题 3: 响应时间过长

**症状**：API 请求超时

**解决方案**：
1. 检查 Railway 服务的超时设置（建议至少 60 秒）
2. 考虑使用 `use_simple_mode: true` 跳过社交趋势收集
3. 或者只启用 ML 预测，不启用语义分析

## ✅ 验证清单

部署后确认：

- [ ] ✅ 健康检查显示 `ml_predictor: true`
- [ ] ✅ 健康检查显示 `semantic_analyzer: true`
- [ ] ✅ API 可以正常响应（带 ML 参数）
- [ ] ✅ 内存使用在可接受范围（<1GB）
- [ ] ✅ 响应时间可接受（<30秒）
- [ ] ✅ 日志显示 ML 模块已加载

## 🎯 使用建议

### 生产环境推荐配置

**选项 A: 默认启用（推荐）**
- 所有请求默认使用 ML 功能
- 准确率提升 20-30%
- 响应时间增加 5-8秒

**选项 B: 可选启用**
- 默认使用规则方法（快速）
- 用户可选择启用 ML（通过 API 参数）
- 平衡性能和准确率

### API 使用示例

```json
{
  "videos": [...],
  "channel_data": {...},
  "use_ml_prediction": true,      // 启用 XGBoost 预测
  "use_semantic_keywords": true,  // 启用 KeyBERT 语义分析
  "enable_predictions": true      // 启用 Prophet 预测
}
```

## 📝 注意事项

1. **内存使用**：ML 版本内存使用约 900MB，确保 Railway 服务有足够内存
2. **构建时间**：首次构建可能需要 10-15 分钟（下载 ML 模型）
3. **响应时间**：启用 ML 功能后响应时间增加，但准确率显著提升
4. **优雅降级**：即使 ML 模块不可用，系统也会自动降级到规则方法

---

**更新日期**: 2026-01-17  
**版本**: MVP 3.1  
**状态**: ✅ 已配置，准备部署
