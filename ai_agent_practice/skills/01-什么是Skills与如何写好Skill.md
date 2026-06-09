# 01 · 什么是 Skills，以及如何写好 Skill

## Cursor Agent Skills 是什么？

**Skills** 是放在 Cursor 里的「可复用说明书」：用 Markdown（`SKILL.md`）教 Agent **何时**、**如何**完成某类任务——例如按团队规范做 Code Review、生成固定格式的 commit message、查询内部数据库约定、或走一遍你常用的个人助理流程。

与一次性在对话里口头说明相比，Skill 可以：

- 跨项目复用（个人 Skill）或随仓库共享（项目 Skill）
- 通过描述（description）让 Agent 在合适场景自动选用
- 用 `/skill-name` 或 `@skill` 显式调用，行为更稳定

官方文档：https://cursor.com/docs/skills  
开放规范参考：https://agentskills.io

---

## SKILL.md 基本格式

每个 Skill 是一个**文件夹**，其中必须包含 `SKILL.md`：

```
my-skill/
├── SKILL.md          # 必需
├── reference.md      # 可选：长文档
├── examples.md       # 可选：示例
└── scripts/          # 可选：辅助脚本
```

### YAML  frontmatter（文件头）

```markdown
---
name: my-skill-name
description: 用第三人称写清楚「做什么」和「何时用」，便于 Agent 发现。
disable-model-invocation: true
---

# Skill 标题

正文：分步骤说明、约束、示例……
```

| 字段 | 说明 |
|------|------|
| `name` | 最多 64 字符，小写字母、数字、连字符 |
| `description` | 最多 1024 字符，**最关键**：写清能力 + 触发场景 |
| `disable-model-invocation` | 为 `true` 时通常仅在用户显式调用时加载；若希望 Agent 自动选用，可省略或设为 false |
| `paths`（若使用） | 限制 Skill 仅在匹配路径下生效（按 Cursor 版本与文档为准） |

---

## 存放位置

| 类型 | 路径 | 范围 |
|------|------|------|
| 项目 Skill | `.cursor/skills/<skill-name>/` | 当前仓库协作者可共享 |
| 个人 Skill | `~/.cursor/skills/<skill-name>/` | 本机所有项目可用 |
| Cursor 内置 | `~/.cursor/skills-cursor/` | **系统管理，请勿手动修改** |

---

## 如何调用 Skill

| 方式 | 说明 |
|------|------|
| `/skill-name` | 在聊天输入框用斜杠命令（名称以 Skill 的 `name` 为准） |
| `@skill` | 在输入中 @ 引用 Skill |
| `/create-skill` | 使用 Cursor 内置「创建 Skill」向导（见内置 create-skill Skill） |
| 自动发现 | description 写得好时，Agent 会在相关任务中主动读取该 Skill |

---

## 写好 Skill 的最佳实践（摘要）

以下整理自 Cursor 内置 **create-skill** 指南与社区经验：

### 1. 先想清楚再写

- **目的与范围**：这一条 Skill 只解决一件事还是一条流水线？
- **存放位置**：个人通用 vs 项目专用？
- **触发场景**：用户说什么话、做什么文件操作时应启用？
- **领域知识**：Agent 默认不知道的内部规范、API、命名约定。
- **输出格式**：是否需要固定模板（表格、清单、中文/英文）？

### 2. description 是「搜索引擎」

- 用**第三人称**（「处理 Excel 并生成报表」），避免「我可以帮你…」
- 同时写 **WHAT**（能力）和 **WHEN**（触发词、文件类型、任务类型）
- 要具体：提到 PDF、xlsx、PR review、commit message 等关键词

### 3. 正文要精简

上下文窗口有限；Agent 本身很聪明，只写**它不知道的**步骤与约束。  
删掉泛泛的编程教程，保留：命令、路径、检查清单、反例。

### 4. 用户原文要原样保留

若用户提供了必须使用的措辞或模板，在 Skill 里** verbatim** 使用，不要擅自改写。

### 5. 不要动内置目录

切勿在 `~/.cursor/skills-cursor/` 里创建或修改 Skill；用 `~/.cursor/skills/` 或 `.cursor/skills/`。

### 6. 可选脚本

复杂校验可放 `scripts/`，但在 Skill 正文里写清何时运行、需要什么环境。

---

## 创建新 Skill 的快捷路径

1. 在 Cursor 对话中运行 **`/create-skill`**，按向导填写。
2. 或手动：`mkdir -p ~/.cursor/skills/my-skill` → 编辑 `SKILL.md` → 用 `/my-skill` 试跑。
3. 改 description 后多试几种用户说法，看 Agent 是否会自动选用。

---

## 下一步

浏览 [02-热门个人助理类Skills推荐.md](./02-热门个人助理类Skills推荐.md)，安装或参考社区 Skill，加速搭建个人助理工作流。
