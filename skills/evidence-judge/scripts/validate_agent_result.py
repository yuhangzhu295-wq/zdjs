#!/usr/bin/env python3
"""validate_agent_result.py — 校验模型输出是否符合 AgentResult 协议。

纯标准库，可独立运行。

校验内容：
- status 取值合法（SUCCESS / PROTOCOL_FAILED / ERROR）
- option_verdicts 每个值 ∈ {TRUE, FALSE, UNKNOWN, CONFLICT}
- evidence_refs 中的 evidence_id 必须存在于 evidence_ids
- 必填字段存在

用法：
  echo '{"evidence_ids": ["EV_001"], "agent_result": {"status":"SUCCESS",'\
       '"option_verdicts":{"A":"TRUE"},"evidence_refs":{"A":["EV_001"]}}}' \
    | python3 validate_agent_result.py

输出：
  {"valid": true, "errors": []}
"""

from __future__ import annotations

import json
import sys

VALID_STATUS = {"SUCCESS", "PROTOCOL_FAILED", "ERROR"}
VALID_VERDICTS = {"TRUE", "FALSE", "UNKNOWN", "CONFLICT"}


def validate(evidence_ids: list[str], result: dict) -> list[str]:
    errors: list[str] = []
    if not isinstance(result, dict):
        return ["agent_result must be an object"]

    status = result.get("status")
    if status not in VALID_STATUS:
        errors.append(f"invalid_status: {status!r}")

    verdicts = result.get("option_verdicts")
    if not isinstance(verdicts, dict):
        errors.append("option_verdicts must be an object")
    else:
        for k, v in verdicts.items():
            if v not in VALID_VERDICTS:
                errors.append(f"invalid_verdict: {k}={v!r}")

    refs = result.get("evidence_refs", {})
    if not isinstance(refs, dict):
        errors.append("evidence_refs must be an object")
    else:
        valid_ids = set(evidence_ids)
        for k, ref_list in refs.items():
            for ref in ref_list:
                if ref not in valid_ids:
                    errors.append(f"fake_evidence_id: {k}->{ref}")

    for field in ("reasoning_summary", "uncertainties", "missing_evidence"):
        if field not in result:
            errors.append(f"missing_field: {field}")

    return errors


def main() -> None:
    raw = sys.stdin.read()
    try:
        data = json.loads(raw) if raw.strip() else {}
        evidence_ids = data.get("evidence_ids", [])
        result = data.get("agent_result", {})
        errors = validate(evidence_ids, result)
        out = {"valid": not errors, "errors": errors}
        code = 0
    except Exception as e:  # noqa: BLE001
        out = {"error": f"{type(e).__name__}: {e}"}
        code = 1
    print(json.dumps(out, ensure_ascii=False))
    sys.exit(code)


if __name__ == "__main__":
    main()
