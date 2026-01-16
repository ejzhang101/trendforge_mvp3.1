# GitHub 推送指南

## 🔐 认证方式

GitHub 已不再支持密码认证，需要使用以下方式之一：

---

## 方法 1: Personal Access Token (推荐，简单快速)

### 步骤

1. **创建 Personal Access Token**
   - 访问：https://github.com/settings/tokens
   - 点击 "Generate new token (classic)"
   - 填写 Token 名称（如：`TrendForge MVP 3.1`）
   - 选择过期时间（建议选择较长时间或不过期）
   - **重要**：勾选 `repo` 权限（完整仓库访问权限）
   - 点击 "Generate token"
   - **立即复制 token**（只显示一次）

2. **使用 Token 推送**
   ```bash
   # 推送时会提示输入用户名和密码
   # 用户名：你的 GitHub 用户名
   # 密码：使用刚才生成的 Personal Access Token（不是 GitHub 密码）
   git push -u origin main
   ```

3. **或者直接在 URL 中包含 token**（不推荐，但方便）
   ```bash
   # 格式：https://token@github.com/用户名/仓库名.git
   git remote set-url origin https://你的token@github.com/ejzhang101/trendforge_mvp3.1.git
   git push -u origin main
   ```

---

## 方法 2: SSH 密钥（更安全，推荐长期使用）

### 步骤

1. **检查是否已有 SSH 密钥**
   ```bash
   ls -la ~/.ssh/id_*.pub
   ```

2. **如果没有，生成新的 SSH 密钥**
   ```bash
   ssh-keygen -t ed25519 -C "your_email@example.com"
   # 按 Enter 使用默认路径
   # 可以设置密码（可选，更安全）
   ```

3. **复制公钥**
   ```bash
   cat ~/.ssh/id_ed25519.pub
   # 复制输出的内容
   ```

4. **添加到 GitHub**
   - 访问：https://github.com/settings/keys
   - 点击 "New SSH key"
   - Title: 填写描述（如：`MacBook Pro`）
   - Key: 粘贴刚才复制的公钥
   - 点击 "Add SSH key"

5. **测试 SSH 连接**
   ```bash
   ssh -T git@github.com
   # 应该看到: Hi ejzhang101! You've successfully authenticated...
   ```

6. **更改远程 URL 为 SSH**
   ```bash
   git remote set-url origin git@github.com:ejzhang101/trendforge_mvp3.1.git
   ```

7. **推送代码**
   ```bash
   git push -u origin main
   git push origin --tags
   ```

---

## 🚀 快速推送命令

### 使用 Personal Access Token

```bash
# 方法 A: 交互式输入（推荐）
git push -u origin main
# 用户名：ejzhang101
# 密码：你的 Personal Access Token

# 方法 B: 在 URL 中包含 token
git remote set-url origin https://你的token@github.com/ejzhang101/trendforge_mvp3.1.git
git push -u origin main
```

### 使用 SSH

```bash
# 1. 更改远程 URL
git remote set-url origin git@github.com:ejzhang101/trendforge_mvp3.1.git

# 2. 推送
git push -u origin main
git push origin --tags
```

---

## ✅ 验证推送

推送成功后，访问：
https://github.com/ejzhang101/trendforge_mvp3.1

确认：
- [ ] 所有文件已上传
- [ ] 提交历史完整
- [ ] 标签已推送（v2.0.1, v3.0.0, v3.1.0）

---

## 🔍 当前状态

- **远程仓库**: ✅ 已配置
  - URL: https://github.com/ejzhang101/trendforge_mvp3.1.git
- **本地分支**: main
- **待推送**: 所有本地提交和标签

---

## 💡 推荐

对于长期使用，**推荐使用 SSH 方式**：
- 更安全
- 不需要每次输入 token
- 一次配置，长期使用

对于快速推送，可以使用 **Personal Access Token**。
