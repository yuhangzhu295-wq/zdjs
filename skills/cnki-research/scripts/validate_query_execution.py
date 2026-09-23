#!/usr/bin/env python3
"""validate_query_execution.py — 校验 CNKI 检索的 query_plan 与 query_executed 是否一致。

纯标准库，可独立运行。

校验逻辑：
- target 是「提取目标」，不是检索参数，跳过。
- sort_by 按语义映射校验排序方向（citation_desc → 被引 等）。
- 值型字段（author/title/subject/institution/keyword/source/year_from/year_to）
  按「具体值必须出现在执行记录中」校验，避免误匹配字段名。

关键字段不一致 → mismatch，该 Evidence 不得评 A。

用法：
  echo '{"query_plan":{"author":"张三","year_from":2023,"sort_by":"citation_desc"},'\
       '"query_executed":{"field":"作者","value":"张三","year":"2023","sort":"被引降序"}}' \
    | python3 validate_query_execution.py

输出：
  {"match": true, "mismatches": []}
"""

from __future__ import annotations

import json
import sys

# sort_by 语义映射：plan 的枚举值 -> executed 中可接受的关键字
_SORT_HINTS = {
    "citation_desc": ("被引",),
    "download_desc": ("下载",),
    "date_desc": ("时间", "发表时间"),
    "date_asc": ("时间", "发表时间"),
    "relevance": ("相关", "相关度"),
}
_ANY_SORT = ("被引", "下载", "时间", "相关", "sort")

# 值型字段：按具体值校验
_VALUE_KEYS = (
    "author", "title", "subject", "institution", "keyword", "source",
    "year_from", "year_to",
)


def _sort_match(plan_val, executed_text: str) -> bool:
    hints = _SORT_HINTS.get(plan_val)
    if hints is None:
        return any(h in executed_text for h in _ANY_SORT)
    return any(h in executed_text for h in hints)


def validate(query_plan: dict, query_executed: dict) -> list[str]:
    mismatches: list[str] = []
    if not isinstance(query_plan, dict) or not isinstance(query_executed, dict):
        return ["query_plan and query_executed must be objects"]

    executed_text = json.dumps(query_executed, ensure_ascii=False)

    for key, val in query_plan.items():
        if val is None:
            continue
        if key == "target":
            # 提取目标（COAUTHOR/RESULT_COUNT/DOI…）不是检索参数，不校验
            continue
        if key == "sort_by":
            if not _sort_match(val, executed_text):
                mismatches.append(key)
            continue
        # 值型字段：具体值必须出现在执行记录中
        if str(val) not in executed_text:
            mismatches.append(key)

    return mismatches


def main() -> None:
    raw = sys.stdin.read()
    try:
        data = json.loads(raw) if raw.strip() else {}
        query_plan = data.get("query_plan", {})
        query_executed = data.get("query_executed", {})
        mismatches = validate(query_plan, query_executed)
        out = {"match": not mismatches, "mismatches": mismatches}
        code = 0
    except Exception as e:  # noqa: BLE001
        out = {"error": f"{type(e).__name__}: {e}"}
        code = 1
    print(json.dumps(out, ensure_ascii=False))
    sys.exit(code)


if __name__ == "__main__":
    main()
