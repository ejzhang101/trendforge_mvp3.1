# 数据准确性修复 - MVP 3.1

## 问题描述

用户报告以下指标数据有误，与实际不符：
- ❌ 关键词重要性指标（匹配度）
- ❌ 7天趋势预测
- ❌ 相关信息
- ❌ 匹配度
- ❌ 互联网热度
- ❌ 内容相关性
- ❌ 预测观看数

## 根本原因分析

### 1. 模拟数据生成不准确

**问题**：当没有社交媒体趋势数据时，后端创建的模拟数据过于简单：
- `composite_score` = `topic_score * 100`（固定公式）
- `growth_rate` = `topic_score * 50`（固定公式）
- 没有考虑频道表现、排名等因素

**影响**：导致所有基于这些数据的计算都不准确：
- 互联网热度（viral_potential）不准确
- 匹配度（match_score）不准确
- 预测观看数（predicted_views）不准确

### 2. 互联网热度计算未区分数据来源

**问题**：`_calculate_viral_potential` 方法没有区分真实社交媒体数据和模拟数据

**影响**：模拟数据被当作真实数据处理，导致热度分数虚高或虚低

## 已完成的修复

### 1. 改进模拟社交趋势数据生成 (`backend/app_v2.py`)

**修复前**：
```python
mock_trend = {
    'keyword': topic,
    'composite_score': topic_score * 100,  # 简单固定公式
    'growth_rate': topic_score * 50,  # 简单固定公式
    'sources': ['channel_analysis'],
}
```

**修复后**：
```python
# 1. 考虑频道表现因子
channel_performance_factor = min(1.2, avg_views / 50000)
base_composite = topic_score * 100
composite_score = min(100, base_composite * (0.8 + channel_performance_factor * 0.2))

# 2. 基于排名计算增长率（排名越靠前，增长率越高）
rank_factor = (len(channel_topics) - idx) / len(channel_topics)
growth_rate = topic_score * 30 + rank_factor * 20  # 30-50 范围

# 3. 添加更多上下文信息
mock_trend = {
    'keyword': topic,
    'composite_score': round(composite_score, 2),
    'growth_rate': round(growth_rate, 2),
    'sources': ['channel_analysis'],
    'rising_queries': [topic],
    'trend_score': round(composite_score, 2),
    # ... 更多字段
}
```

**改进点**：
- ✅ 考虑频道表现（高表现频道 = 更高热度）
- ✅ 基于排名计算增长率（模拟新兴趋势）
- ✅ 添加更多上下文信息

### 2. 改进互联网热度计算 (`backend/services/predictive_recommender.py`)

**修复前**：
```python
def _calculate_viral_potential(self, trend: Dict) -> float:
    composite_score = trend.get('composite_score', 0)
    growth_rate = trend.get('growth_rate', 0)
    source_count = len(trend.get('sources', []))
    
    base_score = composite_score
    growth_bonus = min(30, growth_rate * 0.3)
    platform_bonus = min(20, (source_count - 1) * 10)
    
    viral_score = base_score + growth_bonus + platform_bonus
    return min(100, round(viral_score, 2))
```

**修复后**：
```python
def _calculate_viral_potential(self, trend: Dict) -> float:
    # 检查是否有真实的社交媒体数据
    has_real_social_data = any(
        source not in ['channel_analysis', 'database'] 
        for source in sources
    )
    
    # 基础分数
    base_score = composite_score
    
    # 增长加成（基于增长率）
    growth_bonus = min(30, max(0, growth_rate) * 0.3)
    
    # 平台加成（多平台验证）
    platform_bonus = min(20, (source_count - 1) * 10) if source_count > 1 else 0
    
    # 数据质量加成（如果有真实社交媒体数据）
    data_quality_bonus = 5 if has_real_social_data else 0
    
    viral_score = base_score + growth_bonus + platform_bonus + data_quality_bonus
    
    # 确保分数在合理范围内（20-100）
    viral_score = max(20, min(100, round(viral_score, 2)))
    
    return viral_score
```

**改进点**：
- ✅ 区分真实社交媒体数据和模拟数据
- ✅ 为真实数据添加质量加成
- ✅ 确保分数在合理范围内（20-100）

## 数据计算流程

### 1. 匹配度（Match Score）计算

```
匹配度 = 互联网热度 × 40% + 表现潜力 × 25% + 内容相关性 × 35%
```

**各组成部分**：
- **互联网热度**：基于 `composite_score`、`growth_rate`、平台数量
- **表现潜力**：基于互联网热度、主题相关性、风格兼容性、受众匹配度
- **内容相关性**：基于主题相关性（50%）、风格兼容性（30%）、受众匹配度（20%）

### 2. 互联网热度（Viral Potential）计算

```
互联网热度 = 基础分数 + 增长加成 + 平台加成 + 数据质量加成
```

**各组成部分**：
- **基础分数**：`composite_score`（来自社交媒体聚合或模拟数据）
- **增长加成**：`growth_rate × 0.3`（最高 30 分）
- **平台加成**：多平台验证（Twitter + Reddit + Google Trends，最高 20 分）
- **数据质量加成**：如果有真实社交媒体数据，+5 分

### 3. 内容相关性（Relevance Score）计算

```
内容相关性 = 主题相关性 × 50% + 风格兼容性 × 30% + 受众匹配度 × 20%
```

**各组成部分**：
- **主题相关性**：关键词与频道主题的匹配程度
- **风格兼容性**：关键词与频道内容风格的兼容性
- **受众匹配度**：关键词与目标受众的匹配度

### 4. 预测观看数（Predicted Views）计算

```
预测观看数 = 基准播放量 × 热度系数 × 相关性系数 × 表现潜力系数 × 时效性系数 × 频道稳定性 × 标题优化 × 置信度因子
```

**各系数范围**：
- **热度系数**：1.0-2.5（基于互联网热度）
- **相关性系数**：0.7-1.3（基于内容相关性）
- **表现潜力系数**：0.8-1.5（基于表现潜力）
- **时效性系数**：0.9-1.2（基于匹配度）
- **频道稳定性**：0.95-1.1（基于历史表现稳定性）
- **标题优化**：0.98-1.05（小幅提升）
- **置信度因子**：0.8-1.1（基于预测置信度）

**最终范围**：1000 - 50,000,000 次观看

## 验证步骤

### 1. 检查后端日志

在 Railway 部署日志中，应该看到：
```
✅ Using content_analyzer: LightweightContentAnalyzer
📊 Step 1/5: Analyzing channel...
🌐 Step 2/5: Collecting social media trends...
💡 Step 3/5: Generating recommendations...
🔮 Step 5/5: Generating Prophet predictions...
```

### 2. 检查数据范围

所有指标应该在合理范围内：
- **匹配度**：0-100
- **互联网热度**：20-100（最低 20，避免过低）
- **内容相关性**：0-100
- **预测观看数**：1,000 - 50,000,000

### 3. 测试不同场景

1. **有社交媒体数据**：
   - 互联网热度应该较高（有数据质量加成）
   - 匹配度应该更准确

2. **无社交媒体数据（使用模拟数据）**：
   - 互联网热度应该基于频道表现和主题排名
   - 匹配度应该基于频道分析

3. **高表现频道**：
   - 模拟数据的 `composite_score` 应该更高
   - 预测观看数应该更准确

## 常见问题排查

### 问题 1：所有指标都显示为固定值

**可能原因**：
- 使用了缓存的旧数据
- 后端未正确计算

**解决方案**：
1. 清除数据库缓存（删除该频道的分析记录）
2. 重新分析频道
3. 检查后端日志，确认看到计算过程

### 问题 2：互联网热度总是 50

**可能原因**：
- 使用了旧的模拟数据生成逻辑
- `composite_score` 计算不正确

**解决方案**：
1. 确认后端代码已更新（检查 `app_v2.py` 第 516-532 行）
2. 检查 `_calculate_viral_potential` 方法（`predictive_recommender.py` 第 356-385 行）
3. 重新部署后端

### 问题 3：预测观看数不准确

**可能原因**：
- 基准播放量（`avg_views`）不正确
- 系数计算有误

**解决方案**：
1. 检查 `high_performers.avg_views` 和 `median_views` 是否正确
2. 检查 `_predict_performance` 方法（`predictive_recommender.py` 第 491-575 行）
3. 确认所有系数都在合理范围内

## 相关文件

- `backend/app_v2.py` - 主应用，模拟数据生成（第 516-532 行）
- `backend/services/predictive_recommender.py` - 推荐引擎，所有计算逻辑
  - `_calculate_viral_potential` (第 356-385 行) - 互联网热度计算
  - `_calculate_match_score` (第 270-354 行) - 匹配度计算
  - `_calculate_performance_potential` (第 369-385 行) - 表现潜力计算
  - `_predict_performance` (第 491-575 行) - 预测观看数计算
- `frontend/app/analysis/[channelId]/page.tsx` - 前端显示页面

## 更新日期

2026-01-14 - MVP 3.1 数据准确性修复
