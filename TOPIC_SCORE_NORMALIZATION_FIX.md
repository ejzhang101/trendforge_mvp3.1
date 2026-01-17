# 主题重要性分数归一化修复

## 🔍 问题描述

**问题**: 主题重要性分数显示为 9.00 和 3.60，但根据规则应该是 0-1 之间的 TF-IDF 分数。

**影响**:
- 前端显示不符合文档说明（0-1 范围）
- 分数标签分类错误（所有主题都显示为"核心"）
- 用户困惑

## 🔧 根本原因

1. **TF-IDF 计算未归一化**: 
   - 原始 TF-IDF 分数可能很大（取决于文档数量和词频）
   - 公式: `(TF / total_words) * log(N / DF)`
   - 对于高频词，分数可能远大于 1

2. **Bigrams 分数未归一化**:
   - Bigrams 使用 `count * 1.5` 作为分数
   - 如果某个 bigram 出现多次，分数可能很大

3. **合并分数未归一化**:
   - 多个方法合并时，分数可能累加
   - 方法加成 `(1 + method_bonus)` 可能使分数超过 1

## ✅ 修复方案

### 修复 1: TF-IDF 分数归一化

在 `_extract_tfidf_topics` 方法中，计算完所有 TF-IDF 分数后，进行归一化：

```python
# 归一化分数到 0-1 范围
if tfidf_scores:
    max_score = max(tfidf_scores.values())
    min_score = min(tfidf_scores.values())
    score_range = max_score - min_score if max_score > min_score else 1.0
    
    # 归一化: (score - min) / range
    normalized_scores = {
        word: (score - min_score) / score_range if score_range > 0 else 0.5
        for word, score in tfidf_scores.items()
    }
```

### 修复 2: 合并分数归一化

在 `_merge_topics` 方法中，合并所有主题后，进行归一化：

```python
# 归一化所有分数到 0-1 范围
if topic_map:
    all_scores = [t['score'] for t in topic_map.values()]
    max_score = max(all_scores) if all_scores else 1.0
    min_score = min(all_scores) if all_scores else 0.0
    score_range = max_score - min_score if max_score > min_score else 1.0
    
    # 归一化每个主题的分数
    for topic_data in topic_map.values():
        if score_range > 0:
            topic_data['score'] = (topic_data['score'] - min_score) / score_range
        else:
            topic_data['score'] = 0.5  # 默认值
```

## 📊 归一化公式

**Min-Max 归一化**:
```
normalized_score = (score - min_score) / (max_score - min_score)
```

**特点**:
- 将分数映射到 [0, 1] 范围
- 保持相对大小关系
- 最高分 = 1.0，最低分 = 0.0

## 🎯 预期效果

修复后：
- ✅ 所有主题分数都在 0-1 范围内
- ✅ 分数标签正确分类：
  - 0.9-1.0: 核心
  - 0.7-0.9: 次要
  - 0.5-0.7: 辅助
  - <0.5: 边缘
- ✅ 前端显示符合文档说明

## 📋 验证步骤

1. **重新分析频道**
   - 清除数据库缓存
   - 重新分析频道

2. **检查主题分数**
   - 打开"核心主题"部分
   - 验证所有分数都在 0-1 范围内
   - 验证分数标签正确显示

3. **检查分数分布**
   - 应该有不同级别的主题（核心、次要、辅助、边缘）
   - 不应该所有主题都是"核心"

---

**更新日期**: 2026-01-17
