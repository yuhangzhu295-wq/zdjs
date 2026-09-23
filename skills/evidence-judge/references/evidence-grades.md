# Evidence Grades 与 Gate 规则

## Evidence Grade

- **A**：实时原始数据库 / 官方一手资料直接证明关键事实；或可复算的形式化证据。
- **B**：两个独立可靠高质量来源一致。
- **C**：一个可靠来源，但仍存在推理步骤。
- **D**：证据弱，主要依赖模型。
- **X**：冲突。
- **U**：不足。

**模型数量永远不能改变 Grade**：即便 3:0 一致，也不能把 C 升为 A。

## Evidence Gate 规则（确定性）

```
动态事实无 live evidence        → NEED_MORE_SEARCH
一手来源冲突                    → CONFLICT
fake evidence id                → PROTOCOL_REJECT
多选存在 UNKNOWN                → ESCALATE
无法产生唯一单选答案            → ESCALATE
Grade D / U / X                 → ESCALATE
否则                            → PASS
```

只有 PASS 才允许 contest-runner 点击答案。

## 答案合成（deterministic）

- POSITIVE 单选：唯一 TRUE。
- NEGATIVE 单选：唯一 FALSE。
- POSITIVE 多选：所有 TRUE。
- NEGATIVE 多选：所有 FALSE。
- 存在关键 UNKNOWN 或 CONFLICT → 不直接选择。
