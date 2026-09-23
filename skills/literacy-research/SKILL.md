---
name: literacy-research
description: >-
  当题目涉及高校信息素养教育数据库、AI 素养与技能提升数据库、或比赛学练测资源
  （信息素养、检索原理、信息检索系统、AI 工具、AIGC、AI 产品功能等）时使用。
  优先使用赛事指定数据库的站内检索/分类导航获取 Evidence，而不是看到「AI 工具」就直接
  Web 搜索。不处理 CNKI 检索与普通网页检索。
---

# Purpose

在赛事指定的信息素养/AI素养数据库与学练测平台中检索并提取 Evidence。

# When to Use

- 路由为 `LITERACY_DB` 或 `AI_LITERACY_DB` 的题目。

# When NOT to Use

- CNKI 检索 → cnki-research。
- 指定数据库找不到后才扩展到产品官网 / 官方 Web / 普通 Web。

# Inputs

- 题目关键词与 search_targets（来自 question-router）。

# Required Context

- 用户已登录相应数据库（登录态由 Harness 维护）。
- 可用资源见 `references/sites.md`。

# Workflow

1. 识别关键词 → 打开/切换到正确数据库（`LITERACY` 或 `AI_LITERACY` Tab）。
2. 使用站内检索或分类导航定位课程/知识点/工具说明。
3. 打开正文，阅读实际内容。
4. 按 `references/search-strategy.md` 提取 Evidence。

# Evidence Rules

- 赛事数据库有明确答案时，优先赛事数据库。
- 证据类型用 PRIMARY_DATABASE；来源标注具体数据库。

# Browser Rules

- 使用抽象动作：SWITCH_TAB / FIND_TEXT / NAVIGATE / READ_PAGE。
- 复用 `LITERACY` / `AI_LITERACY` Tab。
- 不要优先搜索博客。

# Failure Handling

- 站内无结果 → reformulate query 或换分类导航。
- 数据库找不到 → 才转产品官网/官方Web/普通Web，并如实标注来源。
- session 失效 → LOGIN_REQUIRED。

# Stop Conditions

- LOGIN_REQUIRED → 暂停，请求人工处理。

# Expected Output

- 一条或多条 Evidence（PRIMARY_DATABASE）。

# Security Rules

- 不在 references/sites.md 保存账号密码。
