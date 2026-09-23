# CNKI Evidence Extraction

从 CNKI 页面读取结果并生成 Evidence。

## 读取优先级

1. 结构化 DOM / 列表项（结果数量、题名、作者、来源、年份、被引、下载）。
2. 文献详情页（DOI、基金、参考文献、完整作者列表）。
3. 页面可见文本（兜底）。

## 提取规则

- 数值类（结果数量、被引、下载）必须实时读取，`dynamic=true`，`direct_match=true`。
- 列表类（作者、合作者、参考文献）逐项提取，不臆造。
- 读不到关键字段 → 标记 missing，不填占位值（尤其不得填 0 当真实值）。

## Evidence 示例（COAUTHOR）

```json
{
  "evidence_id": "EV_001",
  "claim_id": "claim_A",
  "stance": "support",
  "evidence_type": "PRIMARY_DATABASE",
  "source_name": "中国知网 CNKI",
  "title": "目标文献题名",
  "url": "https://...",
  "fact": "该文献作者为：张三、李四、王五（排除题目指定作者后，合作者为李四、王五）。",
  "retrieved_at": "2026-09-23T03:00:00Z",
  "dynamic": false,
  "direct_match": true,
  "reliability_tier": 1,
  "query_plan": {"author": "张三", "year_from": 2023, "year_to": 2023, "sort_by": "citation_desc", "target": "COAUTHOR"},
  "query_executed": {"field": "作者", "value": "张三", "year": "2023", "sort": "被引降序", "opened": "第1条"}
}
```

## 页面 UI 变化（semantic relocation）

- 字段/按钮位置变化时，用 FIND_TEXT 按可见文本重新定位，不要依赖固定 CSS 选择器。
