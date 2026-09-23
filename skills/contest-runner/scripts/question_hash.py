#!/usr/bin/env python3
"""question_hash.py — 确定性题目哈希（去重守卫）。

纯标准库，可独立运行，供任意 Harness 调用。

用法：
  echo '{"question": "...", "options": {"A": "...", "B": "..."}}' | python3 question_hash.py

输出：
  {"question_hash": "<sha256 hex>"}
"""

from __future__ import annotations

import hashlib
import json
import re
import sys


def normalize(text: str) -> str:
    """去空白、统一全半角、小写。"""
    text = text.strip()
    text = re.sub(r"\s+", " ", text)
    text = "".join(
        chr(ord(c) - 0xFEE0) if 0xFF01 <= ord(c) <= 0xFF5E else c for c in text
    )
    return text.lower()


def question_hash(question: str, options: dict[str, str]) -> str:
    """SHA256(normalized_question + normalized_options)。"""
    q = normalize(question)
    opts = "|".join(
        f"{normalize(k)}:{normalize(v)}" for k, v in sorted(options.items())
    )
    payload = f"{q}\n{opts}"
    return hashlib.sha256(payload.encode("utf-8")).hexdigest()


def main() -> None:
    raw = sys.stdin.read()
    try:
        data = json.loads(raw) if raw.strip() else {}
        question = data.get("question", "")
        options = data.get("options", {})
        if not isinstance(options, dict):
            raise ValueError("options must be an object")
        out = {"question_hash": question_hash(question, options)}
        code = 0
    except Exception as e:  # noqa: BLE001
        out = {"error": f"{type(e).__name__}: {e}"}
        code = 1
    print(json.dumps(out, ensure_ascii=False))
    sys.exit(code)


if __name__ == "__main__":
    main()
