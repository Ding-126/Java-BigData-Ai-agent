# ClickHouse 高可用与集群运维面试题 (高级/专家)

## 1. ClickHouse 的副本 (Replication) 机制是如何实现的？
**标准答案：**
ClickHouse 的副本机制不依赖于表引擎本身，而是通过 `ReplicatedMergeTree` 系列引擎实现：
1. **依赖 ZooKeeper**：所有的副本协调（如日志复制、选主、合并任务分发）都通过 ZooKeeper 完成。
2. **多主架构 (Multi-Master)**：任何一个副本都可以接收写入。写入后，该副本会将操作日志（Log）写入 ZooKeeper。
3. **异步拉取**：其他副本监听到 ZooKeeper 的变化后，会从源副本拉取数据零件 (part)。
4. **数据一致性**：通过校验和（Checksum）确保副本间数据一致。

---

## 2. ClickHouse 集群如何实现横向扩展 (Sharding)？
**标准答案：**
1. **分片 (Shard)**：将数据分布在不同的节点上。
2. **Distributed 引擎**：
   - 逻辑表，不存储数据。
   - 写入时：根据 `sharding_key` 将数据转发到对应分片。
   - 查询时：将查询分发到所有分片，并汇总结果（分布式聚合）。
3. **扩容流程**：
   - 增加新节点。
   - 修改配置文件中的 `remote_servers`。
   - 存量数据迁移：ClickHouse 不会自动重平衡数据，通常需要手动移动分区或使用 `clickhouse-copier` 工具。

---

## 3. ZooKeeper 在 ClickHouse 集群中的角色是什么？如果 ZooKeeper 挂了会怎样？
**标准答案：**
1. **角色**：
   - 存储副本操作日志。
   - 副本间的数据同步协调。
   - `ReplicatedMergeTree` 的选主（Leader Election）。
   - 分布式 DDL 执行。
2. **故障影响**：
   - **查询不受影响**：如果只是查询，不经过 ZooKeeper。
   - **写入受限**：无法写入 `ReplicatedMergeTree` 表（因为无法记录日志），但可以写入非副本表。
   - **合并停止**：后台合并任务无法协调，会导致 part 堆积。
   - **元数据只读**：无法执行 `CREATE/DROP/ALTER` 等分布式 DDL。
3. **替代方案**：ClickHouse 官方已推出 `Keeper`（C++ 实现），兼容 ZK 协议，性能更好且无需 Java 运行时。

---

## 4. 如何处理 ClickHouse 的“Too many parts”错误？
**标准答案：**
这是 ClickHouse 运维中最常见的错误，通常意味着后台合并速度跟不上写入速度。
1. **根本原因**：
   - 写入批次太小，频率太高。
   - 分区键粒度太细（如按秒分区），导致产生大量分区。
2. **解决方法**：
   - **客户端优化**：增大写入 Batch Size，降低写入频率。
   - **配置调整**：适当调大 `parts_to_throw_insert` 阈值（默认 300）。
   - **硬件优化**：提高磁盘 IOPS（换 SSD）。
   - **架构优化**：检查分区键，确保单个表的分区总数不要过多。

---

## 5. ClickHouse 的监控体系应该关注哪些核心指标？
**标准答案：**
1. **查询性能**：
   - `Query Duration`：查询耗时 P99。
   - `Queries per second (QPS)`。
2. **系统资源**：
   - `CPU Usage`：ClickHouse 是 CPU 密集型。
   - `Memory Usage`：防止 OOM。
   - `Disk IOPS & Throughput`。
3. **ClickHouse 特有指标**：
   - `Parts count`：每个表的数据零件数，预警 "Too many parts"。
   - `Replication queue size`：副本同步队列长度，判断同步延迟。
   - `ZooKeeper exceptions`：ZK 连接异常。
   - `Inserted rows/bytes`：写入吞吐量。
