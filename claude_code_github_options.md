# Claude Code 翻译与美化候选（只读检索）

检索时间：2026-10-24

## 中文翻译 / 本地化

1. [Dublin1231/polished-localization-for-claude-code](https://github.com/Dublin1231/polished-localization-for-claude-code)
   - MIT；面向 Claude Code 的中文界面本地化、工具提示和任务完成通知。
   - README 明确支持 Windows/macOS/Linux；界面汉化走 npm，Hook 可 npm 或手动安装。
   - 适合先做中文体验试用。项目规模较小，安装前应检查与当前 2.1.310 的兼容性及回滚方式。

2. [xu-xiang/everything-claude-code-zh](https://github.com/xu-xiang/everything-claude-code-zh)
   - 中文翻译版的 Everything Claude Code 工具包（Skills、Agents、Hooks、Commands、Rules 等）。
   - README 标示 MIT，约 2K stars（检索时）；它主要是工作流/配置资源中文化，不是 Claude Code 主界面汉化。

## 终端美化 / 状态栏

1. [sirmalloc/ccstatusline](https://github.com/sirmalloc/ccstatusline)
   - 约 13K stars（检索时），MIT；可显示模型、Git 分支、token 使用量等。
   - README 有 Windows 支持和配置文档，适合先试用，侵入性相对低。

2. [Nanako0129/coralline](https://github.com/Nanako0129/coralline)
   - 约 549 stars；MIT；10 套主题、3 种布局、子智能体面板、5 小时/7 天限额预测。
   - 提供 Windows 原生 PowerShell 渲染器；README 标明本地运行、无网络和 API 调用。

3. [hellosverre/claude-skins](https://github.com/hellosverre/claude-skins)
   - 约 197 stars；MIT；16 套 skins、工具调用图标和卡片式输出。
   - README 要求 Claude Code 2.1.287+，与当前 2.1.310 版本线匹配；通过插件市场安装。

4. [Piebald-AI/tweakcc](https://github.com/Piebald-AI/tweakcc)
   - 约 2.5K stars；可自定义系统提示、主题、工具集和 UI。
   - 功能最强但改动面最大，可能对 Claude Code 内部行为和升级产生影响，建议先备份、在测试配置中试用。

## 建议顺序

先只试 `ccstatusline` 或 `coralline` 做状态栏美化；中文化再评估 `polished-localization-for-claude-code`。不要同时安装多个会改写 UI、Hook 或系统提示的项目。任何第三方插件安装前应先确认版本兼容、许可证、安装脚本和卸载步骤。

本文件先记录检索结果；本次执行结果见下方。

## 本次执行结果（2026-10-24）

- 已安装 `ccstatusline` 2.2.32，并写入 Claude Code `settings.json` 的 `statusLine.command = "ccstatusline"`，刷新间隔 10 秒；命令已用示例输入验证可运行。
- 已安装 `polished-localization-for-claude-code` 0.4.0 的中文工具提示 Hook，Git Bash 验证通过。
- 该包的“界面汉化”脚本要求旧式 `cli.js`，当前 Claude Code 2.1.310 使用原生 `bin/claude.exe`，因此没有强行修改二进制；界面英文替换未生效，工具提示中文化已生效。
- `coralline` 未同时安装，以免与 ccstatusline 竞争同一个 `statusLine` 配置；如需切换，先卸载/移除 ccstatusline 配置再安装 coralline。

