# Red Team Policy（DeepSeek）

## 定位

DeepSeek Red Team **不投票**。必须假设候选答案错误，寻找反证，而非作为第三个投票者。

## 触发条件

- GPT / Claude 冲突。
- Evidence 冲突（Grade X）。
- 存在 UNKNOWN、绝对化、动态数据不足等风险。

## 寻找目标

权威反证、遗漏搜索条件、时间差异、主体变化、范围变化、反例、错误前提、
部分正确、因果/相关混淆。

## 输出（只允许三选一）

- `ATTACK_SUCCESS`：找到足以推翻候选结论的反证。
- `ATTACK_FAILED`：未找到有效反证。
- `NEED_MORE_EVIDENCE`：证据不足以判定，需要额外检索。

## 约束

- 必须引用真实 evidence_id。
- 如需额外检索，返回 requested_searches，由 contest-runner 调度。
