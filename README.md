# 自动检索skill（zdjs）

本仓库同时包含 Codex skills 和信息素养 Research Agent 应用。统一 skill 入口为 auto-research，显示名“自动检索skill”。七个 skill 位于 skills/，应用的 FastAPI 后端位于 backend/，React 前端位于 frontend/，测试位于 tests/。

## 功能

- 单题或事实核验：解析题型、否定措辞与各选项 Claim，选择来源，检索并打开页面，记录证据并给出带来源的结论。
- 连续在线答题：contest-runner 描述逐题读取、检索、证据门控、选择和页面验证的流程，默认停在最终提交前。
- 证据不足、来源冲突或登录受阻时报告实际状态；模型意见不能替代证据。

## Skill 安装

将 skills/ 下的七个目录复制到 Codex skills 目录（通常为 ~/.codex/skills/），然后重新加载 skills。Windows PowerShell 示例：

    git clone https://github.com/yuhangzhu295-wq/zdjs.git
    Copy-Item -Path ./zdjs/skills/* -Destination "$HOME/.codex/skills" -Recurse -Force

安装后可使用 $auto-research。其余六个目录分别负责题目路由、CNKI 检索、素养库检索、网页检索、证据判断和连续答题编排。

## 本地运行应用

需要 Python 3.11+ 和 Node.js。以下命令从仓库根目录执行：

    python -m pip install -r backend/requirements.txt
    python -m uvicorn app.main:app --app-dir backend --port 8001

另开终端启动前端：

    cd frontend
    npm ci
    npm run dev

打开 http://localhost:5173。后端测试使用 python -m pytest -q。

当前独立运行的 API 使用 local_evidence_only 模式。backend/app/codex_bridge.py 定义了 CodexRoleRunner 接口，但仓库尚未提供实际连接 Codex 桌面子代理的适配器；因此独立 API 运行时不会真实启动三个 Codex 子代理。联网检索和受保护来源的访问取决于当前网络、浏览器工具与用户登录状态。CNKI 动态数据需要已登录会话；系统不会保存账号密码或绕过验证码。项目 Playwright MCP 配置位于 .codex/config.toml，供应商密钥只从环境变量读取，示例见 .env.example。

## 仓库边界

未上传本地浏览器 Profile、密钥、安装依赖、构建产物，以及 ChatGPT 项目同步的 sources/ 参考 PDF。PDF 是只读的项目资料，不是运行本应用所需的源码。
