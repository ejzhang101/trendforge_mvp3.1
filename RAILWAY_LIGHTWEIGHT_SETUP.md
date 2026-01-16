# 🪶 Railway 轻量级部署配置

## 📋 概述

为了优化 Railway 部署的内存使用，创建了轻量级依赖版本 `requirements_railway.txt`。

### 内存优化

**移除的大型依赖**（节省 ~750MB）：
- ❌ spaCy (200MB)
- ❌ KeyBERT (150MB)
- ❌ scikit-learn (100MB)
- ❌ sentence-transformers (300MB)
- ❌ youtube-transcript-api（字幕分析暂时禁用）

**保留的核心功能**：
- ✅ FastAPI + Uvicorn
- ✅ NLTK（轻量级 NLP）
- ✅ 社交媒体 API（Twitter, Reddit, Google Trends）
- ✅ YouTube API
- ✅ 数据处理（NumPy, Pandas）

**总内存占用**: < 400MB（相比原来 ~1.2GB）

---

## 🔧 配置文件更新

### 1. railway.json

已更新为使用 `requirements_railway.txt`：

```json
{
  "build": {
    "builder": "NIXPACKS",
    "buildCommand": "cd backend && pip install -r requirements_railway.txt && python -c \"import nltk; nltk.download('punkt'); nltk.download('stopwords'); nltk.download('averaged_perceptron_tagger')\""
  }
}
```

**变更**：
- 使用 `requirements_railway.txt` 而不是 `requirements_v2.txt`
- 移除 `python -m spacy download en_core_web_sm`
- 添加 NLTK 数据下载

### 2. nixpacks.toml

已更新构建命令：

```toml
[phases.install]
cmds = [
  "cd backend",
  "pip install -r requirements_railway.txt",
  "python -c \"import nltk; nltk.download('punkt'); nltk.download('stopwords'); nltk.download('averaged_perceptron_tagger')\""
]
```

### 3. Railway Dashboard 设置

在 Railway Dashboard → Settings → Build 中：

**Custom Build Command**:
```
cd backend && pip install -r requirements_railway.txt && python -c "import nltk; nltk.download('punkt'); nltk.download('stopwords'); nltk.download('averaged_perceptron_tagger')"
```

---

## ⚠️ 功能影响

### 受影响的功能

1. **深度 NLP 分析**：
   - ❌ 不再使用 spaCy 进行实体识别
   - ❌ 不再使用 KeyBERT 进行关键词提取
   - ✅ 使用 NLTK 进行基础文本处理

2. **字幕分析**：
   - ❌ 暂时禁用（需要 youtube-transcript-api）
   - ✅ 标题和描述分析仍然可用

3. **ML 模型**：
   - ❌ 不再使用 scikit-learn 进行 ML 预测
   - ✅ 基础统计和规则引擎仍然可用

### 仍然可用的功能

- ✅ 频道内容分析（基于 NLTK）
- ✅ 社交媒体趋势收集
- ✅ AI 推荐引擎
- ✅ Prophet 时间序列预测（如果启用）
- ✅ 脚本生成（如果配置了 OpenAI API Key）

---

## 🚀 部署步骤

### 1. 更新 Railway Dashboard 配置

在 Railway Dashboard → Settings → Build：

1. **更新 Custom Build Command**：
   ```
   cd backend && pip install -r requirements_railway.txt && python -c "import nltk; nltk.download('punkt'); nltk.download('stopwords'); nltk.download('averaged_perceptron_tagger')"
   ```

2. **保存设置**

### 2. 触发新部署

1. 点击 "Deployments" 标签页
2. 点击 "Deploy" 或 "Redeploy"
3. 查看构建日志

### 3. 验证部署

构建日志应该显示：
- ✅ 安装轻量级依赖
- ✅ 下载 NLTK 数据
- ✅ 不再尝试下载 spaCy 模型
- ✅ 构建时间更短
- ✅ 内存使用更低

---

## 🔄 回退到完整版本

如果需要恢复完整功能：

1. **更新 railway.json**：
   ```json
   "buildCommand": "cd backend && pip install -r requirements_v2.txt && python -m spacy download en_core_web_sm"
   ```

2. **更新 nixpacks.toml**：
   ```toml
   "pip install -r requirements_v2.txt",
   "python -m spacy download en_core_web_sm"
   ```

3. **更新 Railway Dashboard**：
   - Build Command: `cd backend && pip install -r requirements_v2.txt && python -m spacy download en_core_web_sm`

---

## 📊 性能对比

| 指标 | 完整版本 | 轻量级版本 |
|------|---------|-----------|
| 内存占用 | ~1.2GB | < 400MB |
| 构建时间 | ~5-8分钟 | ~2-3分钟 |
| 依赖数量 | 48个 | 18个 |
| NLP 功能 | 完整 | 基础 |
| ML 功能 | 完整 | 基础 |

---

## 🎯 推荐使用场景

### 使用轻量级版本（requirements_railway.txt）

- ✅ Railway 免费/基础计划（内存限制）
- ✅ 快速部署和测试
- ✅ 基础功能需求
- ✅ 成本优化

### 使用完整版本（requirements_v2.txt）

- ✅ 需要完整 NLP 功能
- ✅ 需要 ML 预测
- ✅ 需要字幕分析
- ✅ 有足够内存资源

---

## 📝 代码兼容性

代码应该能够处理缺失的依赖：

```python
# 示例：优雅降级
try:
    import spacy
    nlp = spacy.load('en_core_web_sm')
    USE_SPACY = True
except ImportError:
    USE_SPACY = False
    # 使用 NLTK 作为替代
    import nltk
```

确保代码中有适当的 fallback 逻辑。

---

**最后更新**: 2026-01-16  
**版本**: MVP 3.1.0 (Railway 优化版)
