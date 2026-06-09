# 01 · 快速了解 Hermes Agent

## Hermes Agent 是什么？

**Hermes Agent** 是 [Nous Research](https://nousresearch.com) 开源的**自主 AI 智能体（Autonomous AI Agent）**。它不仅能像 ChatGPT 一样对话，还能在本地或服务器上**持续运行**、**记住上下文**、**调用工具**（搜索、代码、文件、消息平台等），并可通过「技能（Skills）」不断扩展能力。

你可以把它理解为：**带长期记忆和工具箱的个人 AI 助理**，适合自动化日常事务、研究、编程辅助与消息渠道上的远程指挥。

## 官方链接

| 资源 | 链接 |
|------|------|
| 官网 | https://hermes-agent.nousresearch.com |
| 备用站点 | https://hermes-agent.org |
| GitHub 源码 | https://github.com/NousResearch/hermes-agent |
| 官方文档 | https://hermes-agent.nousresearch.com/docs |
| 社区 Discord | https://discord.gg/NousResearch |

## 核心概念（用大白话）

### 1. 持久记忆（Persistent Memory）

Agent 会把重要信息写入本地存储，跨会话仍能「记得」你的偏好、项目背景、常用联系人说明等，而不是每次对话从零开始。

### 2. 自改进技能（Self-improving Skills）

Hermes 支持以 **Skill** 形式封装工作流（例如：每周摘要、固定格式的邮件草稿、某类研究步骤）。你可以新增、修改技能，让 Agent 越用越贴合你的习惯。

### 3. Gateway（消息网关）

**Gateway** 把 Hermes 接到 **Telegram、Discord、Slack** 等 IM。你在手机上发消息，家里的 Mac 或服务器上的 Agent 就能执行并回复——相当于「远程助理控制台」。

### 4. CLI 终端对话

在 Mac 终端运行 `hermes` 即可进入交互式聊天，适合本地快速任务、调试配置、不依赖 IM 的场景。

## 适合当「个人助理」的典型场景

- **日程与提醒**：通过 Gateway 在 Telegram/Slack 里下达「明天提醒我买…」类指令（具体能力取决于你配置的工具与模型）。
- **信息整理**：让 Agent 根据记忆里的项目背景，整理笔记、对比方案、生成待办清单。
- **研究与阅读**：联网搜索 + 长文摘要，结果写入记忆供下次引用。
- **开发辅助**：在终端里解释代码、跑脚本、对接 Git（需正确配置工具与权限）。
- **多渠道统一入口**：同一套 Hermes 实例，CLI 深度工作 + IM 轻量指令。

## 和 Cursor 的关系

- **Cursor** 侧重 IDE 里的编码 Agent 与 **Cursor Skills**（见本仓库 `skills/` 目录）。
- **Hermes Agent** 是独立产品，可在系统级、消息渠道运行，两者可并存：例如 Cursor 写代码，Hermes 在 Slack 里做日常助理。

## 下一步

请阅读 [02-Mac安装配置与日常维护.md](./02-Mac安装配置与日常维护.md)，按步骤在 Mac 上安装并完成首次 `hermes setup`。
