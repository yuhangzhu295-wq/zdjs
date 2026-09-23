# Web Research Query Strategy

## 查询构造

1. 优先带官方/权威限定词：`site:gov.cn`、`site:edu.cn`、产品官方域名。
2. 事实类用精确短语；概念类用定义词（「定义」「含义」「规定」）。
3. 动态事实加时间限定或「最新」。

## 搜索预算

| 模式 | max_searches |
| --- | --- |
| FAST | 3 |
| NORMAL | 8 |
| ESCALATED | 15 |

达到预算仍不足 → NEEDS_VERIFICATION，禁止无限循环。

## support / counter 查询

- 重要 Claim：默认执行 support query（找支持证据）。
- 必要时执行 counter query（找反证）。
- 绝对化 Claim：必须寻找反例。

## 结果处理

- 无结果 → reformulate query（换词/扩范围）。
- 结果过多 → refine（加限定词、站点限定、时间限定）。
