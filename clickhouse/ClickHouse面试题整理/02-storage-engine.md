# ClickHouse 存储引擎与索引面试题 (高级/专家)

## 1. 深入理解 MergeTree 的合并过程 (LSM-Tree 思想)
**标准答案：**
ClickHouse 的 `MergeTree` 借鉴了 LSM-Tree (Log-Structured Merge-Tree) 的思想，但有所不同：
1. **写入流程**：数据先按批次写入磁盘，形成一个个小的 `part`（数据分片）。每个 `part` 内部是有序的。
2. **后台合并 (Merge)**：ClickHouse 会在后台启动线程，将多个小的 `part` 合并成一个大的 `part`。
3. **合并逻辑**：
   - 排序：合并时进行归并排序。
   - 去重/聚合：如果是 `ReplacingMergeTree` 或 `SummingMergeTree`，会在合并阶段执行去重或聚合操作。
4. **优点**：写入时是顺序 IO，极大提高了写入吞吐量。
5. **缺点**：数据不是实时合并的，因此 `ReplacingMergeTree` 的去重具有“滞后性”。

---

## 2. ClickHouse 的二级索引 (Skip Index / Data Skipping Index) 是如何工作的？
**标准答案：**
由于主键索引是稀疏的，ClickHouse 引入了二级索引来进一步加速查询：
1. **原理**：在 `index_granularity` 的基础上，再定义一个更大的粒度（如每 10 个 mark）。
2. **索引类型**：
   - `minmax`：存储该范围内的最小值和最大值。
   - `set(max_rows)`：存储该范围内的去重集合。
   - `bloom_filter`：布隆过滤器，用于快速判断某个值是否**可能**存在。
   - `ngrambf_v1` / `tokenbf_v1`：用于加速字符串模糊匹配（LIKE）。
3. **工作方式**：查询时，先通过二级索引排除掉肯定不包含目标数据的块，减少扫描的 granule 数量。

---

## 3. 为什么 ClickHouse 的主键 (Primary Key) 不需要唯一？
**标准答案：**
这是 ClickHouse 与传统关系型数据库（如 MySQL）最大的区别之一：
1. **设计目标不同**：传统数据库主键是为了唯一标识一行（稠密索引）；ClickHouse 主键是为了**排序**和**建立稀疏索引**。
2. **稀疏索引的要求**：稀疏索引只需要知道数据的排序顺序，以便按块记录范围。它不关心数据是否重复。
3. **去重实现**：如果需要唯一性，应使用 `ReplacingMergeTree` 引擎，并配合后台合并或 `FINAL` 关键字（虽然 `FINAL` 性能较差）。

---

## 4. 解释 ClickHouse 中的 Mark (书签) 文件和数据压缩块的关系
**标准答案：**
ClickHouse 的存储由 `.bin` (压缩数据) 和 `.mrk2` (标记文件) 组成：
1. **.bin 文件**：存储实际列数据，按块压缩。一个压缩块可能包含多个 granule 的数据。
2. **.mrk2 文件**：连接稀疏索引和 `.bin` 文件的桥梁。
   - 记录了每个 granule 在 `.bin` 文件中的偏移量（Offset）。
   - 包含两个偏移量：压缩块在文件中的起始位置，以及解压后数据在块内的起始位置。
3. **查询过程**：
   - 通过 `.idx` (索引) 定位到 mark 编号。
   - 通过 `.mrk2` 找到对应的 `.bin` 文件偏移量。
   - 读取并解压数据。

---

## 5. 如何处理 ClickHouse 中的实时更新和删除？
**标准答案：**
ClickHouse 本质上不支持高效的行级随机更新和删除。常见方案：
1. **Alter Update/Delete (Mutation)**：
   - 语法：`ALTER TABLE ... UPDATE/DELETE`。
   - 原理：重写整个数据零件 (part)，是非常重的操作，异步执行。
   - 场景：适用于大批量、低频次的合规性删除。
2. **ReplacingMergeTree**：
   - 原理：通过版本号或时间戳，在合并时保留最新版本。
   - 场景：最常用的“伪更新”方案。
3. **CollapsingMergeTree / VersionedCollapsingMergeTree**：
   - 原理：通过一个 `sign` 列（1 和 -1）来抵消旧数据。
   - 场景：高性能的流式更新模拟。
4. **外部状态表**：
   - 将经常变动的状态存储在 Redis 或 Dictionary 中，查询时通过 `join` 或 `dictGet` 获取。
