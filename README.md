# 自动检索skill（zdjs）

这是一组供 Codex 使用的检索与证据核验 skills。统一入口是 auto-research（显示名：自动检索skill）。完整流程需要安装本仓库的七个 skill。

## 功能

- 单题或事实核验：解析题型、否定措辞与各选项 Claim，选择来源，实际检索并打开原始页面，记录证据并给出带来源的结论。
- 连续在线答题：在已打开的答题页逐题执行读取、检索、证据门控、选择和页面验证；默认停在最终提交前。
- 证据不足、来源冲突或登录受阻时报告实际状态；模型意见不能替代证据。

## 组成

| Skill | 职责 |
| --- | --- |
| auto-research | 统一入口与任务分流 |
| question-router | 题型、极性、陷阱和来源路由 |
| cnki-research | CNKI 文献检索 |
| literacy-research | 信息素养和赛事数据库检索 |
| web-research | 官方与公开网页检索 |
| evidence-judge | 证据门控、协议校验和答案合成 |
| contest-runner | 连续答题状态管理和页面操作编排 |

## 安装

将 skills/ 下的七个目录复制到本机 Codex skills 目录（通常为 ~/.codex/skills/），然后重新加载 skills。Windows PowerShell 示例：

    git clone https://github.com/yuhangzhu295-wq/zdjs.git
    Copy-Item -Path ./zdjs/skills/* -Destination "$HOME/.codex/skills" -Recurse -Force

安装后可在请求中使用 $auto-research。实际联网、浏览器控制与独立子代理是否可用，取决于当前会话的工具和授权；skill 本身是工作流程和辅助脚本，不是独立运行的后台服务。

各目录的 SKILL.md 是入口说明；部分目录还含 references/ 和 scripts/。仓库未包含用户登录凭据或浏览器 Profile。
