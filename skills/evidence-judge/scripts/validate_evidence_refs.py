#!/usr/bin/env python3
"""validate_evidence_refs.py — 校验 AgentResult 引用的 evidence_id 是否真实存在。

纯标准库，可独立运行。

用法：
  echo '{"evidence_ids": ["EV_001","EV_002"],'\
       '"agent_result": {"evidence_refs": {"A": ["EV_001"], "B": ["EV_999"]}}}' \
    | python3 validate_evidence_refs.py

输出：
  {"valid": false, "invalid_refs": ["EV_999"]}
"""

from __future__ import annotations

import json
import sys


def validate(evidence_ids: list[str], evidence_refs: dict[str, list[str]]):
    valid = set(evidence_ids)
    invalid: list[str] = []
    for refs in evidence_refs.values():
        for ref in refs:
            if ref not in valid:
                invalid.append(ref)
    # 去重保序
    seen: set[str] = set()
    unique = [r for r in invalid if not (r in seen or seen.add(r))]
    return unique


def main() -> None:
    raw = sys.stdin.read()
    try:
        data = json.loads(raw) if raw.strip() else {}
        evidence_ids = data.get("evidence_ids", [])
        evidence_refs = data.get("agent_result", {}).get("evidence_refs", {})
        if not isinstance(evidence_refs, dict):
            raise ValueError("agent_result.evidence_refs must be an object")
        invalid = validate(evidence_ids, evidence_refs)
        out = {"valid": not invalid, "invalid_refs": invalid}
        code = 0
    except Exception as e:  # noqa: BLE001
        out = {"error": f"{type(e).__name__}: {e}"}
        code = 1
    print(json.dumps(out, ensure_ascii=False))
    sys.exit(code)


if __name__ == "__main__":
    main()
