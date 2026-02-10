# 状态与容错

## Q1 [基础] Flink 有哪几类状态？状态后端（State Backend）有哪些可选，分别适用什么场景？

**答案**

**是什么**  
**状态分类**  
- **Keyed State**：与 key 绑定，仅可在 `KeyedStream` 的算子内使用；类型有 ValueState、ListState、MapState、ReducingState、AggregatingState。  
- **Operator State**：与算子实例绑定（如 Source 的 offset）；类型有 ListState、UnionListState；常用于 Source/Sink 的 offset 或自定义缓冲。  
- **Broadcast State**：广播流上的状态，所有并行实例共享同一份逻辑状态。

**状态后端**  
- **HashMapStateBackend**：状态在 JVM 堆上，快但受 TM 内存限制；适合状态小、无大状态或测试。  
- **EmbeddedRocksDBStateBackend**：状态主要在 RocksDB（磁盘/本地），可支持大状态、增量 Checkpoint；单 key 访问比堆慢，适合大状态、长窗口。  
- **生产常用**：大状态、长窗口用 RocksDB；小状态、低延迟可考虑 HashMap（需控制 TM 内存）。

**为什么这样设计**  
- **状态分类**：Keyed State 按 key 隔离，便于并行处理与状态管理；Operator State 与算子实例绑定，适合 Source/Sink 的 offset。  
- **状态后端**：HashMap 快但受内存限制；RocksDB 支持大状态但访问慢；按状态规模选择。

**适用版本**：1.17；RocksDB 增量 Checkpoint 在 1.15+ 成熟。

---

## Q2 [进阶] Checkpoint 和 Savepoint 的区别？Exactly-Once 语义在 Flink 里是如何实现的？

**答案**

**是什么**  
**Checkpoint vs Savepoint**  
- **Checkpoint**：由 Flink 自动、周期性触发的快照，用于故障恢复；可配置间隔、超时、是否增量等；一般存到 HDFS/S3 等，作业取消后通常可删。  
- **Savepoint**：用户主动触发的快照，格式与 Checkpoint 兼容但偏向「版本保留、升级、A/B 测试」；恢复时可改并行度、改图（需兼容）；生产上常用于发布前打点、升级前后回滚。

**Exactly-Once 实现**  
- **端到端**：需要 Source 可重放 + Flink 内部 Exactly-Once + Sink 幂等或事务。  
- **Flink 内部**：  
  - **Chandy-Lamport 分布式快照**：JM 向 Source 注入 barrier，barrier 随流向下游传播；算子收到某 checkpoint 的 barrier 时对本状态做快照、再转发 barrier；所有算子快照一致对齐到同一逻辑时间点。  
  - **Sink 端**：两阶段提交（2PC）或幂等写；如 Kafka 用 FlinkKafkaProducer 的「事务 + 预提交」，Checkpoint 成功时 commit，否则 abort 重放。

**为什么这样设计**  
- **Checkpoint vs Savepoint**：Checkpoint 自动、频繁，用于快速恢复；Savepoint 手动、持久，用于版本管理；格式兼容便于统一恢复逻辑。  
- **Chandy-Lamport**：分布式快照算法，保证所有算子快照一致对齐；barrier 传播保证时间点一致。

**适用版本**：1.17；Kafka 两阶段 Sink 在 1.4+ 支持，行为稳定。

---

## Q3 [生产] 状态变大或 Checkpoint 变慢怎么办？如何做状态迁移与作业升级？

**答案**

**状态变大 / Checkpoint 慢**  
- **增量 Checkpoint**（RocksDB）：只持久化上次以来的增量，减少 IO 与时长；大状态必开。  
- **调大 Checkpoint 间隔**：在可接受恢复进度范围内适当拉长。  
- **调大超时、并行度**：避免 barrier 迟迟对齐不了；适当提高 TM 数或 Slot 数。  
- **RocksDB 调优**：block cache、write buffer、本地目录用 SSD 等；减少大 key、大 value 或超大 MapState。  
- **状态 TTL**：对可过期的状态开 TTL，减少体积与扫描成本。

**状态迁移与作业升级**  
- **同版本/兼容改图**：直接 Savepoint，停止旧作业，从 Savepoint 恢复新作业（可改并行度等）。  
- **Flink 版本升级**：用 Savepoint 做「停机迁移」：旧版本打 Savepoint → 新版本从该 Savepoint 恢复；需保证状态格式兼容（同大版本内一般兼容，跨大版本需看发布说明）。  
- **状态迁移工具**：若有 schema 或目录变更，可配合自定义迁移逻辑或 Flink 提供的状态迁移能力（视版本而定）。

**为什么这样优化**  
- **增量 Checkpoint**：只写增量，减少 IO；但需维护增量链，恢复时需合并增量。  
- **状态迁移**：Savepoint 格式兼容，便于版本升级；但需保证状态格式兼容，否则需迁移。

**适用版本**：1.17；RocksDB 增量 Checkpoint、Savepoint 兼容性以官方文档为准。

---

## Q4 [基础] Keyed State 的 ValueState、ListState、MapState 分别适合什么场景？如何选择？

**答案**

**是什么**  
- **ValueState<T>**：单值状态；适合「每个 key 一个当前值」，如去重里的「是否已见」、聚合里的「当前累加值」。  
- **ListState<T>**：列表状态；适合「每个 key 一个列表」，如最近 N 条记录、缓冲一批再发。  
- **MapState<K,V>**：键值状态；适合「每个 key 一个 map」，如按子 key 计数、按维度聚合。

**选择**：  
- 单值、无历史列表用 ValueState；需保留多条用 ListState；需按子 key 访问用 MapState。  
- MapState 比 ListState 的「先 list 再过滤」更省内存与 CPU，适合大 key 下的多维度状态。

**为什么这样设计**  
- **ValueState**：单值，访问快、内存小；适合简单状态。  
- **ListState**：列表，支持追加、遍历；但查找需遍历，性能不如 MapState。  
- **MapState**：键值，支持按 key 访问；适合多维度状态，性能好。

**注意**：状态需在 `RuntimeContext` 里注册（如 `getRuntimeContext().getState(descriptor)`）；带 TTL 时需在 StateDescriptor 里配置。

---

## Q5 [进阶] Checkpoint 的「对齐」和「非对齐」有什么区别？非对齐有什么代价？

**答案**

**是什么**  
- **对齐 Checkpoint（Aligned）**：某算子收到某 checkpoint 的 barrier 时，会**先阻塞**该 channel 上 barrier 之后的数据，等**所有**输入 channel 的 barrier 都到齐后，再做本算子的状态快照，然后下发 barrier；保证快照是「所有输入到 barrier 为止」的一致状态。  
- **非对齐 Checkpoint（Unaligned）**：barrier 到达时**不阻塞**后续数据；算子把 barrier 到达时已在 channel 里的数据（in-flight）也记入快照，然后立即下发 barrier；对齐时间短，但快照体积会变大（含 in-flight 数据），恢复时需重放这些数据。

**为什么这样设计**  
- **对齐**：保证快照一致性，但对齐时间长（需等最慢的 channel）；适合对齐时间短的作业。  
- **非对齐**：对齐时间短，但快照大（含 in-flight 数据）；适合背压大、对齐很慢的作业。

**代价**：  
- 非对齐：快照更大、恢复时可能略慢；适合**背压大、对齐很慢**的作业。  
- 对齐：快照小、语义清晰；默认推荐；若 checkpoint 长期卡在「对齐」阶段，可尝试开启非对齐。

**适用版本**：1.17；非对齐在 1.11+ 支持，1.12+ 可配置为默认。

---

## Q6 [进阶] 状态 TTL 是什么？如何配置？对 Checkpoint 和恢复有什么影响？

**答案**

**是什么**  
**状态 TTL**：为 Keyed State 设置**生存时间**，过期后访问时视为不存在（可配置清理策略）；用于减少状态体积、避免无限增长。

**配置**：  
- 在 `StateTtlConfig` 里设置 `ttl`（Duration）、`updateType`（OnCreate/OnReadAndWrite）、`stateVisibility`（ReturnExpiredIfNotCleanedUp/NeverReturnExpired）、清理策略（全量清理、增量清理、RocksDB 压缩时清理）。  
- 将 `StateTtlConfig` 设到 `StateDescriptor`，再注册状态。

**对 Checkpoint/恢复的影响**：  
- 过期数据在 Checkpoint 里**仍会写入**（恢复后仍按 TTL 清理）；增量清理或压缩清理只减少运行时和本地状态体积。  
- 恢复后 TTL 继续生效；若 TTL 很长，历史状态会保留到过期为止。

**为什么这样设计**  
- **TTL**：减少状态体积，避免无限增长；但过期数据仍写入 Checkpoint，保证恢复一致性。  
- **清理策略**：全量清理开销大，增量清理或压缩清理开销小；按状态规模选择。

**注意**：MapState 的 TTL 是按 entry 过期；ListState 是全 list 一个 TTL。大状态 + TTL 建议用 RocksDB + 增量清理。

**适用版本**：1.17；TTL 在 1.6+ 支持，RocksDB 增量清理在 1.10+ 支持。

---

## Q7 [生产] Broadcast State 是什么？典型用法和注意事项？

**答案**

**是什么**  
**Broadcast State**：**广播流**上的状态；广播流的一条记录会发往**所有**下游算子实例，下游用 Broadcast State 存「广播出来的规则/配置」；另一条主流按 key 分区，下游可「用广播状态 + 本 key 数据」做处理。

**典型用法**：  
- **规则/配置下发**：规则流 broadcast，主流按 key 处理；每条主流数据可查当前规则（如风控规则、映射表）。  
- **动态维度表**：维度表变更通过广播流下发，主流数据与维度 join 时总能看到最新维度。

**为什么这样设计**  
- **广播流**：一条记录发往所有实例，保证所有实例看到相同内容；适合规则/配置下发。  
- **Broadcast State**：所有实例存同一份逻辑状态（各自一份副本）；只有广播流可写，主流只读。

**注意**：  
- Broadcast State 是 **Operator State**，所有并行实例存同一份逻辑内容（各自一份副本）；只有广播流可写，主流只读。  
- 更新顺序：先处理广播流更新状态，再处理主流；同一 checkpoint 内顺序由 Flink 保证。  
- 状态不能太大（会复制到每个实例）；大维度表更适合用 Temporal Table Join 或外部存储。

**适用版本**：1.17；Broadcast State 在 1.5+ 支持，行为稳定。

---

## Q8 [高级] Checkpoint barrier 在源码里是如何传播的？如何保证所有算子快照对齐到同一时间点？

**答案**

**Barrier 传播机制**  
- **注入**：JM 向 Source 算子注入 barrier（通过 `CheckpointCoordinator`）；Source 收到 barrier 后，对本状态做快照，再向下游发送 barrier。  
- **传播**：barrier 随数据流向下游传播；每个算子收到 barrier 后，对本状态做快照，再转发 barrier。  
- **对齐**：多输入算子（如 join）需等所有输入的 barrier 都到齐后，再做快照；保证快照一致性。

**源码实现思路**  
- **CheckpointCoordinator**：JM 的 `CheckpointCoordinator` 负责触发 Checkpoint；向 Source 发送 `TriggerCheckpoint` 消息。  
- **AbstractStreamOperator**：算子的 `processElement` 处理数据，`processWatermark` 处理 barrier；收到 barrier 时调用 `snapshotState` 做快照。  
- **对齐机制**：`TwoInputStreamOperator` 等多输入算子，维护每个输入的 barrier 状态；所有输入的 barrier 都到齐后，再做快照。

**如何保证对齐**  
- **阻塞机制**：对齐模式下，算子收到某输入的 barrier 后，阻塞该输入 barrier 之后的数据；等所有输入的 barrier 都到齐后，再做快照、下发 barrier。  
- **非对齐模式**：不阻塞，但把 in-flight 数据也记入快照；保证快照一致性，但快照体积大。

**适用版本**：1.17；Barrier 传播机制在 1.2+ 支持，1.11+ 引入非对齐模式。

---

## Q9 [高级] 状态序列化机制是什么？如何优化序列化性能？自定义序列化器如何实现？

**答案**

**序列化机制**  
- **Java 序列化**：默认使用 Java 序列化（`Serializable`），兼容性好但性能差、体积大。  
- **Kryo 序列化**：Flink 内置 Kryo 序列化，性能好、体积小；需注册类型（`env.registerType`）。  
- **自定义序列化**：实现 `TypeSerializer` 接口，自定义序列化逻辑；适合特定类型优化。

**如何优化**  
- **使用 Kryo**：`env.getConfig().enableForceKryo()` 或 `env.registerTypeWithKryoSerializer`；性能提升 2–5 倍。  
- **注册类型**：Kryo 需注册类型，否则用反射；注册后性能更好。  
- **自定义序列化**：对热点类型实现自定义 `TypeSerializer`；如用 Protobuf、Avro 等。

**自定义序列化实现**  
- **实现 TypeSerializer**：实现 `serialize`、`deserialize`、`copy`、`createInstance` 等方法。  
- **注册**：`env.registerTypeWithKryoSerializer(MyClass.class, MySerializer.class)` 或 `env.getConfig().registerKryoType(MyClass.class)`。

**实际案例**  
- **某公司优化**：从 Java 序列化切换到 Kryo，状态序列化时间减少 60%；注册常用类型后，再减少 20%。

**适用版本**：1.17；序列化机制在 1.x 稳定，1.10+ 优化 Kryo 性能。

---

## Q10 [高级] RocksDB 状态后端如何与 Flink 集成？状态如何存储和访问？

**答案**

**集成机制**  
- **RocksDB 实例**：每个 Task 有独立的 RocksDB 实例；状态按 key 组织，存在 RocksDB 的 key-value 存储里。  
- **状态访问**：`RocksDBStateBackend` 实现 `StateBackend` 接口；`AbstractRocksDBState` 封装 RocksDB 操作（get、put、delete）。

**存储结构**  
- **Key 组织**：状态按 `(namespace, key)` 组织；namespace 对应算子的状态命名空间，key 对应 Keyed State 的 key。  
- **Value 存储**：状态值序列化后存在 RocksDB；RocksDB 的 LSM-Tree 结构，写快、读略慢。

**内存模型与优化**  
- **托管内存 (Managed Memory)**：Flink 1.10+ 默认通过 `taskmanager.memory.managed.size` 统一管理 RocksDB 的内存（包括 **Block Cache**、**Write Buffer** 和 **Index/Filter Blocks**）。这避免了堆外内存失控导致的容器 OOM。
- **JNI 权衡**：RocksDB 是 C++ 编写，Java 访问需通过 JNI。**瓶颈**：频繁的 JNI 调用和序列化/反序列化开销。如果状态很小且访问极频（如简单的计数器），HashMapBackend 可能比 RocksDB 快 2-5 倍。

**源码实现思路**  
- **RocksDBStateBackend**：实现 `StateBackend` 接口；创建 `RocksDBKeyedStateBackend` 管理 Keyed State。  
- **RocksDBKeyedStateBackend**：封装 RocksDB 操作；`getValue`、`putValue`、`removeValue` 等方法。

**适用版本**：1.17；RocksDB 集成在 1.3+ 支持，1.10+ 优化性能。

---

## Q11 [高级] 增量 Checkpoint 是如何实现的？与全量 Checkpoint 有什么区别？

**答案**

**增量 Checkpoint 实现**  
- **RocksDB 快照**：RocksDB 支持增量快照（SST 文件级别）；只持久化新增或修改的 SST 文件，未修改的文件复用上次快照。  
- **快照链**：维护快照链（base checkpoint + incremental checkpoints）；恢复时从 base 开始，依次应用增量。

**底层原理**  
- Flink 会追踪哪些 SST 文件已经上传到持久化存储（如 HDFS）。在新的 Checkpoint 触发时，RocksDB 会创建一个 **Checkpoint 实例**（硬链接），Flink 扫描该实例下的文件，仅上传那些“新生成”的文件。
- **引用计数**：分布式存储上的 SST 文件通过引用计数管理，只有当所有依赖它的 Checkpoint 都过期时，文件才会被物理删除。

**与全量 Checkpoint 区别**  
- **全量**：每次 Checkpoint 都持久化全部状态；IO 大、耗时长，但恢复简单。  
- **增量**：只持久化增量；IO 小、耗时长，但恢复需合并增量链。

**适用版本**：1.17；增量 Checkpoint 在 1.15+ 成熟，1.17+ 优化恢复性能。

---

## Q12 [专家] Checkpoint 一直卡在「对齐」阶段，如何排查？可能的原因有哪些？

**答案**

**排查步骤**  
1. **检查背压**：Web UI 看各算子的 backpressure；若某算子背压高，该算子的 barrier 传播慢，导致对齐慢。  
2. **检查数据倾斜**：Web UI 看各 subtask 的 record 数；若某 subtask 数据量大，处理慢，barrier 传播慢。  
3. **检查网络**：TM 间网络是否正常？网络抖动或延迟高会导致 barrier 传播慢。  
4. **检查 Checkpoint 超时**：Checkpoint 超时时间是否过短？对齐时间长时，需适当拉长超时。

**可能原因**  
- **背压**：下游算子处理慢，barrier 传播慢；需优化慢算子或提高并行度。  
- **锁竞争 (Lock Contention)**：在 Flink 1.13 之前，Checkpoint 的触发需要获取 Task 的 **主锁 (StreamTask Lock)**。如果用户代码中有耗时的同步操作（如阻塞式 IO），会阻碍 Barrier 的处理。
- **非对齐 Checkpoint 的代价**：虽然非对齐能解决对齐慢，但它会显著增加 Checkpoint 的大小（包含 in-flight 数据），在 IO 瓶颈场景下反而可能导致 Checkpoint 失败。

**解决方案**  
- **开启非对齐 Checkpoint**：`execution.checkpointing.unaligned: true`。
- **使用单线程算子**：避免在 `processElement` 中进行耗时同步操作，改用 **Async I/O**。

**适用版本**：1.17；Checkpoint 对齐问题排查方法通用。

---

## Q13 [专家] 状态倾斜（某 key 状态 100GB）如何优化？能否拆分？如何保证一致性？

**答案**

**优化方案**  
- **状态拆分**：将大 key 的状态拆分成多个子 key；如原 key 是 `user_id`，拆成 `user_id_0`、`user_id_1` 等；处理时按子 key 聚合，结果侧合并。  
- **状态迁移**：将大 key 的状态迁移到外部存储（如 Redis、HBase）；Flink 状态只存小 key，大 key 查外部存储。  
- **RocksDB 优化**：大 key 用 RocksDB，支持大状态；但需优化 RocksDB 配置（block cache、write buffer）。

**拆分实现**  
- **加盐**：对 key 加随机后缀（如 `key + "_" + random(0, N)`），先按子 key 处理，再去盐合并。  
- **一致性保证**：拆分后，同一逻辑 key 的数据可能在不同 subtask；需在结果侧合并，保证一致性。

**为什么这样优化**  
- **状态拆分**：减少单 key 状态大小，分散到多个 subtask；但需在结果侧合并，增加复杂度。  
- **外部存储**：大 key 状态存外部，Flink 状态只存小 key；但需保证外部存储的可用性与一致性。

**实际案例**  
- **某公司**：某 key 状态 100GB，拆分成 10 个子 key；每个子 key 10GB，分散到 10 个 subtask；结果侧合并，性能提升 5 倍。

**适用版本**：1.17；状态拆分需自定义实现，Flink 不直接支持。

---

## Q14 [专家] 如何设计一个支持 PB级状态、毫秒级延迟、99.99% 可用性的流处理系统？

**答案**

**架构设计**  
- **状态存储**：PB 级状态用 RocksDB + 增量 Checkpoint + 分布式存储（HDFS/S3）；RocksDB 本地缓存热点，冷数据在分布式存储。  
- **延迟优化**：算子链、网络优化、状态访问优化（block cache、预取）；关键路径用 HashMap 状态后端，非关键路径用 RocksDB。  
- **高可用**：JM HA + Checkpoint 高频（如 30 秒）+ 多区域部署；故障时快速恢复，保证可用性。

**状态管理**  
- **分层存储**：热点状态在 RocksDB 本地，冷状态在分布式存储；根据访问频率动态迁移。  
- **状态压缩**：状态压缩（如 Snappy、LZ4）减少存储体积；但需权衡压缩时间与存储空间。

**延迟优化**  
- **算子链**：关键路径算子链化，减少序列化与网络；非关键路径可断开链，隔离背压。  
- **状态访问**：热点状态用 HashMap，冷状态用 RocksDB；或 RocksDB block cache 预热。

**高可用设计**  
- **Checkpoint 频率**：高频 Checkpoint（如 30 秒），减少恢复进度损失；但需权衡 Checkpoint 开销。  
- **多区域部署**：主备区域，主区域故障时切换到备区域；Checkpoint 跨区域同步。

**实际案例**  
- **某公司**：PB 级状态，RocksDB + 增量 Checkpoint + HDFS；Checkpoint 5 分钟，恢复 10 分钟；99.99% 可用性。

**适用版本**：1.17；需结合 RocksDB、增量 Checkpoint、分布式存储能力。

---

## Q15 [专家] 状态恢复失败，如何排查？可能的原因有哪些？如何修复？

**答案**

**排查步骤**  
1. **检查 Checkpoint 完整性**：Checkpoint 文件是否完整？是否有损坏？看 Checkpoint 目录的文件列表与大小。  
2. **检查状态格式兼容性**：状态格式是否兼容？Flink 版本是否匹配？看恢复日志里的异常。  
3. **检查状态后端兼容性**：状态后端类型是否匹配？HashMap 与 RocksDB 状态不兼容。  
4. **检查算子 UID**：算子 UID 是否匹配？UID 不匹配会导致状态无法绑定到正确算子。

**可能原因**  
- **Checkpoint 损坏**：Checkpoint 文件损坏或不完整；可能是存储故障、网络中断、写入失败。  
- **状态格式不兼容**：Flink 版本升级，状态格式不兼容；需做状态迁移。  
- **算子 UID 不匹配**：算子 UID 变更，状态无法绑定；需恢复原 UID 或迁移状态。  
- **状态后端不匹配**：状态后端类型变更（如 HashMap → RocksDB），状态不兼容；需迁移状态。

**如何修复**  
- **Checkpoint 损坏**：从更早的 Checkpoint 恢复；或从 Savepoint 恢复（Savepoint 更可靠）。  
- **状态格式不兼容**：做状态迁移；用旧版本读 Checkpoint，写为新格式；或使用 Flink 提供的迁移工具。  
- **算子 UID 不匹配**：恢复原 UID；或迁移状态到新 UID（需自定义迁移逻辑）。

**预防措施**  
- **Checkpoint 验证**：恢复前验证 Checkpoint 完整性；或使用 Savepoint（更可靠）。  
- **版本兼容性**：升级前检查状态格式兼容性；同大版本内一般兼容，跨大版本需迁移。

**适用版本**：1.17；状态恢复问题排查方法通用。

---

## Q16 [专家] 如何实现状态迁移？跨版本、跨状态后端的状态迁移方案？

**答案**

**状态迁移方案**  
- **Savepoint 迁移**：旧版本打 Savepoint，新版本从 Savepoint 恢复；需保证状态格式兼容。  
- **自定义迁移**：用旧版本读 Checkpoint，写为新格式；或写迁移作业，读取旧状态，写入新状态。

**跨版本迁移**  
- **同大版本**：一般状态格式兼容；直接 Savepoint 恢复即可。  
- **跨大版本**：需看发布说明；若不兼容，需做状态迁移（如用旧版本读 Savepoint，写为新格式）。

**跨状态后端迁移**  
- **HashMap → RocksDB**：状态格式不同，需迁移；写迁移作业，读取 HashMap 状态，写入 RocksDB 状态。  
- **RocksDB → HashMap**：类似，需迁移；但 HashMap 受内存限制，大状态不适合。

**实现方案**  
- **迁移作业**：写 Flink 作业，读取旧状态，写入新状态；需保证状态一致性。  
- **工具**：Flink 提供状态迁移工具（视版本而定）；或使用第三方工具。

**实际案例**  
- **某公司**：Flink 1.13 → 1.17，状态格式兼容，直接 Savepoint 恢复；HashMap → RocksDB，写迁移作业，迁移 1TB 状态，耗时 2 小时。

**适用版本**：1.17；状态迁移需根据版本与状态后端选择方案。

---

## Q17 [专家] 状态泄漏（状态持续增长）如何排查？如何修复？如何预防？

**答案**

**排查步骤**  
1. **检查状态大小**：Web UI 看各算子的 state size；若持续增长，可能是状态泄漏。  
2. **检查状态 TTL**：状态是否设置了 TTL？TTL 是否生效？看状态清理日志。  
3. **检查状态清理**：窗口触发后状态是否清理？`WindowFunction.clear` 是否调用？看代码逻辑。

**可能原因**  
- **状态未清理**：窗口触发后状态未清理；或状态 TTL 未设置，状态无限增长。  
- **状态 TTL 失效**：TTL 配置错误或清理策略未生效；状态未按预期清理。  
- **状态泄漏**：代码逻辑错误，状态未正确清理；如 MapState 的 entry 未删除。

**如何修复**  
- **设置 TTL**：对可过期的状态设置 TTL；如窗口状态设置窗口长度 + allowedLateness。  
- **修复清理逻辑**：检查 `WindowFunction.clear` 是否调用；或修复状态清理逻辑。

**如何预防**  
- **状态监控**：监控状态大小，设置告警；状态异常增长时告警。  
- **代码审查**：审查状态使用代码，确保状态正确清理；或使用状态 TTL。

**实际案例**  
- **某公司**：窗口状态未清理，运行 1 个月后状态 500GB；设置 TTL（1 小时）后，状态稳定在 50GB。

**适用版本**：1.17；状态泄漏排查方法通用。
