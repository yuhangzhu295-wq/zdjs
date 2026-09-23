# Routing Rules（question-router）

Router 只决定去哪找事实，不回答题目。

## 关键词 → 路由

### CNKI
中国知网、CNKI、知网、作者、篇名、主题、关键词、文献、期刊、论文、学位论文、
基金、机构、来源、DOI、被引、下载、参考文献、高级检索、专业检索

### LITERACY_DB
高校信息素养教育数据库、信息素养、检索原理、信息检索系统、信息检索、检索语言、
布尔检索、截词检索

### AI_LITERACY_DB
AI素养与技能提升数据库、AI素养、AI工具、AIGC、人工智能工具、AI产品功能、
大语言模型、提示词

### OFFICIAL_WEB
国务院、教育部、政府、法规、条例、国家标准、政策、规范、办法

### PRODUCT_OFFICIAL
当前功能、支持模型、菜单、产品能力（且标记 dynamic）

### FORMAL_REASONING
推理、逻辑关系、必然推出、演绎、三段论（且无检索线索）

## 决策顺序

1. 唯一命中 → 该路由。
2. 多类命中 → MULTI_SOURCE。
3. 无命中且含推理标志词 → FORMAL_REASONING。
4. 其余无命中 → GENERAL_WEB。

## 输出

```json
{
  "question_type": "...",
  "polarity": "...",
  "dynamic": true,
  "traps": [],
  "route": "CNKI",
  "claims": ["claim_A", "..."],
  "search_targets": []
}
```
