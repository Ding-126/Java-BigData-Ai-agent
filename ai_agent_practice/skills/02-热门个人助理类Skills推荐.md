# 02 · 热门个人助理类 Skills 推荐

精选 **15+** 与个人助理、效率、记忆、自动化相关的 Skills 与合集。安装方式因来源而异：Marketplace、复制到 `~/.cursor/skills/`、或启用 Cursor 插件。链接以各项目当前地址为准。

---

## 一、awesome-cursor-skills 精选

来源合集：[spencerpauly/awesome-cursor-skills](https://github.com/spencerpauly/awesome-cursor-skills)

| 名称 | 简介 | 链接 |
|------|------|------|
| saving-workspace-context | 保存当前工作区上下文，便于跨会话恢复项目背景 | https://github.com/spencerpauly/awesome-cursor-skills |
| suggesting-skills | 根据你的用法建议还缺哪些 Skill | https://github.com/spencerpauly/awesome-cursor-skills |
| building-skills-from-patterns | 从重复对话模式提炼并生成新 Skill | https://github.com/spencerpauly/awesome-cursor-skills |

> 上述三项通常在 awesome 仓库的子目录或列表中按名称查找；克隆仓库后复制对应 Skill 文件夹到 `~/.cursor/skills/` 即可。

---

## 二、Cursor 内置 Skills（`~/.cursor/skills-cursor/`，勿改）

通过 `/命令` 或 Agent 自动加载使用，适合日常助理与 IDE 配置。

| 名称 | 简介 | 参考 |
|------|------|------|
| create-skill | 创建新 Agent Skill 的向导与规范 | 对话中输入 `/create-skill` |
| create-rule | 编写 Cursor Rules（持久 AI 偏好） | `/create-rule` |
| update-cursor-settings | 修改 settings.json（主题、格式化等） | 提及改 Cursor 设置时自动相关 |
| loop | 按间隔重复执行提示（如定时检查） | `/loop` |
| automate | 创建 Cursor Automations 工作流 | Automations 相关任务 |

内置说明文档：https://cursor.com/docs/skills

---

## 三、Anthropic 官方 Skills 仓库

合集：[anthropics/skills](https://github.com/anthropics/skills)

| 名称 | 简介 | 链接 |
|------|------|------|
| doc-coauthoring | 协作写文档：大纲、修订、一致语气 | https://github.com/anthropics/skills |
| pdf | PDF 提取、合并、表单等文档处理 | https://github.com/anthropics/skills |
| xlsx | 表格分析、透视、图表与 Excel 工作流 | https://github.com/anthropics/skills |
| pptx | 演示文稿生成与调整 | https://github.com/anthropics/skills |
| skill-creator | 从需求生成符合规范的 Skill 草稿 | https://github.com/anthropics/skills |

适合助理场景：整理发票 PDF、汇总 xlsx 预算、写周报 doc、快速做汇报 pptx。

---

## 四、记忆与表达风格

| 名称 | 简介 | 链接 |
|------|------|------|
| chatcrystal | 对话记忆 / 上下文水晶球类 Skill（社区记忆增强） | 可在 [skills.sh](https://skills.sh) 或 GitHub 搜索 `chatcrystal cursor skill` |
| concise | 中文简洁回答模式，减少冗长输出 | 社区 Skill，常见于 awesome 列表或 skills.sh |

---

## 五、Superpowers 插件 Skills（规划、调试、协作）

安装 **Superpowers** 插件后，可在 Agent 中调用下列技能（与本会话使用的插件同源）。

| 名称 | 简介 |
|------|------|
| brainstorming | 做功能前先澄清需求与方案 |
| writing-plans | 多步骤任务写实现计划 |
| executing-plans | 按计划分阶段执行 |
| systematic-debugging | 遇 bug 先系统排查再改代码 |
| test-driven-development | 先写测试再实现 |
| verification-before-completion | 声称完成前先跑验证命令 |
| using-git-worktrees | 隔离分支开发 |
| finishing-a-development-branch | 功能做完后的合并/PR 选项 |
| requesting-code-review / receiving-code-review | 发起或响应 Code Review |
| dispatching-parallel-agents | 多任务并行子 Agent |
| subagent-driven-development | 按计划拆给子 Agent 执行 |

插件文档：在 Cursor 扩展市场搜索 **Superpowers**。

---

## 六、更多发现渠道

| 合集 / 平台 | 说明 | URL |
|-------------|------|-----|
| awesome-cursor-skills | 社区 curated 列表 | https://github.com/spencerpauly/awesome-cursor-skills |
| anthropics/skills | Anthropic 示例 Skills | https://github.com/anthropics/skills |
| skills.sh | Skills 索引与搜索 | https://skills.sh |
| Cursor Marketplace | 官方/第三方扩展与 Skills | https://cursor.com/marketplace |

---

## 七、个人助理组合示例

1. **Morning brief**：`loop` + 自定义 Skill（读日历/邮件摘要模板）+ `concise` 输出中文简报。  
2. **文档流水线**：`doc-coauthoring` → `pdf` / `pptx` 导出。  
3. **长期项目**：`saving-workspace-context` + 项目内 `.cursor/skills/` 放团队规范。  
4. **少踩坑开发**：Superpowers 的 `brainstorming` → `writing-plans` → `verification-before-completion`。

---

## 八、安装提示（Mac）

1. 克隆或下载 Skill 仓库中的**单个 Skill 目录**（含 `SKILL.md`）。  
2. 复制到 `~/.cursor/skills/<skill-name>/` 或项目 `.cursor/skills/`。  
3. 重启或新开 Agent 对话，用 `/skill-name` 测试。  
4. 勿覆盖 `~/.cursor/skills-cursor/`。

需要自定义助理行为时，优先 **`/create-skill`** 或参考 [01-什么是Skills与如何写好Skill.md](./01-什么是Skills与如何写好Skill.md)。
