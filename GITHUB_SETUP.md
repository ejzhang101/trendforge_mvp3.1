# GitHub 仓库配置指南

## 📋 当前状态

代码已提交到本地 Git，但尚未配置 GitHub 远程仓库。

---

## 🚀 配置 GitHub 远程仓库

### 方法 1: 连接到现有 GitHub 仓库

如果你已经有一个 GitHub 仓库：

```bash
# 添加远程仓库
git remote add origin https://github.com/你的用户名/你的仓库名.git

# 验证远程仓库
git remote -v

# 推送代码
git push -u origin main

# 推送标签
git push origin --tags
```

### 方法 2: 创建新的 GitHub 仓库

1. **在 GitHub 上创建新仓库**
   - 访问 https://github.com/new
   - 填写仓库名称（例如：`TrendForge`）
   - 选择 Public 或 Private
   - **不要**初始化 README、.gitignore 或 license（因为本地已有）

2. **连接并推送**
   ```bash
   # 添加远程仓库（替换为你的实际 URL）
   git remote add origin https://github.com/你的用户名/TrendForge.git
   
   # 推送代码
   git push -u origin main
   
   # 推送所有标签
   git push origin --tags
   ```

### 方法 3: 使用 SSH（推荐）

如果你配置了 SSH 密钥：

```bash
# 添加 SSH 远程仓库
git remote add origin git@github.com:你的用户名/你的仓库名.git

# 推送代码
git push -u origin main
```

---

## 📦 推送当前代码

配置好远程仓库后，执行：

```bash
# 推送主分支
git push -u origin main

# 推送所有标签（包括 v3.1.0）
git push origin --tags
```

---

## ✅ 验证推送

推送完成后，访问你的 GitHub 仓库，确认：
- [ ] 所有文件已上传
- [ ] 提交历史完整
- [ ] 标签已推送（v2.0.1, v3.0.0, v3.1.0）

---

## 🔐 认证问题

如果遇到认证问题：

### HTTPS 方式
```bash
# GitHub 已不再支持密码认证，需要使用 Personal Access Token
# 1. 访问 https://github.com/settings/tokens
# 2. 创建新的 token（选择 repo 权限）
# 3. 使用 token 作为密码
```

### SSH 方式
```bash
# 生成 SSH 密钥（如果还没有）
ssh-keygen -t ed25519 -C "your_email@example.com"

# 将公钥添加到 GitHub
# 1. 复制 ~/.ssh/id_ed25519.pub
# 2. 访问 https://github.com/settings/keys
# 3. 添加新的 SSH key
```

---

## 📝 当前提交状态

```bash
# 查看最新提交
git log --oneline -5

# 查看所有标签
git tag -l

# 查看未推送的提交
git log origin/main..main 2>/dev/null || echo "未配置远程仓库"
```

---

**注意**：如果仓库是私有的，确保你有推送权限。
