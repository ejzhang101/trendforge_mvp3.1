# 🎛️ Railway Dashboard 配置指南

## 📋 当前配置状态

根据你的 Railway Dashboard 截图：

### ✅ 已配置
- **Builder**: Nixpacks（已设置，虽然标记为 Deprecated）
- **Settings 页面**: 可以访问 Build 和 Deploy 设置

### ⚠️ 注意事项
- Nixpacks 被标记为 "Deprecated"（已弃用）
- Railway 推荐使用新的构建器（可能是 Railpack）

---

## 🔧 Build 设置配置

### 1. Builder 设置

**当前状态**: Nixpacks（Deprecated）

**选项**：
- **Nixpacks**（当前选择）- 虽然标记为 Deprecated，但应该可以工作
- **Railpack**（如果可用）- Railway 的新推荐构建器
- **Dockerfile** - 如果明确需要 Docker

**建议**：
- 如果 Nixpacks 可以正常工作，暂时保持
- 如果遇到问题，考虑切换到 Railpack（如果可用）

### 2. Metal Build Environment

**当前状态**: 关闭

**说明**：
- Railway 的新 Metal 构建环境
- 更快，将在未来成为默认选项

**建议**：
- 可以尝试开启，看是否能改善构建速度
- 如果开启后出现问题，可以关闭

### 3. Custom Build Command

**需要设置**：
```
cd backend && pip install -r requirements_v2.txt && python -m spacy download en_core_web_sm
```

**操作步骤**：
1. 点击 "+ Build Command" 按钮
2. 输入上面的命令
3. 保存

---

## 🚀 Deploy 设置配置

### 1. Custom Start Command

**需要设置**：
```
cd backend && python -m uvicorn app_v2:app --host 0.0.0.0 --port $PORT
```

**操作步骤**：
1. 点击 "+ Start Command" 按钮
2. 输入上面的命令
3. 保存

### 2. Regions

**当前状态**: US East (Virginia, USA) - 1 Instance

**说明**：
- 单区域部署，适合当前需求
- 多区域需要 Pro 计划

### 3. Teardown

**当前状态**: 关闭

**说明**：
- 控制旧部署的终止时机
- 当前关闭状态可以接受

---

## ✅ 配置检查清单

### Build 设置
- [x] Builder 设置为 Nixpacks（或 Railpack）
- [ ] Custom Build Command 已设置
- [ ] Metal Build Environment（可选，可尝试开启）

### Deploy 设置
- [ ] Custom Start Command 已设置
- [x] Region 已配置（US East）
- [x] Teardown 设置（当前关闭可接受）

---

## 🚀 下一步操作

### 1. 设置 Custom Build Command

在 Build 设置中：
1. 点击 "+ Build Command"
2. 输入：
   ```
   cd backend && pip install -r requirements_v2.txt && python -m spacy download en_core_web_sm
   ```
3. 保存

### 2. 设置 Custom Start Command

在 Deploy 设置中：
1. 点击 "+ Start Command"
2. 输入：
   ```
   cd backend && python -m uvicorn app_v2:app --host 0.0.0.0 --port $PORT
   ```
3. 保存

### 3. 触发新部署

1. 在 Railway Dashboard 中
2. 点击 "Deployments" 标签页
3. 点击 "Deploy" 或 "Redeploy"
4. 查看构建日志

### 4. 验证部署成功

构建日志应该显示：
- ✅ 使用 Nixpacks 构建器
- ✅ 执行 Build Command
- ✅ 安装依赖成功
- ✅ 启动应用成功

---

## 🔍 如果仍然使用 Docker

如果设置后仍然使用 Docker 构建：

1. **检查 Builder 设置**
   - 确认 Builder 下拉菜单选择的是 "Nixpacks"（不是 Docker）

2. **检查是否有 Dockerfile 检测**
   - 即使有 `.railwayignore`，Railway 可能仍会检测到 Dockerfile
   - 考虑临时重命名 `backend/Dockerfile`

3. **尝试删除并重新创建服务**
   - 在创建时明确选择 Nixpacks

---

## 📝 关于 Nixpacks Deprecated

Nixpacks 被标记为 Deprecated，但：
- 仍然可以使用
- Railway 推荐迁移到新的构建器（可能是 Railpack）
- 如果 Nixpacks 工作正常，可以继续使用
- 如果遇到问题，考虑切换到 Railpack

---

**最后更新**: 2026-01-16  
**版本**: MVP 3.1.0
