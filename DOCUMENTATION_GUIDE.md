# TrendForge 文档使用指南

> 本文档说明如何有效使用 TrendForge 项目的各种文档，特别是 `.cursorrules` 和 `project-memory.md` 的配合使用。

**最后更新**: 2024-01-13

---

## 📋 文档概览

### 核心文档

| 文档 | 用途 | 受众 | 更新频率 |
|------|------|------|----------|
| **`.cursorrules`** | 编码规范、架构约定、技术栈偏好 | Cursor AI + 开发团队 | 架构/规范变更时 |
| **`project-memory.md`** | 历史结论、决策记录、优化历程 | 开发团队 + 新成员 | 每次重大变更后 |
| **`ALGORITHM_DOCUMENTATION.md`** | 算法详细说明、模型参数 | 算法工程师 + 开发团队 | 算法变更时 |
| **`DEPLOYMENT.md`** | 部署指南、环境配置 | DevOps + 部署人员 | 部署流程变更时 |

---

## 🔄 `.cursorrules` 与 `project-memory.md` 配合使用流程

### 1. 理解两者的区别

#### `.cursorrules` (规范文档)
- **性质**: 静态规范、约定、规则
- **内容**: 
  - 编码规范（命名、格式、组织）
  - 技术栈偏好
  - 架构约定
  - 禁忌事项
  - 常用模式
- **特点**: 相对稳定，变更较少
- **作用**: 指导"如何做"

#### `project-memory.md` (历史文档)
- **性质**: 动态记录、经验总结、决策历史
- **内容**:
  - 项目演进历史
  - 算法优化历程
  - 问题解决方案
  - 性能优化记录
  - 技术债务
- **特点**: 持续更新，记录变化
- **作用**: 说明"为什么这样做"

---

## 📖 使用场景和流程

### 场景 1: 开发新功能

**流程步骤:**

```
1. 查看 .cursorrules
   ↓
   了解: 编码规范、命名规则、文件组织、技术栈
   ↓
2. 查看 project-memory.md
   ↓
   了解: 相关功能的演进历史、类似功能的实现经验
   ↓
3. 参考 ALGORITHM_DOCUMENTATION.md (如涉及算法)
   ↓
   了解: 算法细节、参数配置、评估标准
   ↓
4. 遵循规范进行开发
   ↓
5. 完成后更新 project-memory.md
   ↓
   记录: 新功能决策、实现方式、遇到的问题
```

**示例:**

假设要开发一个新的"竞品分析"功能：

1. **查看 `.cursorrules`**:
   - 了解后端服务应放在 `backend/services/` 目录
   - 遵循 `snake_case` 命名规范
   - 使用 `async/await` 处理异步操作
   - 错误处理使用 try-except + fallback

2. **查看 `project-memory.md`**:
   - 查看"架构决策"部分，了解模块化设计原则
   - 查看"关键问题与解决方案"，避免重复踩坑
   - 查看"性能优化记录"，了解缓存和并行处理经验

3. **开发实现**:
   - 创建 `backend/services/competitor_analyzer.py`
   - 遵循 `.cursorrules` 中的编码规范
   - 参考 `project-memory.md` 中的最佳实践

4. **更新文档**:
   - 在 `project-memory.md` 的"架构决策"或"未来改进方向"中记录新功能

---

### 场景 2: 解决技术问题

**流程步骤:**

```
1. 查看 project-memory.md 的"关键问题与解决方案"
   ↓
   查找: 是否已有类似问题的解决方案
   ↓
2. 如果找到，参考解决方案
   ↓
3. 如果未找到，查看 .cursorrules 的"禁忌和注意事项"
   ↓
   避免: 常见错误和陷阱
   ↓
4. 解决问题
   ↓
5. 更新 project-memory.md
   ↓
   记录: 新问题、解决方案、经验总结
```

**示例:**

假设遇到"预测播放量不准确"的问题：

1. **查看 `project-memory.md`**:
   - 在"关键问题与解决方案"中找到"预测播放量固定值问题"
   - 了解历史解决方案：多因素动态算法

2. **参考 `.cursorrules`**:
   - 查看"核心算法参数"部分
   - 了解预测播放量算法的正确公式

3. **解决问题**:
   - 应用历史解决方案
   - 或基于历史经验开发新方案

4. **更新文档**:
   - 如果问题已解决，在 `project-memory.md` 的"技术债务记录"中标记为"已解决"
   - 如果是新问题，添加到"关键问题与解决方案"

---

### 场景 3: 优化算法或性能

**流程步骤:**

```
1. 查看 project-memory.md 的"核心算法优化历程"
   ↓
   了解: 历史优化经验、参数调整记录
   ↓
2. 查看 ALGORITHM_DOCUMENTATION.md
   ↓
   了解: 当前算法参数、评估指标
   ↓
3. 查看 .cursorrules 的"核心算法参数"
   ↓
   了解: 算法公式、参数范围
   ↓
4. 进行优化
   ↓
5. 更新两个文档
   ↓
   project-memory.md: 记录优化历程、效果
   ALGORITHM_DOCUMENTATION.md: 更新参数配置
```

**示例:**

假设要优化 ML 模型的准确度：

1. **查看 `project-memory.md`**:
   - 在"核心算法优化历程"中查看"算法准确度优化"部分
   - 了解历史优化措施：对数变换、交叉验证、特征选择

2. **查看 `ALGORITHM_DOCUMENTATION.md`**:
   - 了解当前模型参数配置
   - 查看评估指标定义

3. **查看 `.cursorrules`**:
   - 了解 ML 模型参数的规范范围
   - 了解模型选择标准

4. **进行优化**:
   - 基于历史经验调整参数
   - 记录优化效果

5. **更新文档**:
   - `project-memory.md`: 在"核心算法优化历程"中记录新优化
   - `ALGORITHM_DOCUMENTATION.md`: 更新参数配置

---

### 场景 4: 代码审查

**流程步骤:**

```
1. 对照 .cursorrules 检查编码规范
   ↓
   检查: 命名、格式、文件组织、错误处理
   ↓
2. 参考 project-memory.md 检查最佳实践
   ↓
   检查: 是否遵循历史经验、是否重复已知问题
   ↓
3. 提供审查意见
   ↓
4. 如有新发现，更新 project-memory.md
```

**检查清单:**

- [ ] 命名规范是否符合 `.cursorrules`？
- [ ] 文件组织是否符合架构约定？
- [ ] 错误处理是否遵循最佳实践？
- [ ] 是否避免了 `project-memory.md` 中记录的问题？
- [ ] 是否使用了 `project-memory.md` 中推荐的模式？

---

### 场景 5: 新成员入职

**流程步骤:**

```
1. 阅读 .cursorrules (30分钟)
   ↓
   了解: 项目规范、技术栈、架构约定
   ↓
2. 阅读 project-memory.md (1小时)
   ↓
   了解: 项目历史、演进过程、重要决策
   ↓
3. 阅读 ALGORITHM_DOCUMENTATION.md (如需要)
   ↓
   了解: 算法细节、技术实现
   ↓
4. 查看 DEPLOYMENT.md (如需要)
   ↓
   了解: 部署流程、环境配置
   ↓
5. 开始开发
   ↓
   遇到问题时，参考相应文档
```

**学习路径:**

1. **第一天**: 阅读 `.cursorrules` + `project-memory.md` 的"项目演进历史"
2. **第二天**: 阅读 `project-memory.md` 的"关键问题与解决方案"
3. **第三天**: 阅读 `ALGORITHM_DOCUMENTATION.md`（如涉及算法开发）
4. **第四天**: 开始参与小功能开发，遇到问题随时查阅文档

---

## 🎯 在 Cursor 中的实际使用

### 方法 1: 直接引用文档

```
# 开发新功能时
@.cursorrules 我应该如何组织新的服务模块？

# 解决问题时
@project-memory.md 之前遇到过类似的问题吗？

# 优化算法时
@ALGORITHM_DOCUMENTATION.md 当前的模型参数是什么？
```

### 方法 2: 组合引用

```
# 同时参考多个文档
@.cursorrules @project-memory.md 我想添加一个新的推荐算法，应该遵循什么规范？历史上有类似的优化经验吗？
```

### 方法 3: 在代码注释中引用

```python
# 参考 .cursorrules: 核心算法参数 - 匹配分数算法
# 参考 project-memory.md: 核心算法优化历程 - 匹配分数算法优化
def calculate_match_score(...):
    """
    计算匹配分数
    
    算法公式（参考 .cursorrules）:
    match_score = viral_potential * 0.4 + performance_score * 0.25 + relevance_score * 0.35
    
    优化历史（参考 project-memory.md）:
    - MVP 2.0: 初始版本（相关性40% + 风格20% + 受众20% + 机会20%）
    - MVP 3.0: 优化版本（热度40% + 表现25% + 相关性35%）
    """
    pass
```

---

## 📝 文档更新规范

### 何时更新 `.cursorrules`

- ✅ 新增技术栈或依赖
- ✅ 修改编码规范
- ✅ 更新架构约定
- ✅ 添加新的禁忌事项
- ❌ 不要记录具体问题解决方案（应放在 `project-memory.md`）
- ❌ 不要记录历史变更（应放在 `project-memory.md`）

### 何时更新 `project-memory.md`

- ✅ 完成重大功能开发
- ✅ 解决重要技术问题
- ✅ 进行算法优化
- ✅ 做出重要架构决策
- ✅ 发现新的最佳实践
- ✅ 解决技术债务
- ❌ 不要记录编码规范（应放在 `.cursorrules`）
- ❌ 不要记录静态约定（应放在 `.cursorrules`）

---

## 🔍 快速查找指南

### 我想知道...

| 问题 | 查看文档 | 章节 |
|------|----------|------|
| 如何命名变量？ | `.cursorrules` | 编码规范 - Python/TypeScript 命名规则 |
| 为什么这样设计？ | `project-memory.md` | 架构决策 |
| 之前遇到过这个问题吗？ | `project-memory.md` | 关键问题与解决方案 |
| 算法参数是什么？ | `.cursorrules` | 核心算法参数 |
| 算法优化历史？ | `project-memory.md` | 核心算法优化历程 |
| 如何部署？ | `DEPLOYMENT.md` | 全部 |
| 模型详细参数？ | `ALGORITHM_DOCUMENTATION.md` | 参数配置与调优 |
| 性能优化经验？ | `project-memory.md` | 性能优化记录 |
| 技术债务有哪些？ | `project-memory.md` | 技术债务记录 |

---

## 💡 最佳实践

### 1. 开发前必读

```
开始开发新功能前：
1. 快速浏览 .cursorrules 的相关章节
2. 查看 project-memory.md 是否有相关经验
3. 确认理解规范和最佳实践
```

### 2. 遇到问题时

```
遇到问题时的查找顺序：
1. project-memory.md 的"关键问题与解决方案"
2. .cursorrules 的"禁忌和注意事项"
3. 如果未找到，解决问题后更新 project-memory.md
```

### 3. 完成功能后

```
完成功能后的文档更新：
1. 更新 project-memory.md 记录新功能
2. 如果涉及规范变更，更新 .cursorrules
3. 如果涉及算法，更新 ALGORITHM_DOCUMENTATION.md
```

### 4. 定期维护

```
每月回顾：
1. 检查 project-memory.md 的技术债务是否已解决
2. 检查 .cursorrules 是否需要更新（通常较少）
3. 确保文档与代码同步
```

---

## 🎓 总结

### `.cursorrules` 和 `project-memory.md` 的关系

```
.cursorrules (规范)
    ↓
    "如何做" - 静态规范
    ↓
    指导开发
    ↓
project-memory.md (历史)
    ↓
    "为什么这样做" - 动态记录
    ↓
    记录经验
```

### 核心原则

1. **`.cursorrules`**: 规范在前，指导开发
2. **`project-memory.md`**: 经验在后，记录历史
3. **两者配合**: 规范 + 经验 = 高质量代码

---

**文档维护**: 每次重大变更后更新相关文档  
**版本**: 1.0.0  
**最后更新**: 2024-01-13
