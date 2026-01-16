# ✅ Railway Dashboard 配置检查清单

## 📋 当前配置状态（根据截图）

### ✅ 已正确配置

1. **Build 设置**：
   - ✅ Builder: **Nixpacks**（已设置，虽然标记为 Deprecated）
   - ✅ Custom Build Command: 已设置（`cd backend && pip install -r requirements_v2.txt && python -m spac...`）

2. **Deploy 设置**：
   - ✅ Custom Start Command: 已设置（`cd backend && python -m uvicorn app_v2:app --host 0.0.0.0 --port...`）

3. **Source 设置**：
   - ✅ Source Repo: `ejzhang101/trendforge_mvp3.1`
   - ✅ Branch: `main`

---

## 🔍 需要验证的配置

### 1. Root Directory 设置

在 **Source 设置页面**：
- 找到 "Add Root Directory" 选项
- **应该留空**（Railway 从仓库根目录开始）
- 如果设置了路径，应该清空它

**为什么重要**：
- Root Directory 影响构建命令的工作目录
- 如果设置错误，`cd backend` 可能无法找到正确的目录

### 2. Build Command 完整性

在 **Build 设置页面**，确认 Custom Build Command 是完整的：

```
cd backend && pip install -r requirements_v2.txt && python -m spacy download en_core_web_sm
```

**检查点**：
- 包含 `cd backend`
- 包含 `pip install -r requirements_v2.txt`
- 包含 `python -m spacy download en_core_web_sm`（完整命令）

### 3. Start Command 完整性

在 **Deploy 设置页面**，确认 Custom Start Command 是完整的：

```
cd backend && python -m uvicorn app_v2:app --host 0.0.0.0 --port $PORT
```

**检查点**：
- 包含 `cd backend`
- 包含 `python -m uvicorn app_v2:app`
- 包含 `--host 0.0.0.0`
- 包含 `--port $PORT`（使用环境变量，不是硬编码端口）

---

## 🚀 下一步操作

### 步骤 1: 验证 Root Directory

1. 在 Railway Dashboard → Settings → Source
2. 检查 "Add Root Directory" 部分
3. **确保留空**（不要设置任何路径）
4. 如果设置了路径，点击删除或清空

### 步骤 2: 验证命令完整性

1. **Build 设置**：
   - 点击 Custom Build Command 输入框
   - 确认命令完整：`cd backend && pip install -r requirements_v2.txt && python -m spacy download en_core_web_sm`
   - 如果被截断，补充完整

2. **Deploy 设置**：
   - 点击 Custom Start Command 输入框
   - 确认命令完整：`cd backend && python -m uvicorn app_v2:app --host 0.0.0.0 --port $PORT`
   - 如果被截断，补充完整

### 步骤 3: 保存并触发新部署

1. 保存所有设置更改
2. 点击 "Deployments" 标签页
3. 点击 "Deploy" 或 "Redeploy"
4. 查看构建日志

### 步骤 4: 验证构建成功

在构建日志中应该看到：
- ✅ "Using NIXPACKS builder"
- ✅ "Detected Python project"
- ✅ 执行 Build Command
- ✅ 安装依赖成功
- ✅ 下载 spaCy 模型成功
- ✅ 执行 Start Command
- ✅ 应用启动成功

不应看到：
- ❌ "Docker build"
- ❌ "Dockerfile:20"
- ❌ "pip: command not found"

---

## 🐛 如果仍然使用 Docker

如果配置都正确但仍然使用 Docker：

1. **清除缓存**：
   - 删除当前部署
   - 触发全新部署

2. **重新创建服务**：
   - 删除当前后端服务
   - 重新创建服务
   - 在创建时明确选择 Nixpacks

3. **检查环境变量**：
   - 确保没有 `RAILWAY_BUILDER=Docker` 这样的环境变量

---

## 📝 完整配置参考

### Build Command（完整）
```
cd backend && pip install -r requirements_v2.txt && python -m spacy download en_core_web_sm
```

### Start Command（完整）
```
cd backend && python -m uvicorn app_v2:app --host 0.0.0.0 --port $PORT
```

### Root Directory
- **留空**（不设置任何路径）

---

**最后更新**: 2026-01-16  
**状态**: 配置已基本完成，需要验证完整性
