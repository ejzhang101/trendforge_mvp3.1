# 🔧 Redis 手动安装指南

由于 Homebrew 安装需要交互式操作，请按照以下步骤手动安装：

## 📋 步骤 1: 安装 Homebrew

在终端中运行：

```bash
/bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"
```

**注意：** 安装过程可能需要：
- 输入管理员密码
- 按回车确认
- 等待几分钟完成安装

安装完成后，根据提示运行（通常是）：

```bash
# Intel Mac
echo 'eval "$(/usr/local/bin/brew shellenv)"' >> ~/.zshrc
eval "$(/usr/local/bin/brew shellenv)"

# Apple Silicon Mac
echo 'eval "$(/opt/homebrew/bin/brew shellenv)"' >> ~/.zshrc
eval "$(/opt/homebrew/bin/brew shellenv)"
```

## 📋 步骤 2: 安装 Redis

```bash
brew install redis
```

## 📋 步骤 3: 启动 Redis

```bash
# 启动 Redis 服务（开机自启）
brew services start redis

# 或者手动启动（不自动启动）
redis-server
```

## 📋 步骤 4: 验证 Redis

```bash
redis-cli ping
# 应该返回: PONG
```

## 📋 步骤 5: 验证配置

`.env` 文件已包含 `REDIS_URL=redis://localhost:6379`，无需额外配置。

## 📋 步骤 6: 重启后端

```bash
cd backend
source venv/bin/activate
python app_v2.py
```

## 📋 步骤 7: 验证连接

```bash
curl http://localhost:8000/health | python3 -m json.tool | grep cache
# 应该显示: "cache": true
```

---

## 🚀 快速命令（复制粘贴）

```bash
# 1. 安装 Homebrew（如果需要）
/bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"

# 2. 配置 Homebrew PATH（根据提示选择）
# Intel Mac:
echo 'eval "$(/usr/local/bin/brew shellenv)"' >> ~/.zshrc && eval "$(/usr/local/bin/brew shellenv)"
# Apple Silicon Mac:
echo 'eval "$(/opt/homebrew/bin/brew shellenv)"' >> ~/.zshrc && eval "$(/opt/homebrew/bin/brew shellenv)"

# 3. 安装 Redis
brew install redis

# 4. 启动 Redis
brew services start redis

# 5. 验证
redis-cli ping

# 6. 重启后端（在另一个终端）
cd backend
source venv/bin/activate
python app_v2.py
```

---

## ✅ 验证清单

- [ ] Homebrew 已安装 (`brew --version`)
- [ ] Redis 已安装 (`brew list redis`)
- [ ] Redis 正在运行 (`redis-cli ping` 返回 PONG)
- [ ] `.env` 文件包含 `REDIS_URL=redis://localhost:6379`
- [ ] 后端健康检查显示 `"cache": true`

---

## 🐛 故障排除

### Homebrew 安装失败

如果 Homebrew 安装需要管理员权限，请：
1. 在终端中手动运行安装命令
2. 输入管理员密码
3. 等待安装完成

### Redis 启动失败

```bash
# 检查 Redis 是否已安装
brew list redis

# 手动启动 Redis
redis-server

# 检查端口是否被占用
lsof -i :6379
```

### 后端无法连接 Redis

1. 确认 Redis 正在运行：`redis-cli ping`
2. 检查 `.env` 文件中的 `REDIS_URL`
3. 查看后端日志中的错误信息

---

**提示：** 如果不想安装 Redis，系统仍会使用内存缓存作为 Fallback，但性能提升有限。
