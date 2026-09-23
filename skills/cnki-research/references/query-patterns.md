# CNKI Query Patterns

目标：在已登录 CNKI 页面真实操作，读取实时结果。禁止猜数据。

## 支持的检索字段

title / subject / author / institution / keyword / source / year_from / year_to /
document_type / sort_by

## 支持的目标（target）

RESULT_COUNT / TITLE / AUTHOR / COAUTHOR / INSTITUTION / SOURCE / YEAR / DOI /
CITATION_COUNT / DOWNLOAD_COUNT / FUND / KEYWORD / REFERENCE

## 工作流模板

### TITLE_EXACT
篇名字段精确输入 → 检索 → 打开目标文献 → 提取 metadata。

### AUTHOR_SEARCH
作者字段输入 → 检索 → 打开目标文献。

### AUTHOR_YEAR
作者检索 → 限定年份 → 必要时排序 → 打开目标文献。

### SUBJECT_YEAR_RANGE
主题检索 → 设年份范围 → 读取结果。

### RESULT_COUNT
解析检索条件 → 选字段 → 填条件 → 设时间 → 执行检索 → 读取当前结果数量（实时）。

### HIGHEST_CITED
解析作者/年份 → 选字段 → 填作者 → 限年份 → 搜索 → 按被引降序 → 打开第一条 → 提取 metadata。

### DOI_LOOKUP
篇名精确检索 → 打开文献详情 → 查找 DOI。

### COAUTHOR
作者检索 → 年份筛选 → 必要时被引排序 → 打开目标文章 → 读取完整作者列表 →
排除题目指定作者 → 输出 coauthors。

### INSTITUTION / SOURCE / FUND / KEYWORD
对应字段检索 → 打开目标文献 → 提取对应字段值。

### REFERENCE
找到文章 → 打开详情 → 定位参考文献部分 → 提取目标信息。

### CITATION_COUNT / DOWNLOAD_COUNT
定位目标文献详情 → 读取实时被引/下载数值（动态）。

## Query Integrity

每次检索必须记录 `query_plan`（意图）与 `query_executed`（实际浏览器执行），
用 `scripts/validate_query_execution.py` 校验一致性；关键字段不一致 →
QUERY_EXECUTION_MISMATCH，该 Evidence 不得评 A。
