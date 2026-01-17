# 🚀 ML 功能部署 - 下一步操作指南

## 📋 当前状态

✅ **已完成**：
- ML 依赖已添加到 `requirements_v2.txt`
- Dockerfile 已更新
- 本地测试通过
- 代码已推送到 GitHub
- Railway 应该正在自动部署

---

## 🎯 第一步：检查 Railway 部署状态

### 1. 访问 Railway Dashboard

1. **打开 Railway Dashboard**
   - 访问：https://railway.app
   - 登录你的账户

2. **找到你的后端服务**
   - 进入你的项目
   - 找到后端服务（通常是 "Backend" 或类似名称）

### 2. 检查构建日志

1. **查看 Deployments**
   - 点击服务名称
   - 切换到 "Deployments" 标签
   - 查看最新的部署状态

2. **检查构建日志**
   - 点击最新的部署
   - 查看构建日志，确认：
     - ✅ `pip install` 成功安装所有依赖
     - ✅ ML 库（xgboost, keybert, scikit-learn, sentence-transformers）已安装
     - ✅ Docker 镜像构建成功
     - ✅ 服务启动成功

3. **检查服务状态**
   - 状态应该显示为 "Active"（绿色）
   - 如果有错误，查看日志并修复

**⏱️ 预计构建时间**: 5-10 分钟（首次可能更长）

---

## 🧪 第二步：验证部署成功

### 方法 1: 使用健康检查 API

```bash
# 替换为你的 Railway URL
RAILWAY_URL="https://your-service-name.up.railway.app"

# 检查健康状态
curl $RAILWAY_URL/health | jq '.services.ml_predictor'
curl $RAILWAY_URL/health | jq '.services.semantic_analyzer'
```

**预期输出**：
```json
true
true
```

### 方法 2: 使用测试脚本

```bash
# 设置 Railway URL
export BACKEND_URL="https://your-service-name.up.railway.app"

# 运行测试脚本
./test_ml_features.sh
```

### 方法 3: 检查完整健康状态

```bash
curl $RAILWAY_URL/health | jq '.'
```

**应该看到**：
```json
{
  "status": "healthy",
  "version": "3.1.0",
  "services": {
    "ml_predictor": true,
    "semantic_analyzer": true,
    ...
  },
  "capabilities": {
    "ml_prediction": true,
    "semantic_analysis": true,
    ...
  }
}
```

---

## 🎯 第三步：测试 ML 功能

### 测试 1: 基础分析（不使用 ML）

```bash
curl -X POST $RAILWAY_URL/api/v2/full-analysis \
  -H "Content-Type: application/json" \
  -d '{
    "videos": [{"videoId": "test", "title": "AI Tutorial", "viewCount": 1000, "publishedAt": "2024-01-01"}],
    "channel_data": {"subscriberCount": 10000},
    "use_ml_prediction": false,
    "use_semantic_keywords": false
  }' | jq '.recommendations[0].predicted_performance.method'
```

**预期输出**：`"rule_based"`

### 测试 2: 启用 ML 预测

```bash
curl -X POST $RAILWAY_URL/api/v2/full-analysis \
  -H "Content-Type: application/json" \
  -d '{
    "videos": [{"videoId": "test", "title": "AI Tutorial", "viewCount": 1000, "publishedAt": "2024-01-01"}],
    "channel_data": {"subscriberCount": 10000},
    "use_ml_prediction": true,
    "use_semantic_keywords": false
  }' | jq '.recommendations[0].predicted_performance.method'
```

**预期输出**：`"xgboost_ml"` 或 `"rule_based"`（如果模型未训练）

### 测试 3: 启用语义分析

```bash
curl -X POST $RAILWAY_URL/api/v2/full-analysis \
  -H "Content-Type: application/json" \
  -d '{
    "videos": [{"videoId": "test", "title": "AI Tutorial", "viewCount": 1000, "publishedAt": "2024-01-01"}],
    "channel_data": {"subscriberCount": 10000},
    "use_ml_prediction": false,
    "use_semantic_keywords": true
  }' | jq '.recommendations[0].predicted_performance'
```

### 测试 4: 同时启用两者

```bash
curl -X POST $RAILWAY_URL/api/v2/full-analysis \
  -H "Content-Type: application/json" \
  -d '{
    "videos": [{"videoId": "test", "title": "AI Tutorial", "viewCount": 1000, "publishedAt": "2024-01-01"}],
    "channel_data": {"subscriberCount": 10000},
    "use_ml_prediction": true,
    "use_semantic_keywords": true
  }' | jq '.recommendations[0]'
```

---

## 🔧 第四步：故障排除

### 问题 1: 构建失败

**症状**：Railway 构建失败，日志显示错误

**检查**：
1. 查看构建日志中的错误信息
2. 常见问题：
   - 内存不足：增加 Railway 服务内存限制
   - 依赖冲突：检查 `requirements_v2.txt`
   - Docker 构建错误：检查 Dockerfile

**解决方案**：
```bash
# 检查依赖文件
cat backend/requirements_v2.txt | grep -E "xgboost|keybert"

# 应该看到：
# xgboost>=2.0.3
# keybert>=0.8.3
```

### 问题 2: ML 模块不可用

**症状**：健康检查显示 `ml_predictor: false`

**检查**：
```bash
# 查看服务日志
railway logs --service your-service-name | grep -i "xgboost\|keybert"
```

**应该看到**：
```
✅ ML Performance Predictor (XGBoost) available
✅ Semantic Analyzer (KeyBERT) available
```

**解决方案**：
1. 检查构建日志确认依赖已安装
2. 重新部署服务
3. 检查内存使用（可能需要更多内存）

### 问题 3: 响应时间过长

**症状**：API 请求超时

**解决方案**：
1. 检查 Railway 服务的超时设置（建议至少 60 秒）
2. 考虑使用 `use_simple_mode: true` 跳过社交趋势收集
3. 或者只启用 ML 预测，不启用语义分析

### 问题 4: 内存不足

**症状**：服务崩溃或重启

**解决方案**：
1. Railway Dashboard → Service Settings → Resources
2. 增加内存限制到至少 1GB
3. 如果仍然不足，考虑只启用 ML 预测或语义分析之一

---

## 📊 第五步：监控和优化

### 监控指标

1. **内存使用**
   - Railway Dashboard → Metrics
   - 预期：~800-900MB
   - 如果超过 1GB，考虑优化

2. **响应时间**
   - 基础分析：5-10秒
   - + ML 预测：+3-5秒
   - + 语义分析：+2-3秒
   - 总计：10-18秒（可接受）

3. **错误率**
   - 检查 Railway 日志
   - 监控 API 错误率

### 优化建议

1. **如果内存不足**：
   - 只启用 ML 预测（不启用语义分析）
   - 或只启用语义分析（不启用 ML 预测）

2. **如果响应时间过长**：
   - 使用 `use_simple_mode: true` 跳过社交趋势收集
   - 减少 `max_recommendations` 数量

3. **如果准确率不够**：
   - 确保同时启用 `use_ml_prediction` 和 `use_semantic_keywords`
   - 收集更多训练数据以提升 ML 模型准确率

---

## ✅ 完成检查清单

部署完成后，确认：

- [ ] ✅ Railway 构建成功
- [ ] ✅ 健康检查显示 `ml_predictor: true`
- [ ] ✅ 健康检查显示 `semantic_analyzer: true`
- [ ] ✅ API 可以正常响应
- [ ] ✅ ML 功能测试通过
- [ ] ✅ 内存使用在可接受范围（<1GB）
- [ ] ✅ 响应时间可接受（<30秒）

---

## 🎯 下一步建议

### 短期（1-2周）

1. **监控生产环境**
   - 观察内存使用
   - 监控响应时间
   - 收集用户反馈

2. **A/B 测试**
   - 对比规则方法和 ML 方法的准确率
   - 收集数据以训练更好的模型

### 中期（1个月）

1. **模型训练**
   - 收集 1000+ 真实数据
   - 训练 XGBoost 模型
   - 部署生产模型

2. **性能优化**
   - 优化特征工程
   - 减少响应时间
   - 优化内存使用

### 长期（3个月+）

1. **持续改进**
   - 定期重新训练模型
   - 优化算法参数
   - 添加新特征

---

## 📞 需要帮助？

如果遇到问题：

1. **查看日志**：
   ```bash
   railway logs --service your-service-name
   ```

2. **检查健康状态**：
   ```bash
   curl $RAILWAY_URL/health | jq '.'
   ```

3. **运行测试脚本**：
   ```bash
   ./test_ml_features.sh
   ```

4. **查看部署文档**：
   - `DEPLOY_ML_ENABLED_MVP3.1.md`

---

**更新日期**: 2026-01-17  
**版本**: MVP 3.1  
**状态**: ✅ 等待 Railway 部署完成
