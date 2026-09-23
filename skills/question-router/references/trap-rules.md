# Trap Rules（question-router 风险识别）

## Polarity

- 含否定意图（错误的是/不正确的是/不属于/不能说明/未体现/没有/不是）→ NEGATIVE。
- 否则 → POSITIVE。
- 双重否定叠加时，polarity 可能含糊 → 标记 DOUBLE_NEGATION，交由 evidence-judge 处理。

## 风险陷阱类型

| 类型 | 触发 |
| --- | --- |
| NEGATION | 否定词（错误的是、不正确的是、不属于、不能说明、未体现、没有） |
| DOUBLE_NEGATION | 并非…不、无不、不无、双重否定结构 |
| ABSOLUTE_WORDING | 全部、所有、任何、唯一、一定、必须、完全、从不、绝不、只能 |
| ENTITY_SWITCH | 主体被替换（A 的性质安到 B） |
| TIME_RANGE_CHANGE | 时间范围被改变（把某时期说成普遍） |
| SCOPE_CHANGE | 范围扩大/缩小（部分→全部） |
| CAUSE_CORRELATION | 把相关当因果 |
| PARTIAL_TRUTH | 半对半错、以偏概全 |
| WRONG_PREMISE | 前提错误 |
| DYNAMIC_FACT | 动态触发词（见下） |

## 动态事实触发词

当前、目前、截至、最新、现在、现有、多少篇、被引、下载、排名、检索结果

命中任一 → `dynamic=true`，必须实时检索。

## 绝对化处理

出现 ABSOLUTE_WORDING → 要求反例核查（requires_counterexample_check）。
