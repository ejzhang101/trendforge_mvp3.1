# Git 仓库设置指南

## 📦 当前状态

Git 仓库已初始化，所有代码和文档已提交。

### 版本信息

- **版本**: v2.0.1-quickfix
- **标签**: v2.0.1
- **提交**: 已完成初始提交

---

## 🚀 推送到远程仓库

### 1. 添加远程仓库

```bash
# GitHub
git remote add origin https://github.com/your-username/TrendForge.git

# 或 GitLab
git remote add origin https://gitlab.com/your-username/TrendForge.git

# 或 Bitbucket
git remote add origin https://bitbucket.org/your-username/TrendForge.git
```

### 2. 推送代码和标签

```bash
# 推送主分支
git push -u origin main

# 推送所有标签
git push origin --tags
```

### 3. 验证

```bash
# 检查远程仓库
git remote -v

# 查看提交历史
git log --oneline --graph

# 查看标签
git tag -l
```

---

## 📝 提交规范

### 提交信息格式

```
<type>: <subject>

<body>

<footer>
```

### 类型 (type)

- `feat`: 新功能
- `fix`: 修复 bug
- `docs`: 文档更新
- `style`: 代码格式（不影响功能）
- `refactor`: 重构
- `perf`: 性能优化
- `test`: 测试相关
- `chore`: 构建/工具相关

### 示例

```bash
git commit -m "feat: Add SerpAPI integration for social trends"
git commit -m "fix: Resolve async issues in backtest analyzer"
git commit -m "docs: Update architecture documentation"
```

---

## 🏷️ 版本标签

### 创建标签

```bash
# 轻量标签
git tag v2.0.1

# 附注标签（推荐）
git tag -a v2.0.1 -m "Version 2.0.1 description"
```

### 查看标签

```bash
git tag -l
git tag -l "v2.*"
git show v2.0.1
```

### 删除标签

```bash
# 本地删除
git tag -d v2.0.1

# 远程删除
git push origin --delete v2.0.1
```

---

## 🔄 分支策略

### 主分支

- `main` - 生产环境代码
- `develop` - 开发分支（可选）

### 功能分支

```bash
# 创建功能分支
git checkout -b feature/serpapi-integration

# 提交更改
git add .
git commit -m "feat: Add SerpAPI collector"

# 合并到主分支
git checkout main
git merge feature/serpapi-integration
```

---

## 📋 当前提交内容

### 主要文件

- `backend/app_v2.py` - FastAPI 主应用
- `backend/services/enhanced_social_collector.py` - SerpAPI 集成
- `backend/services/backtest_analyzer.py` - 回测优化
- `frontend/app/analysis/[channelId]/page.tsx` - 前端错误修复
- `VERSION_2.0.1_SERPAPI.md` - 版本文档
- `ARCHITECTURE_V2.0.1.md` - 架构文档
- `CHANGELOG.md` - 变更日志
- `README.md` - 项目说明

### 配置文件

- `vercel.json` - Vercel 部署配置
- `railway.json` - Railway 部署配置
- `docker-compose.yml` - Docker 配置
- `.gitignore` - Git 忽略文件

---

## 🔍 查看提交历史

```bash
# 简洁格式
git log --oneline

# 详细格式
git log

# 图形化显示
git log --oneline --graph --all

# 查看特定文件的变更
git log --follow -- <file>
```

---

## 📦 导出版本

### 创建归档

```bash
# 创建 tar 归档
git archive --format=tar --prefix=TrendForge-v2.0.1/ v2.0.1 | gzip > TrendForge-v2.0.1.tar.gz

# 创建 zip 归档
git archive --format=zip --prefix=TrendForge-v2.0.1/ v2.0.1 > TrendForge-v2.0.1.zip
```

---

## ✅ 检查清单

- [x] Git 仓库已初始化
- [x] .gitignore 已配置
- [x] 所有代码已提交
- [x] 版本文档已创建
- [x] 版本标签已创建
- [ ] 远程仓库已添加（待完成）
- [ ] 代码已推送到远程（待完成）

---

**最后更新**: 2026-01-13
