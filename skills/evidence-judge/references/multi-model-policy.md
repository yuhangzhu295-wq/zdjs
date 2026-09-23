# Multi-Model Policy

## 模型角色

| 模型 | 角色 |
| --- | --- |
| GPT | Primary Solver + Final Judge |
| Claude | Independent Critic |
| DeepSeek | Evidence Verifier / Red Team |

## 调用模式

- 正常题：Evidence → GPT。
- 风险题：Evidence → GPT + Claude 独立（并行）。
- 冲突题：Evidence → GPT + Claude → DeepSeek Red Team。

## 独立分析约束

- Claude 首次分析不得看到 GPT 输出。
- DeepSeek Red Team 不作为第三票。

## 统一 AgentResult 协议

```json
{
  "agent_role": "GPT_PRIMARY",
  "status": "SUCCESS",
  "option_verdicts": {"A": "TRUE", "B": "FALSE", "C": "UNKNOWN", "D": "CONFLICT"},
  "evidence_refs": {"A": ["EV_001"], "B": [], "C": [], "D": []},
  "reasoning_summary": "...",
  "uncertainties": [],
  "missing_evidence": [],
  "needs_more_search": false,
  "requested_searches": []
}
```

- 每个选项 verdict 只允许 TRUE / FALSE / UNKNOWN / CONFLICT。
- 模型不负责最终选 A/B/C/D，最终字母由 deterministic Answer Composer 完成。
- 任何 evidence_id 必须存在于 EvidencePool，否则 PROTOCOL_REJECT。

## 协议失败处理

- schema 错误 → 允许 1 次 repair retry（只修结构，不改语义）；再失败 → PROTOCOL_FAILED，
  该 Agent 不得参与 Final Judge。
