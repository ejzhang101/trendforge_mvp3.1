# 📊 缓存机制总结

## ✅ 已实现的缓存

### 1. 数据库缓存（前端）
- **位置：** `frontend/app/api/analyze/route.ts`
- **策略：** 当天缓存（00:00 - 23:59）
- **缓存内容：** 完整分析结果（频道数据、推荐、回测）
- **效果：** 同一天内重复搜索同一频道，<1 秒响应
- **状态：** ✅ 已启用

### 2. Redis 缓存（后端）
- **位置：** `backend/services/enhanced_social_collector.py`
- **策略：** 1 小时 TTL
- **缓存内容：** Twitter、Reddit、Google Trends 数据
- **效果：** 1 小时内重复查询相同关键词，从缓存读取
- **状态：** ⚠️ 需要安装 Redis

### 3. 内存缓存（Fallback）
- **位置：** `backend/services/enhanced_social_collector.py` (CacheManager)
- **策略：** 1 小时 TTL（本地内存）
- **效果：** Redis 不可用时的备用方案
- **状态：** ✅ 自动启用

---

## 🚀 快速启用 Redis

### 方法 1: 使用自动配置脚本（推荐）

```bash
cd backend
./setup-redis.sh
```

### 方法 2: 手动安装

```bash
# 1. 安装 Homebrew（如果未安装）
/bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"

# 2. 安装 Redis
brew install redis

# 3. 启动 Redis
brew services start redis

# 4. 配置 .env
echo "REDIS_URL=redis://localhost:6379" >> backend/.env

# 5. 重启后端
cd backend
source venv/bin/activate
python app_v2.py
```

---

## 📈 性能提升

| 优化措施 | API 调用减少 | 响应时间提升 |
|---------|------------|------------|
| **数据库缓存** | YouTube API: 100% (当天) | 20-30秒 → <1秒 |
| **+ Redis 缓存** | 社交媒体 API: 90% (1小时) | 社交媒体收集: 10-15秒 → <1秒 |
| **组合使用** | 总体减少: 80-90% | 总体提升: 10-20倍 |

---

## 🔍 验证缓存工作

### 检查数据库缓存

```bash
# 第一次搜索频道（会调用 API）
time curl -X POST http://localhost:3000/api/analyze ...

# 第二次搜索同一频道（应该 <1 秒）
time curl -X POST http://localhost:3000/api/analyze ...
```

### 检查 Redis 缓存

```bash
# 检查后端健康状态
curl http://localhost:8000/health | python3 -m json.tool | grep cache
# 应该显示: "cache": true

# 查看 Redis 统计
redis-cli info stats
```

---

## 💡 最佳实践

1. **生产环境：** 必须启用 Redis 缓存
2. **开发环境：** 可选，但强烈推荐
3. **缓存策略：**
   - 频道数据：24 小时（变化较慢）
   - 社交媒体趋势：1-2 小时（变化较快）
   - 推荐结果：24 小时（基于频道分析）

---

**最后更新：** 2026-01-13
