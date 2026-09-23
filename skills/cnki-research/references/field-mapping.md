# CNKI Field Mapping

字段语义 → 检索入口/字段名的映射。实际 CNKI 页面字段名以页面为准，本表给出一致语义。

| 语义字段 | 含义 | 常见页面字段 |
| --- | --- | --- |
| title | 篇名/题名 | 篇名 / 题名 |
| subject | 主题 | 主题 |
| author | 作者 | 作者 / 第一作者 |
| institution | 机构 | 单位 / 机构 |
| keyword | 关键词 | 关键词 |
| source | 来源/刊名 | 文献来源 / 期刊 |
| year_from / year_to | 年份范围 | 发表时间（从…到…） |
| document_type | 文献类型 | 文献类型（期刊/学位论文/会议…） |
| sort_by | 排序 | 相关度 / 发表时间 / 被引 / 下载 |

## sort_by 取值

- relevance（相关度）
- date_desc / date_asc（时间）
- citation_desc（被引降序）
- download_desc（下载降序）

## 注意事项

- 字段名以页面实际可见文本为准；页面 UI 变化时用 FIND_TEXT 定位可见标签。
- 时间过滤优先用 CNKI 的「发表时间」筛选，而不是在检索式里手写年份。
