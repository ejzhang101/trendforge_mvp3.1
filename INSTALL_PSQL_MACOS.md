# 在 macOS 上安装 psql 客户端

## 方法一：使用 Homebrew（推荐）

### 步骤 1: 安装 Homebrew（如果未安装）

```bash
/bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"
```

### 步骤 2: 安装 PostgreSQL 客户端

```bash
brew install postgresql@15
```

### 步骤 3: 添加到 PATH（如果需要）

```bash
echo 'export PATH="/opt/homebrew/opt/postgresql@15/bin:$PATH"' >> ~/.zshrc
source ~/.zshrc
```

**注意**: 如果是 Intel Mac，路径可能是 `/usr/local/opt/postgresql@15/bin`

### 步骤 4: 验证安装

```bash
psql --version
```

应该显示 PostgreSQL 版本号。

---

## 方法二：只安装客户端（轻量级）

如果您只需要 `psql` 客户端，不需要完整的 PostgreSQL 服务器：

```bash
brew install libpq
echo 'export PATH="/opt/homebrew/opt/libpq/bin:$PATH"' >> ~/.zshrc
source ~/.zshrc
```

---

## 方法三：使用 Docker（如果已安装 Docker）

```bash
docker run -it --rm postgres:15 psql "postgresql://postgres:JUsqimUhdhHSOJhJyWpdPMbhyAokKNaq@caboose.proxy.rlwy.net:31013/railway"
```

---

## 方法四：使用 Railway Dashboard（最简单）

如果不想安装命令行工具，可以直接使用 Railway Dashboard：

1. 访问 [Railway Dashboard](https://railway.app)
2. 登录您的账户
3. 找到 PostgreSQL 服务
4. 点击 **"Data"** 或 **"Query"** 标签
5. 在查询界面中执行 SQL 命令

---

## 连接数据库

安装完成后，使用以下命令连接：

```bash
psql "postgresql://postgres:JUsqimUhdhHSOJhJyWpdPMbhyAokKNaq@caboose.proxy.rlwy.net:31013/railway"
```

---

## 执行清除命令

连接成功后，执行：

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

---

## 退出 psql

执行完命令后，输入：

```sql
\q
```

---

**更新日期**: 2026-01-17
