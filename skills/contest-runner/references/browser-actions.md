# Browser Actions（抽象动作）

Skill 不假设具体 Agent Harness 的私有 API。所有浏览器操作用以下抽象动作描述，
由最终 Harness 映射到其真实浏览器能力。

## 抽象动作

| 动作 | 语义 |
| --- | --- |
| OPEN_TAB(role) | 打开或定位一个逻辑 Tab |
| SWITCH_TAB(role) | 切换到指定逻辑 Tab |
| NAVIGATE(url) | 导航到 URL |
| READ_PAGE() | 读取当前页面文本/结构 |
| FIND_TEXT(text) | 在页面中定位可见文本 |
| CLICK(target) | 点击元素 |
| FILL(field, value) | 填写输入框 |
| SELECT(field, option) | 选择下拉/选项 |
| SCROLL() | 滚动页面 |
| BACK() | 返回上一页 |
| REFRESH() | 刷新页面 |
| READ_SELECTED_STATE(target) | 读取控件的选中状态 |

## Tab Role（逻辑标签页）

| Role | 用途 |
| --- | --- |
| CONTEST | 答题页面 |
| CNKI | 中国知网 |
| LITERACY | 高校信息素养教育数据库 |
| AI_LITERACY | AI 素养与技能提升数据库 |
| WEB_SEARCH | 搜索引擎/普通网页 |
| TEMP_SOURCE | 临时详情页（用后可关） |

## 复用原则

- 尽量复用已有 Tab，不要每题无限新建 tab。
- TEMP_SOURCE 用于临时打开的结果详情页，读完可关闭。
