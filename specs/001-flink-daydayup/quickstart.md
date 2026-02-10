# Quickstart: 如何查阅 Flink 面试点整理

**Feature**: 001-flink-daydayup | **Phase**: 1

## 1. 本目录是什么

本目录为 **Flink 面试点整理**，面向约 **60k 岗位** 的面试官与候选人：系统化面试题 + 详细答案，按模块分文件，便于查阅与循序渐进学习。

## 2. 从哪里开始

- **总览**: 打开 [Flink/README.md](./Flink/README.md)，查看文件列表与推荐阅读顺序；新读者可在约 5 分钟内理解整体结构。
- **按模块看**: 直接打开 Flink 目录下对应模块文件，例如：
  - 架构与基础 → [Flink/01-architecture.md](./Flink/01-architecture.md)
  - API 与编程模型 → [Flink/02-api.md](./Flink/02-api.md)
  - 状态与容错 → [Flink/03-state-fault-tolerance.md](./Flink/03-state-fault-tolerance.md)
  - 性能与调优 → [Flink/04-performance.md](./Flink/04-performance.md)
  - 生产与运维 → [Flink/05-production.md](./Flink/05-production.md)
- **按难度复习**: 各文件中题目标有 `[基础]` / `[进阶]` / `[生产]` 时，可先扫一遍基础题再进入进阶与生产题。

## 3. 推荐阅读顺序

- **按模块顺序（适合系统复习）**: 01 → 02 → 03 → 04 → 05。
- **按“基础→进阶→生产”（适合分层刷题）**: 先读各文件中标为 [基础] 的题，再 [进阶]，最后 [生产]。

## 4. 版本与约定

- 答案以 **Apache Flink 1.17** 为主；若某题涉及版本差异，会在答案中单独标明。
- 题目难度标注仅为参考，便于面试官选题与候选人按档位复习。

## 5. 规划与设计文档（供协作者参考）

- 需求与验收: [spec.md](./spec.md)
- 实现计划: [plan.md](./plan.md)
- 研究与决策: [research.md](./research.md)
- 内容结构约定: [data-model.md](./data-model.md)、[contracts/content-structure.md](./contracts/content-structure.md)
