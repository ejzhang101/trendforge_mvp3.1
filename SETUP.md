# TrendForge 项目设置说明

## ✅ 已完成的设置

### 后端
- ✅ Python 虚拟环境已创建 (`backend/venv`)
- ✅ 后端依赖已安装 (`requirements_v2.txt`)
- ✅ Spacy 模型已下载 (`en_core_web_sm`)

### 前端
- ✅ Node.js v24.12.0 已安装 (通过 nvm)
- ✅ pnpm v10.28.0 已安装
- ✅ 前端依赖已安装
- ✅ Prisma schema 已创建

## 📝 下一步操作

### 1. 设置数据库连接

在 `frontend` 目录下创建 `.env` 文件：

```bash
cd frontend
cat > .env << EOF
DATABASE_URL="postgresql://user:password@localhost:5432/trendforge?schema=public"
EOF
```

请根据你的实际数据库配置修改连接字符串。

### 2. 运行 Prisma 数据库推送

```bash
cd frontend
export NVM_DIR="$HOME/.nvm" && [ -s "$NVM_DIR/nvm.sh" ] && \. "$NVM_DIR/nvm.sh"
pnpm prisma db push
```

### 3. 激活后端虚拟环境

```bash
cd backend
source venv/bin/activate  # macOS/Linux
# 或
venv\Scripts\activate  # Windows
```

## 🚀 启动项目

### 后端
```bash
cd backend
source venv/bin/activate
# 启动你的 FastAPI 应用
```

### 前端
```bash
cd frontend
export NVM_DIR="$HOME/.nvm" && [ -s "$NVM_DIR/nvm.sh" ] && \. "$NVM_DIR/nvm.sh"
pnpm dev
```

## 📦 项目文件结构

```
TrendForge/
├── backend/
│   ├── venv/              # Python 虚拟环境
│   └── requirements_v2.txt # Python 依赖
├── frontend/
│   ├── node_modules/      # Node.js 依赖
│   ├── prisma/
│   │   └── schema.prisma  # Prisma 数据库 schema
│   └── package.json       # 前端依赖配置
└── install_node.sh        # Node.js 安装脚本（已执行）
```

## ⚠️ 注意事项

- 每次打开新终端时，如果使用 nvm，需要运行：
  ```bash
  export NVM_DIR="$HOME/.nvm" && [ -s "$NVM_DIR/nvm.sh" ] && \. "$NVM_DIR/nvm.sh"
  ```
  或者将上述命令添加到你的 `~/.zshrc` 文件中。

- 后端虚拟环境需要在每次使用前激活。
