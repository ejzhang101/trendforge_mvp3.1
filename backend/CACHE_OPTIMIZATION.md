# 🚀 缓存优化配置指南 - 减少 API 调用

## 📊 当前缓存机制

系统已实现多层缓存机制：

### 1. ✅ 数据库缓存（已启用）
- **位置：** 前端 API (`frontend/app/api/analyze/route.ts`)
- **策略：** 当天缓存（00:00 - 23:59）
- **效果：** 同一天内重复搜索同一频道，<1 秒响应
- **状态：** ✅ 已启用

### 2. ⚠️ Redis 缓存（可选，推荐）
- **位置：** 后端社交媒体收集器
- **策略：** 1 小时 TTL
- **效果：** 社交媒体趋势数据缓存，减少 Twitter/Reddit/Google Trends API 调用
- **状态：** ⚠️ 需要安装 Redis

### 3. ✅ 内存缓存（Fallback）
- **位置：** 后端 `CacheManager`
- **策略：** 1 小时 TTL（本地内存）
- **效果：** Redis 不可用时的备用方案
- **状态：** ✅ 自动启用

---

## 🔧 安装和配置 Redis

### 步骤 1: 安装 Homebrew（如果未安装）

```bash
/bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"
```

### 步骤 2: 安装 Redis

```bash
brew install redis
```

### 步骤 3: 启动 Redis 服务

```bash
# 启动 Redis（开机自启）
brew services start redis

# 或者手动启动（不自动启动）
redis-server
```

### 步骤 4: 验证 Redis 运行

```bash
redis-cli ping
# 应该返回: PONG
```

### 步骤 5: 配置环境变量

编辑 `backend/.env` 文件，添加：

```bash
# Redis 缓存配置
REDIS_URL=redis://localhost:6379
```

### 步骤 6: 重启后端服务

```bash
cd backend
source venv/bin/activate
python app_v2.py
```

### 步骤 7: 验证 Redis 连接

```bash
curl http://localhost:8000/health | python3 -m json.tool | grep cache
# 应该显示: "cache": true
```

---

## 📈 缓存效果对比

| 场景 | 无缓存 | 数据库缓存 | + Redis 缓存 |
|------|--------|-----------|-------------|
| **首次分析** | 20-30 秒 | 20-30 秒 | 20-30 秒 |
| **同一天重复** | 20-30 秒 | <1 秒 ⚡ | <1 秒 ⚡ |
| **1小时内重复** | 20-30 秒 | 20-30 秒 | 2-5 秒 ⚡ |
| **API 调用** | 每次完整调用 | YouTube API 跳过 | 社交媒体 API 也跳过 |

---

## 🎯 其他优化建议

### 1. 延长数据库缓存时间

当前：当天缓存（24 小时）

可以调整为：
- **3 天缓存：** 适合不常更新的频道
- **7 天缓存：** 适合稳定频道
- **1 小时缓存：** 适合频繁更新的频道

**修改位置：** `frontend/app/api/analyze/route.ts`

```typescript
// 当前：当天缓存
const today = new Date();
today.setHours(0, 0, 0, 0);

// 改为 3 天缓存
const cacheDate = new Date();
cacheDate.setDate(cacheDate.getDate() - 3);
cacheDate.setHours(0, 0, 0, 0);

if (lastAnalyzed.getTime() >= cacheDate.getTime()) {
  // 使用缓存
}
```

### 2. 优化 Redis TTL

**当前：** 1 小时（3600 秒）

**建议：**
- **社交媒体趋势：** 1-2 小时（变化较快）
- **频道分析：** 24 小时（变化较慢）

**修改位置：** `backend/services/enhanced_social_collector.py`

```python
# 社交媒体缓存：1 小时
cache_manager = CacheManager(redis_url=redis_url, ttl=3600)

# 频道分析缓存：24 小时
channel_cache = CacheManager(redis_url=redis_url, ttl=86400)
```

### 3. 批量请求优化

对于多个关键词的社交媒体收集，可以：
- 合并相似关键词
- 使用批量 API（如果支持）
- 减少重复查询

### 4. API 配额管理

**YouTube API：**
- 每日配额：10,000 单位
- 每次搜索：100 单位
- 每次频道查询：1 单位
- **建议：** 使用数据库缓存，避免重复调用

**Twitter API：**
- 速率限制：15 请求/15 分钟
- **建议：** 使用 Redis 缓存，1 小时 TTL

**Reddit API：**
- 速率限制：60 请求/分钟
- **建议：** 使用 Redis 缓存，1 小时 TTL

---

## 🔍 监控和调试

### 查看缓存命中率

```bash
# Redis 统计
redis-cli info stats | grep keyspace

# 查看缓存键数量
redis-cli DBSIZE
```

### 查看缓存内容

```bash
# 查看所有缓存键
redis-cli KEYS "*"

# 查看特定缓存
redis-cli GET "twitter:abc123"
```

### 清除缓存

```bash
# 清除所有缓存
redis-cli FLUSHDB

# 清除特定前缀
redis-cli --scan --pattern "twitter:*" | xargs redis-cli DEL
```

---

## 🚀 快速配置脚本

创建 `backend/setup-redis.sh`：

```bash
#!/bin/bash

echo "🚀 配置 Redis 缓存..."

# 检查 Homebrew
if ! command -v brew &> /dev/null; then
    echo "📦 安装 Homebrew..."
    /bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"
fi

# 安装 Redis
if ! command -v redis-cli &> /dev/null; then
    echo "📦 安装 Redis..."
    brew install redis
fi

# 启动 Redis
echo "🔄 启动 Redis 服务..."
brew services start redis

# 等待 Redis 启动
sleep 2

# 验证 Redis
if redis-cli ping | grep -q "PONG"; then
    echo "✅ Redis 运行正常"
else
    echo "❌ Redis 启动失败"
    exit 1
fi

# 配置 .env
if [ -f .env ]; then
    if ! grep -q "REDIS_URL" .env; then
        echo "📝 添加 REDIS_URL 到 .env..."
        echo "" >> .env
        echo "# Redis 缓存配置" >> .env
        echo "REDIS_URL=redis://localhost:6379" >> .env
        echo "✅ .env 已更新"
    else
        echo "ℹ️ REDIS_URL 已存在于 .env"
    fi
else
    echo "📝 创建 .env 文件..."
    echo "REDIS_URL=redis://localhost:6379" > .env
    echo "✅ .env 已创建"
fi

echo ""
echo "🎉 Redis 配置完成！"
echo ""
echo "下一步："
echo "  1. 重启后端服务: python app_v2.py"
echo "  2. 验证连接: curl http://localhost:8000/health | grep cache"
```

---

## 📝 配置检查清单

- [ ] Homebrew 已安装
- [ ] Redis 已安装
- [ ] Redis 服务正在运行
- [ ] `.env` 文件包含 `REDIS_URL`
- [ ] 后端健康检查显示 `"cache": true`
- [ ] 测试缓存功能（第二次请求应该更快）

---

## 🐛 故障排除

### Redis 连接失败

**检查：**
1. Redis 是否运行：`redis-cli ping`
2. 端口是否正确：`lsof -i :6379`
3. `.env` 文件中的 `REDIS_URL`
4. 后端日志中的错误信息

### 缓存未生效

**检查：**
1. 后端日志中是否有 "✅ Redis cache connected"
2. 健康检查中 `cache` 是否为 `true`
3. 缓存键是否正确生成
4. TTL 设置是否合理

---

**最后更新：** 2026-01-13
