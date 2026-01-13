# ⚡ 快速启用缓存 - 减少 API 调用

## 🎯 目标

减少 API 调用，提升系统性能：
- **首次分析：** 20-30 秒
- **缓存命中：** 2-5 秒 ⚡
- **API 调用减少：** 80-90%

---

## 🚀 一键配置 Redis（推荐）

```bash
cd backend
./setup-redis.sh
```

这个脚本会：
1. ✅ 检查并安装 Homebrew（如果需要）
2. ✅ 安装 Redis
3. ✅ 启动 Redis 服务
4. ✅ 配置 `.env` 文件
5. ✅ 验证 Redis 运行

---

## 📋 手动配置步骤

### 1. 安装 Homebrew（如果未安装）

```bash
/bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"
```

### 2. 安装 Redis

```bash
brew install redis
```

### 3. 启动 Redis

```bash
brew services start redis
```

### 4. 验证 Redis

```bash
redis-cli ping
# 应该返回: PONG
```

### 5. 配置环境变量

`.env` 文件已自动配置，包含：
```bash
REDIS_URL=redis://localhost:6379
```

### 6. 重启后端

```bash
cd backend
source venv/bin/activate
python app_v2.py
```

### 7. 验证连接

```bash
curl http://localhost:8000/health | python3 -m json.tool | grep cache
# 应该显示: "cache": true
```

---

## ✅ 当前缓存状态

### 已启用 ✅
1. **数据库缓存** - 当天缓存，避免重复调用 YouTube API
2. **内存缓存** - 后端 Fallback，1 小时 TTL

### 需要配置 ⚠️
3. **Redis 缓存** - 社交媒体趋势缓存，1 小时 TTL

---

## 📊 缓存效果

| 场景 | 无缓存 | 数据库缓存 | + Redis |
|------|--------|-----------|---------|
| 首次分析 | 20-30s | 20-30s | 20-30s |
| 同一天重复 | 20-30s | <1s ⚡ | <1s ⚡ |
| 1小时内重复 | 20-30s | 20-30s | 2-5s ⚡ |
| API 调用 | 每次完整 | YouTube 跳过 | 全部跳过 |

---

## 🔍 验证缓存工作

### 测试数据库缓存

```bash
# 第一次搜索（会调用 API）
time curl -X POST http://localhost:3000/api/analyze \
  -H "Content-Type: application/json" \
  -d '{"channelIdentifier": "@yourchannel"}'

# 第二次搜索同一频道（应该 <1 秒）
time curl -X POST http://localhost:3000/api/analyze \
  -H "Content-Type: application/json" \
  -d '{"channelIdentifier": "@yourchannel"}'
```

### 测试 Redis 缓存

```bash
# 检查后端健康状态
curl http://localhost:8000/health | python3 -m json.tool

# 查看 Redis 统计
redis-cli info stats
```

---

## 📝 详细文档

- **完整配置指南：** `backend/CACHE_OPTIMIZATION.md`
- **Redis 设置指南：** `backend/REDIS_SETUP.md`
- **缓存总结：** `backend/CACHE_SUMMARY.md`

---

**快速开始：** `cd backend && ./setup-redis.sh`
