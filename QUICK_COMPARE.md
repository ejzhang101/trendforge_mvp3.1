# 快速对比指南 - Localhost vs 生产环境

## 🚀 立即执行对比

### 方法 1: 使用对比脚本（推荐）

```bash
# 1. 确保 localhost 后端运行
cd backend
source venv/bin/activate
python app_v2.py

# 2. 在另一个终端执行对比
cd /Users/ejzhang/Documents/TrendForge
./compare_localhost_production.sh https://你的-railway-后端-url.up.railway.app
```

### 方法 2: 手动对比

#### Localhost 检查

```bash
# 健康检查
curl http://localhost:8000/health | python3 -m json.tool

# 完整系统状态（如果端点可用）
curl http://localhost:8000/debug/full-status | python3 -m json.tool

# 分析器状态
curl http://localhost:8000/debug/analyzer | python3 -m json.tool
```

#### 生产环境检查

```bash
# 替换为你的实际后端 URL
PRODUCTION_URL="https://你的-railway-后端-url.up.railway.app"

# 健康检查
curl $PRODUCTION_URL/health | python3 -m json.tool

# 完整系统状态
curl $PRODUCTION_URL/debug/full-status | python3 -m json.tool

# 分析器状态
curl $PRODUCTION_URL/debug/analyzer | python3 -m json.tool
```

## 📋 关键对比项

### 1. 版本号
- **期望**: 都是 `3.1.0`
- **如果不一致**: 需要重新部署

### 2. 分析器类型
- **期望**: 都是 `LightweightContentAnalyzer`
- **如果不一致**: 后端代码未更新

### 3. 推荐引擎
- **期望**: 都是 `PredictiveRecommendationEngine`
- **如果不一致**: 后端代码未更新

### 4. 功能可用性
- **Prophet**: 都应该是 `true`
- **Script Generator**: 都应该是 `true`
- **YouTube API**: 检查配置状态

### 5. 环境变量
- 对比 `environment_vars` 部分
- 检查哪些 API 已配置

## 🔧 如果发现差异

### 差异 1: 版本号不一致

**症状**: Localhost 是 `3.1.0`，生产环境是 `3.0.0`

**解决**:
1. 在 Railway Dashboard 触发重新部署
2. 等待部署完成
3. 再次检查版本号

### 差异 2: 分析器类型不一致

**症状**: Localhost 是 `LightweightContentAnalyzer`，生产环境是 `EnhancedContentAnalyzer`

**解决**:
1. 确认后端代码已更新
2. 重新部署后端
3. 清除 Python 缓存（如果有）

### 差异 3: 功能不可用

**症状**: 生产环境的某些功能显示为 `false`

**解决**:
1. 检查环境变量配置
2. 检查依赖是否安装
3. 查看部署日志

## 📊 对比结果模板

```
✅ 版本号: 一致 (3.1.0)
✅ 分析器: 一致 (LightweightContentAnalyzer)
✅ Prophet: 一致 (true)
✅ Script Generator: 一致 (true)
❌ 环境变量: 不一致
   - Localhost: TWITTER_BEARER_TOKEN = true
   - 生产环境: TWITTER_BEARER_TOKEN = false
```

---

**提示**: 如果 `/debug/full-status` 返回 404，说明后端代码未更新，需要重启 localhost 后端或重新部署生产环境。
