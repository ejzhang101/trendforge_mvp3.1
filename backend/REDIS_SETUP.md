# 🚀 Redis 缓存配置指南

## 📋 概述

Redis 缓存可以显著减少 API 调用，提升系统性能：
- **首次请求：** 20-30 秒（完整分析）
- **缓存命中：** 2-5 秒 ⚡（10倍提升）

## 🔧 安装 Redis

### macOS (使用 Homebrew)

```bash
# 1. 安装 Redis
brew install redis

# 2. 启动 Redis 服务（开机自启）
brew services start redis

# 3. 验证 Redis 运行
redis-cli ping
# 应该返回: PONG
```

### Ubuntu/Debian

```bash
# 1. 安装 Redis
sudo apt-get update
sudo apt-get install redis-server

# 2. 启动 Redis 服务
sudo systemctl start redis
sudo systemctl enable redis  # 开机自启

# 3. 验证 Redis 运行
redis-cli ping
# 应该返回: PONG
```

### Docker (可选)

```bash
docker run -d -p 6379:6379 --name redis redis:latest
```

## ⚙️ 配置环境变量

### 1. 编辑 `.env` 文件

在 `backend/.env` 文件中添加：

```bash
# Redis 缓存配置
REDIS_URL=redis://localhost:6379

# 如果 Redis 有密码（生产环境推荐）
# REDIS_URL=redis://:password@localhost:6379

# 如果使用远程 Redis
# REDIS_URL=redis://your-redis-host:6379
```

### 2. 验证配置

```bash
cd backend
source venv/bin/activate
python -c "import os; from dotenv import load_dotenv; load_dotenv(); print('REDIS_URL:', os.getenv('REDIS_URL'))"
```

## ✅ 验证 Redis 连接

### 方法 1: 检查后端健康状态

```bash
curl http://localhost:8000/health | python3 -m json.tool
```

应该看到：
```json
{
  "services": {
    "cache": true  // ✅ Redis 已连接
  }
}
```

### 方法 2: 测试缓存功能

```bash
# 第一次请求（会调用 API）
time curl -X POST http://localhost:8000/api/v2/full-analysis ...

# 第二次请求（从缓存读取，应该快很多）
time curl -X POST http://localhost:8000/api/v2/full-analysis ...
```

## 📊 缓存策略

### 当前缓存配置

- **TTL (Time To Live):** 3600 秒（1 小时）
- **缓存内容：**
  - Twitter 趋势数据
  - Reddit 趋势数据
  - Google Trends 数据
  - 频道分析结果（通过数据库）

### 缓存键格式

```
twitter:{keyword_hash}
reddit:{keyword_hash}
google_trends:{keyword_hash}
```

## 🔍 监控缓存使用

### 查看 Redis 统计

```bash
redis-cli info stats
```

### 查看缓存键数量

```bash
redis-cli DBSIZE
```

### 查看所有缓存键

```bash
redis-cli KEYS "*"
```

### 清除缓存（如果需要）

```bash
# 清除所有缓存
redis-cli FLUSHDB

# 清除特定前缀的缓存
redis-cli --scan --pattern "twitter:*" | xargs redis-cli DEL
```

## 🎯 性能优化建议

### 1. 调整缓存 TTL

在 `backend/services/enhanced_social_collector.py` 中：

```python
# 默认 1 小时
cache_manager = CacheManager(redis_url=redis_url, ttl=3600)

# 可以调整为：
# - 30 分钟: ttl=1800
# - 2 小时: ttl=7200
# - 24 小时: ttl=86400
```

### 2. 增加内存缓存

系统已有本地内存缓存作为 fallback，即使 Redis 不可用也能工作。

### 3. 数据库缓存

前端已实现数据库缓存（当天缓存），避免重复调用 YouTube API。

## 🐛 故障排除

### Redis 连接失败

**症状：** 健康检查显示 `"cache": false`

**解决方案：**
1. 检查 Redis 是否运行：`redis-cli ping`
2. 检查端口是否正确：`lsof -i :6379`
3. 检查 `.env` 文件中的 `REDIS_URL`
4. 检查防火墙设置

### 缓存未生效

**症状：** 每次请求都很慢

**解决方案：**
1. 检查 Redis 连接状态
2. 查看后端日志，确认缓存是否被使用
3. 检查缓存键是否正确生成
4. 验证 TTL 设置

### 内存不足

**症状：** Redis 报错或性能下降

**解决方案：**
```bash
# 查看 Redis 内存使用
redis-cli info memory

# 设置最大内存（在 redis.conf 中）
maxmemory 256mb
maxmemory-policy allkeys-lru
```

## 📈 预期效果

| 场景 | 无缓存 | 有 Redis 缓存 |
|------|--------|--------------|
| 首次分析 | 20-30 秒 | 20-30 秒 |
| 重复分析（1小时内） | 20-30 秒 | 2-5 秒 ⚡ |
| API 调用次数 | 每次完整调用 | 首次调用，之后从缓存 |

## 🚀 快速开始

```bash
# 1. 安装 Redis
brew install redis
brew services start redis

# 2. 配置环境变量
echo "REDIS_URL=redis://localhost:6379" >> backend/.env

# 3. 重启后端
cd backend
source venv/bin/activate
python app_v2.py

# 4. 验证
curl http://localhost:8000/health | grep cache
```

---

**最后更新：** 2026-01-13
