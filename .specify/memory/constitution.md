<!--
Sync Impact Report:
- Version change: (template) → 1.0.0
- Modified principles: all placeholders replaced with DayDayUp principles
- Added sections: Content & Structure, Development Workflow, Governance (filled)
- Removed sections: none
- Templates: plan-template.md ✅ (Constitution Check uses "Gates determined based on constitution file"); spec-template.md ✅ (no mandatory changes); tasks-template.md ✅ (no principle-driven task type changes); .cursor/commands/* ✅ (no outdated agent references)
- Follow-up TODOs: none
-->

# DayDayUp Constitution

## Core Principles

### I. 信息优先 (Information-First)

所有技能相关内容必须以清晰的结构与元数据组织；每个技能领域必须有明确的范围与用途，禁止仅作为“收纳夹”的无目的分类。

**理由**：项目目标是长期整理各类技能信息，结构先行才能保证可维护与可扩展。

### II. 便于查阅 (Easy Reference)

内容必须可被快速找到（索引、导航或检索）且格式统一可读；导航与发现能力与内容本身同等重要。

**理由**：用户诉求明确为“方便查阅”，查找成本高即违背项目目标。

### III. 可验证技术栈 (Verifiable Tech Stacks)

凡涉及具体技术栈的技能，必须提供可运行的验证方式（脚本、命令或测试），便于本地或 CI 便捷验证环境与用法。

**理由**：用户要求“某些技术栈可以便捷的验证”，未提供验证路径的技术栈条目不视为完成。

### IV. 可持续扩展 (Incremental & Long-Term)

新增与修改均以增量方式进行；整体结构必须支持长期演进，避免为单次需求做大范围推倒重来。

**理由**：定位为长期项目，一次性大改会提高维护成本与出错率。

### V. 简洁优先 (Simplicity)

优先使用简单格式（如 Markdown、YAML）；不引入当前阶段用不到的工具与流程；遵循 YAGNI。

**理由**：个人项目优先保证可持续执行，过度工程会削弱“整理与查阅”的主线。

## Content & Structure

- **格式**：技能说明与清单以 Markdown 为主；结构化元数据可用 YAML。
- **存放**：按技能领域或技术栈分目录存放，每类有明确命名与 README 或索引说明其范围。
- **技术栈验证**：涉及可运行环境的技术栈，其目录下应包含可执行脚本或测试说明（如 `scripts/`、`Makefile` 或 `README` 中的验证步骤）。

## Development Workflow

- **新增技能/技术栈**：先确定归属与索引方式，再按既有结构增量添加；若为新领域，须补充索引或导航入口。
- **涉及可验证技术栈**：新增或变更时须同步更新验证方式（脚本或文档步骤），并确保在文档中说明如何执行验证。
- **合规**：计划与规格中的 Constitution Check 须对照本宪法原则；若有违反须在计划中说明理由或调整方案。

## Governance

- 本宪法优先于项目内其他流程约定；所有与原则冲突的既有约定以宪法为准。
- **修订**：修改宪法须更新本文档、递增版本号（语义化：MAJOR 为不兼容原则删除/重定义，MINOR 为新增原则或章节，PATCH 为措辞与勘误），并更新“Last Amended”日期。
- **合规**：使用 `/speckit.plan` 等命令时，须根据本宪法填写并通过 Constitution Check；未通过且无合理说明的不得进入下一阶段。
- **运行时指引**：具体功能的开发与验证以各 `specs/` 下的 plan、spec、quickstart 等为准，但不得违背本宪法原则。

**Version**: 1.0.0 | **Ratified**: 2026-02-01 | **Last Amended**: 2026-02-01
