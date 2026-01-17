# 清除数据库缓存详细教程

**目标**: 清除 Railway PostgreSQL 数据库中的旧分析数据，强制系统重新生成正确格式的数据。

## 📋 前置条件

1. 已登录 Railway 账户
2. 有数据库访问权限
3. 知道数据库服务名称

## 🚀 方法一：使用 Railway Dashboard（推荐）

### 步骤 1: 登录 Railway

1. 打开浏览器，访问 [Railway Dashboard](https://railway.app)
2. 使用您的账户登录

### 步骤 2: 找到 PostgreSQL 服务

1. 在 Dashboard 中，找到您的项目（TrendForge）
2. 在项目列表中，找到 **PostgreSQL** 服务
   - 通常显示为 "Postgres" 或 "PostgreSQL"
   - 图标是 🐘 大象图标

### 步骤 3: 打开数据库查询界面

1. 点击 PostgreSQL 服务卡片
2. 在服务详情页面，找到 **"Data"** 或 **"Query"** 标签
3. 点击进入数据库查询界面

**如果找不到 Query 界面**：
- 查找 **"Connect"** 或 **"Settings"** 标签
- 找到 **"Postgres URL"** 或 **"Connection String"**
- 复制连接字符串（稍后在方法二中使用）

### 步骤 4: 执行清除命令

在查询界面中，粘贴以下 SQL 命令：

```sql
-- 步骤 1: 查看当前数据（可选，用于确认）
SELECT COUNT(*) as channel_count FROM "Channel";
SELECT COUNT(*) as trend_count FROM "ChannelTrend";

-- 步骤 2: 删除所有分析记录
-- ⚠️ 警告：这将删除所有已分析的数据
DELETE FROM "ChannelTrend";
DELETE FROM "Channel";

-- 步骤 3: 验证删除结果（可选）
SELECT COUNT(*) as remaining_channels FROM "Channel";
SELECT COUNT(*) as remaining_trends FROM "ChannelTrend";
```

### 步骤 5: 执行查询

1. 点击 **"Run"** 或 **"Execute"** 按钮
2. 等待执行完成
3. 查看结果：
   - `channel_count` 和 `trend_count` 应该显示删除前的数量
   - `remaining_channels` 和 `remaining_trends` 应该显示 `0`

### 步骤 6: 确认删除成功

执行以下查询确认：

```sql
-- 确认所有数据已删除
SELECT 
  (SELECT COUNT(*) FROM "Channel") as channels,
  (SELECT COUNT(*) FROM "ChannelTrend") as trends;
```

两个值都应该是 `0`。

---

## 🔧 方法二：使用 psql 命令行工具（高级）

如果您熟悉命令行，可以使用 `psql` 直接连接数据库。

### 步骤 1: 获取数据库连接信息

1. 在 Railway Dashboard 中，打开 PostgreSQL 服务
2. 找到 **"Connect"** 或 **"Settings"** 标签
3. 复制 **"Postgres URL"** 或 **"Connection String"**
   - 格式类似：`postgresql://postgres:password@host:port/railway`

### 步骤 2: 安装 psql（如果未安装）

**macOS**:
```bash
# 使用 Homebrew
brew install postgresql

# 或使用 MacPorts
sudo port install postgresql15
```

**Linux**:
```bash
# Ubuntu/Debian
sudo apt-get install postgresql-client

# CentOS/RHEL
sudo yum install postgresql
```

**Windows**:
- 下载并安装 [PostgreSQL](https://www.postgresql.org/download/windows/)
- 或使用 [WSL](https://docs.microsoft.com/en-us/windows/wsl/)

### 步骤 3: 连接数据库

在终端中执行：

```bash
# 替换为您的实际连接字符串
psql "postgresql://postgres:JUsqimUhdhHSOJhJyWpdPMbhyAokKNaq@caboose.proxy.rlwy.net:31013/railway"
```

**注意**: 
- 如果连接字符串包含特殊字符，请用引号括起来
- 如果提示输入密码，使用连接字符串中的密码

### 步骤 4: 执行清除命令

连接成功后，在 `psql` 提示符下执行：

```sql
-- 查看当前数据
SELECT COUNT(*) FROM "Channel";
SELECT COUNT(*) FROM "ChannelTrend";

-- 删除所有分析记录
DELETE FROM "ChannelTrend";
DELETE FROM "Channel";

-- 验证删除
SELECT COUNT(*) FROM "Channel";
SELECT COUNT(*) FROM "ChannelTrend";
```

### 步骤 5: 退出 psql

```sql
\q
```

---

## 🌐 方法三：使用在线 SQL 客户端（备选）

如果 Railway Dashboard 的查询界面不可用，可以使用在线 SQL 客户端。

### 步骤 1: 选择在线客户端

推荐工具：
- [Adminer](https://www.adminer.org/) - 单文件 PHP 工具
- [DBeaver](https://dbeaver.io/) - 跨平台数据库工具
- [pgAdmin](https://www.pgadmin.org/) - PostgreSQL 官方工具

### 步骤 2: 获取连接信息

从 Railway Dashboard 获取：
- **Host**: `caboose.proxy.rlwy.net`（或您的实际主机）
- **Port**: `31013`（或您的实际端口）
- **Database**: `railway`
- **Username**: `postgres`
- **Password**: `JUsqimUhdhHSOJhJyWpdPMbhyAokKNaq`（或您的实际密码）

### 步骤 3: 连接数据库

使用上述信息连接到 PostgreSQL 数据库。

### 步骤 4: 执行清除命令

在 SQL 编辑器中执行：

```sql
DELETE FROM "ChannelTrend";
DELETE FROM "Channel";
```

---

## ⚠️ 重要注意事项

### 1. 数据备份（可选但推荐）

在执行删除前，如果您想备份数据：

```sql
-- 导出 Channel 表数据（如果需要）
COPY "Channel" TO '/tmp/channel_backup.csv' WITH CSV HEADER;

-- 导出 ChannelTrend 表数据（如果需要）
COPY "ChannelTrend" TO '/tmp/channel_trend_backup.csv' WITH CSV HEADER;
```

### 2. 只删除特定频道（可选）

如果您只想删除特定频道的记录：

```sql
-- 替换 'YOUR_CHANNEL_ID' 为实际的频道 ID
DELETE FROM "ChannelTrend" WHERE "channelId" = 'YOUR_CHANNEL_ID';
DELETE FROM "Channel" WHERE "channelId" = 'YOUR_CHANNEL_ID';
```

### 3. 保留用户数据

以下命令**只删除分析数据**，不会删除用户数据：

```sql
-- 这些表不会被删除
-- User 表
-- 其他业务表（如果有）
```

---

## ✅ 验证清除成功

清除后，执行以下验证：

```sql
-- 1. 确认 Channel 表为空
SELECT COUNT(*) as channel_count FROM "Channel";
-- 应该返回 0

-- 2. 确认 ChannelTrend 表为空
SELECT COUNT(*) as trend_count FROM "ChannelTrend";
-- 应该返回 0

-- 3. 确认其他表未受影响（可选）
SELECT COUNT(*) as user_count FROM "User";
-- 应该返回 > 0（如果有用户数据）
```

---

## 🔄 清除后的下一步

### 1. 重新分析频道

1. 打开前端应用（Vercel 部署）
2. 输入一个 YouTube 频道标识符
3. 点击"分析"按钮
4. 等待分析完成（1-2 分钟）

### 2. 验证新数据格式

分析完成后，检查数据库：

```sql
-- 检查新保存的数据格式
SELECT 
  ct.id,
  ct."matchScore",
  ct."recommendationData"->>'viralPotential' as viral_potential,
  ct."recommendationData"->>'performanceScore' as performance_score,
  t.keyword
FROM "ChannelTrend" ct
JOIN "Trend" t ON ct."trendId" = t.id
LIMIT 5;
```

应该看到：
- `matchScore` 值不同
- `viral_potential` 值不同
- `performance_score` 值不同
- `recommendationData` 字段包含完整数据

### 3. 验证前端显示

在前端页面检查：
- ✅ 每个推荐的数据不同
- ✅ 7天趋势预测有数据
- ✅ 脚本生成功能正常

---

## 🐛 常见问题

### Q1: 找不到 Query 界面

**解决方案**:
- 使用方法二（psql）或方法三（在线客户端）
- 检查 Railway Dashboard 是否有更新
- 联系 Railway 支持

### Q2: 执行 SQL 时出错

**可能原因**:
- 表名大小写问题（PostgreSQL 区分大小写）
- 权限不足
- 连接超时

**解决方案**:
- 确保表名使用双引号：`"Channel"` 而不是 `channel`
- 检查数据库用户权限
- 重试连接

### Q3: 删除后数据仍然显示

**可能原因**:
- 前端缓存了旧数据
- 浏览器缓存

**解决方案**:
1. 清除浏览器缓存（Ctrl+Shift+R 或 Cmd+Shift+R）
2. 硬刷新页面
3. 清除浏览器存储（开发者工具 → Application → Clear Storage）

### Q4: 连接数据库失败

**可能原因**:
- 连接字符串错误
- 网络问题
- Railway 服务未运行

**解决方案**:
1. 检查连接字符串是否正确
2. 确认 Railway 服务正在运行
3. 检查网络连接
4. 尝试使用 Railway Dashboard 的 Query 界面

---

## 📝 快速参考

### 完整清除命令（复制粘贴）

```sql
-- 删除所有分析记录
DELETE FROM "ChannelTrend";
DELETE FROM "Channel";

-- 验证删除
SELECT 
  (SELECT COUNT(*) FROM "Channel") as channels,
  (SELECT COUNT(*) FROM "ChannelTrend") as trends;
```

### 只删除特定频道

```sql
-- 替换 'YOUR_CHANNEL_ID' 为实际的频道 ID
DELETE FROM "ChannelTrend" WHERE "channelId" = 'YOUR_CHANNEL_ID';
DELETE FROM "Channel" WHERE "channelId" = 'YOUR_CHANNEL_ID';
```

---

## 📞 需要帮助？

如果遇到问题：
1. 查看 Railway 文档：[Railway Docs](https://docs.railway.app)
2. 检查 Railway Dashboard 的日志
3. 联系 Railway 支持

---

**更新日期**: 2026-01-17
