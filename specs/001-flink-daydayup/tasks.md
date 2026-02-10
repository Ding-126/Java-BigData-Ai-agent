# Tasks: Flink 面试点整理（60k 岗位面试官视角）

**Input**: Design documents from `specs/001-flink-daydayup/`  
**Prerequisites**: plan.md, spec.md, research.md, data-model.md, contracts/

**交付目录**: 最终的整理文件（README + 五模块面试题与答案）均放在 **Flink** 目录下：`specs/001-flink-daydayup/Flink/`

**Organization**: 按用户故事分阶段；无自动化测试任务（spec 未要求 TDD）。

## Format: `[ID] [P?] [Story?] Description with file path`

- **[P]**: 可并行（不同文件、无依赖）
- **[Story]**: 所属用户故事（US1/US2/US3）
- 所有路径均相对于仓库根或明确写出 `specs/001-flink-daydayup/Flink/`

## Path Conventions

- **内容根目录**: `specs/001-flink-daydayup/Flink/`（即“Flink 目录”）
- **规划/设计文档**: `specs/001-flink-daydayup/`（spec.md, plan.md, research.md, data-model.md, quickstart.md, contracts/）

---

## Phase 1: Setup（共享基础设施）

**Purpose**: 创建 Flink 目录，确保最终整理文件统一放在该目录下

- [x] T001 Create Flink directory at specs/001-flink-daydayup/Flink/

---

## Phase 2: Foundational（阻塞性前置）

**Purpose**: 总览与索引必须先存在，后续模块文件才能被查阅者通过 README 在 2 分钟内定位

**⚠️ CRITICAL**: 未完成本阶段前不开始各模块内容编写

- [x] T002 Create README.md in specs/001-flink-daydayup/Flink/ with 本目录用途、文件列表（5 个模块文件链接）、推荐阅读顺序（01→05 与 基础→进阶→生产）、版本与约定（答案以 Flink 1.17 为主、难度标注含义），符合 contracts/content-structure.md

**Checkpoint**: README 就绪后，可按模块并行编写内容

---

## Phase 3: User Story 1 - 系统化面试题覆盖（Priority: P1）🎯 MVP

**Goal**: 在 Flink 目录下产出 5 个模块文件，每模块至少 3 道面试题（60k 岗位面试官视角），覆盖架构、API、状态与容错、性能调优、生产与运维

**Independent Test**: 查阅者打开 Flink/README 后能在 2 分钟内找到任意模块对应文件；每个模块文件内至少有 3 道题且题面清晰

### Implementation for User Story 1

- [x] T003 [P] [US1] Create specs/001-flink-daydayup/Flink/01-architecture.md with 一级标题「架构与基础」、至少 3 道面试题（题面为二级标题，可标 [基础]/[进阶]/[生产]），答案可先留空或占位
- [x] T004 [P] [US1] Create specs/001-flink-daydayup/Flink/02-api.md with 一级标题「API 与编程模型」、至少 3 道面试题（同上）
- [x] T005 [P] [US1] Create specs/001-flink-daydayup/Flink/03-state-fault-tolerance.md with 一级标题「状态与容错」、至少 3 道面试题（同上）
- [x] T006 [P] [US1] Create specs/001-flink-daydayup/Flink/04-performance.md with 一级标题「性能与调优」、至少 3 道面试题（同上）
- [x] T007 [P] [US1] Create specs/001-flink-daydayup/Flink/05-production.md with 一级标题「生产与运维」、至少 3 道面试题（同上）

**Checkpoint**: 五个模块文件均存在且每题有题面；可独立验证“按模块找到面试题列表”

---

## Phase 4: User Story 2 - 每题配有详细答案（Priority: P2）

**Goal**: 为 Flink 目录下每个模块文件中的每道题补充详细答案，条理清晰、可独立理解，含原理或选型理由；涉及版本时标明

**Independent Test**: 任选一道题，其答案完整可读、无需外部资料即可理解题意与答案要点

### Implementation for User Story 2

- [x] T008 [US2] Add detailed answers to all questions in specs/001-flink-daydayup/Flink/01-architecture.md（答案紧跟题面、可含小标题/列表；涉及版本处标「适用版本：1.17」等）
- [x] T009 [US2] Add detailed answers to all questions in specs/001-flink-daydayup/Flink/02-api.md
- [x] T010 [US2] Add detailed answers to all questions in specs/001-flink-daydayup/Flink/03-state-fault-tolerance.md
- [x] T011 [US2] Add detailed answers to all questions in specs/001-flink-daydayup/Flink/04-performance.md
- [x] T012 [US2] Add detailed answers to all questions in specs/001-flink-daydayup/Flink/05-production.md

**Checkpoint**: 每题均有详细答案；可随机抽 10 题验证 90% 以上可独立理解（SC-003）

---

## Phase 5: User Story 3 - 多文件组织便于导航与渐进学习（Priority: P3）

**Goal**: 确保通过 README 与模块文件结构，查阅者能在 2 分钟内定位到任意模块或题目，且推荐阅读顺序明确

**Independent Test**: 新读者打开 Flink/README 后 5 分钟内理解整体结构；按“状态与容错”或“基础→进阶→生产”路径可快速找到对应文件

### Implementation for User Story 3

- [x] T013 [US3] Verify and update specs/001-flink-daydayup/Flink/README.md：文件列表包含 01–05 五个模块文件及中文模块名、推荐阅读顺序（按模块 01→05 与 按难度 基础→进阶→生产）清晰可读
- [x] T014 [P] [US3] Add difficulty labels [基础]/[进阶]/[生产] to questions in specs/001-flink-daydayup/Flink/01-architecture.md, 02-api.md, 03-state-fault-tolerance.md, 04-performance.md, 05-production.md where not yet present（便于面试官选题与候选人按档位复习）

**Checkpoint**: README 与各文件满足 SC-001、SC-004；多文件组织一致

---

## Phase 6: Polish & Cross-Cutting Concerns

**Purpose**: 与规划文档的衔接、版本与交叉引用

- [x] T015 Update specs/001-flink-daydayup/quickstart.md：将「从哪里开始」「按模块看」等链接指向 specs/001-flink-daydayup/Flink/README.md 及 Flink/ 下各模块文件路径
- [x] T016 Review all answers in specs/001-flink-daydayup/Flink/*.md for version-specific content；在涉及 Flink 版本或配置差异的答案中补充「适用版本：1.17」或「1.17 与 1.13 差异：…」（FR-005）

---

## Dependencies & Execution Order

### Phase Dependencies

- **Phase 1 (Setup)**: 无依赖，可立即执行
- **Phase 2 (Foundational)**: 依赖 Phase 1；完成后方可开始 Phase 3
- **Phase 3 (US1)**: 依赖 Phase 2；T003–T007 可并行
- **Phase 4 (US2)**: 依赖 Phase 3；T008–T012 可按文件顺序或并行（不同文件）
- **Phase 5 (US3)**: 依赖 Phase 3（README 可依赖 Phase 2 已有 README）；T014 可与 T013 并行
- **Phase 6 (Polish)**: 依赖 Phase 4、Phase 5 完成

### User Story Dependencies

- **US1**: 在 Foundational 完成后即可实施；产出为 5 个模块文件及题面
- **US2**: 依赖 US1 产出；为每题补全答案
- **US3**: README 验证/更新依赖 Phase 2；难度标注可随 US1/US2 一并完成，或在本阶段补全

### Parallel Opportunities

- T003–T007（五个模块文件创建）可并行
- T008–T012（五个模块答案填写）可并行（不同文件）
- T014 可与 T013 并行

---

## Implementation Strategy

### MVP First（仅完成 US1）

1. 完成 Phase 1 + Phase 2
2. 完成 Phase 3（五个模块文件 + 至少各 3 题）
3. **STOP & VALIDATE**：按模块能找到面试题列表、README 可 2 分钟内定位
4. 若需“先有题再补答案”，可在此交付 MVP（仅有题、答案占位）

### Incremental Delivery

1. Phase 1 + 2 → README 与 Flink 目录就绪
2. Phase 3 → 五模块题面就绪（MVP）
3. Phase 4 → 每题详细答案就绪（完整内容）
4. Phase 5 → 导航与难度标注完善
5. Phase 6 → 与 quickstart、版本标注对齐

### Parallel Execution Example（Phase 3）

```text
# 可同时进行：
T003 Create 01-architecture.md in Flink/
T004 Create 02-api.md in Flink/
T005 Create 03-state-fault-tolerance.md in Flink/
T006 Create 04-performance.md in Flink/
T007 Create 05-production.md in Flink/
```

---

## Notes

- 所有**最终整理文件**（README + 01–05 模块 md）均位于 **specs/001-flink-daydayup/Flink/**，满足用户要求“放在 Flink 目录下”且仍在 001-flink-daydayup 交付范围内（FR-006）。
- [P] 表示该任务可与同阶段其他 [P] 任务并行；[USn] 表示归属第 n 个用户故事。
- 每题须有详细答案（FR-002）；版本差异须标明（FR-005）；总览与索引满足 SC-001、SC-004。
