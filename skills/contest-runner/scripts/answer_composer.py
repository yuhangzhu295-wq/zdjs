#!/usr/bin/env python3
"""answer_composer.py — 确定性答案合成。

模型只产出 option_verdicts，最终字母由本脚本确定，不再让模型选字母。

用法：
  echo '{"question_type":"single_choice","polarity":"POSITIVE",'\
       '"option_verdicts":{"A":"TRUE","B":"FALSE","C":"FALSE","D":"FALSE"}}' \
    | python3 answer_composer.py

输出：
  {"ok": true, "answers": ["A"], "answer": "A"}
"""

from __future__ import annotations

import json
import sys

VALID_VERDICTS = {"TRUE", "FALSE", "UNKNOWN", "CONFLICT"}


def compose(question_type: str, polarity: str, verdicts: dict[str, str]):
    """返回 (answers, ok)。ok=False 表示不能唯一确定。"""
    options = sorted(verdicts.keys())
    if not options:
        return [], False

    # 存在关键 UNKNOWN / CONFLICT → 不直接选择
    if any(verdicts.get(k) in ("UNKNOWN", "CONFLICT") for k in options):
        return [], False

    if question_type == "multiple_choice":
        target = "TRUE" if polarity == "POSITIVE" else "FALSE"
        answers = [k for k in options if verdicts.get(k) == target]
        return answers, True

    # single_choice / true_false
    target = "TRUE" if polarity == "POSITIVE" else "FALSE"
    matches = [k for k in options if verdicts.get(k) == target]
    if len(matches) == 1:
        return matches, True
    return [], False


def main() -> None:
    raw = sys.stdin.read()
    try:
        data = json.loads(raw) if raw.strip() else {}
        qtype = data.get("question_type", "single_choice")
        polarity = data.get("polarity", "POSITIVE")
        verdicts = data.get("option_verdicts", {})
        if not isinstance(verdicts, dict):
            raise ValueError("option_verdicts must be an object")

        answers, ok = compose(qtype, polarity, verdicts)
        answer = answers[0] if len(answers) == 1 else "".join(answers)
        out = {"ok": ok, "answers": answers, "answer": answer or None}
        code = 0
    except Exception as e:  # noqa: BLE001
        out = {"error": f"{type(e).__name__}: {e}"}
        code = 1
    print(json.dumps(out, ensure_ascii=False))
    sys.exit(code)


if __name__ == "__main__":
    main()
