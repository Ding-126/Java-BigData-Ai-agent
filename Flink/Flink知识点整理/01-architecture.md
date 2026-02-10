# 架构与基础

## Q1 [基础] 请简述 Flink 的整体架构，以及 JobManager 与 TaskManager 的职责。

**答案**

**是什么**  
Flink 采用**主从架构**：一个 JobManager（主）负责调度与协调，多个 TaskManager（从）负责执行算子与状态。

- **JobManager**  
  - 接收作业（JobGraph），生成 ExecutionGraph，调度 Task、分配 Slot、触发 Checkpoint。  
  - 高可用下可有多个 JM，通过 ZooKeeper/K8s 选主，只有一个 Active；其余 Standby。  
- **TaskManager**  
  - 以 **Slot** 为资源单位执行 Task；一个 Slot 可运行一个算子链（Operator Chain）的一个并行子任务。  
  - 持有状态后端、网络缓冲，与 JM 心跳、上报指标。

**为什么这样设计**  
- **主从分离**：调度与执行解耦，JM 专注协调、TM 专注计算，便于扩展与故障隔离。  
- **Slot 抽象**：统一资源模型，便于跨算子、跨作业的资源管理与调度。  
- **高可用**：JM 单点故障通过 Leader 选举解决；TM 无状态，挂掉后由 JM 重新调度。

**关系**：Client 提交 JobGraph 给 JM；JM 向 TM 分配 Task；TM 之间按数据流做 Shuffle。TM 数量与每 TM 的 Slot 数决定最大并行度。

---

## Q2 [进阶] Flink 的 Slot 与并行度是什么关系？一个 Slot 里能跑多个算子吗？

**答案**

**是什么**  
- **并行度（Parallelism）**：某个算子（或整作业）的并行实例个数，即该算子有多少个并发运行的 Task。  
- **Slot**：TaskManager 上的资源槽，一个 Slot 对应一个**线程**，用于执行**一个算子链**上的**一个并行子任务**。

**关系**：  
- 算子链（Operator Chain）：多个算子可链成一个大 Task，共享一个 Slot、减少序列化与网络。  
- 因此：**一个 Slot 里跑的是「一条链」的一个并行实例**，即多个算子合在一起占一个 Slot，而不是「一个 Slot 多链」。  
- 总 Slot 数 ≥ 作业中「最大并行度」（通常等于某个算子的并行度）。若 Slot 不足，作业会等待资源。

**为什么这样设计**  
- **算子链**：减少序列化/反序列化、网络传输、线程切换，提升吞吐与降低延迟；但链内算子共享资源，需权衡。  
- **Slot 与并行度**：Slot 是物理资源，并行度是逻辑并发；一个 Slot 对应一个并行实例，保证资源隔离。

**选型**：TM 的 Slot 数一般设为 CPU 核数或略少；算子链由 Flink 自动做，也可通过 `disableChaining()` 等 API 调优。

---

## Q3 [生产] 在 YARN 或 K8s 上部署 Flink 时，JobManager 和 TaskManager 的资源如何规划？高可用怎么配？

**答案**

**资源规划**  
- **JobManager**：主要吃 CPU（调度、协调）和少量内存；一般 1–2 核、1–4 GB 即可；大作业或大量小作业时可适当加大。  
- **TaskManager**：按「每 TM 的 Slot 数 × 每 Slot 所需内存」给内存；每 Slot 通常 1–4 GB，视状态与缓冲而定。CPU 与 Slot 数大致 1:1 或略多，避免过度超卖。

**高可用（HA）**  
- **YARN**：在 `flink-conf.yaml` 里配 `high-availability: zookeeper`、`high-availability.storageDir`（如 HDFS 路径）、ZooKeeper 地址；JM 元数据与 Checkpoint 状态存 HDFS，JM 状态存 ZK，主挂掉后重新选举并从 HDFS 恢复。  
- **K8s**：可用原生 K8s HA（多 JM Pod + Leader 选举）或 Flink 的 K8s HA 方案；状态与元数据存到持久卷或外部存储（如 S3/HDFS），重启后从该存储恢复。

**为什么这样规划**  
- **JM 资源**：调度算法复杂度低，主要瓶颈在并发作业数；内存用于存储 ExecutionGraph 与元数据，一般不大。  
- **TM 资源**：按 Slot 分配便于资源隔离；CPU 与 Slot 1:1 避免上下文切换与调度抖动。

**注意**：TM 无状态（或仅本地状态），挂掉后由 JM 重新调度到其他 TM；JM HA 保证调度元数据不丢，配合 Checkpoint/Savepoint 保证作业状态可恢复。

**适用版本**：1.17；YARN/K8s 集成在 1.15+ 行为稳定。

---

## Q4 [基础] JobGraph、ExecutionGraph 和物理执行图分别是什么？谁在什么时候生成？

**答案**

**是什么**  
- **JobGraph**：**逻辑图**的优化表示，由 Client 在提交前生成；将多个算子链成 JobVertex、标注边与分区方式；是提交给 JobManager 的单元。  
- **ExecutionGraph**：**调度视图**，由 JobManager 根据 JobGraph 和并行度生成；每个 JobVertex 展开成多个 ExecutionVertex（并行实例），边展开成 ExecutionEdge；包含 Slot 分配、Attempt 等信息。  
- **物理执行**：TaskManager 收到 Task 部署请求后，运行的是 **Task**（对应 ExecutionVertex 的某次 Attempt）；多个 Task 通过 Shuffle 连接成实际数据流。

**为什么分三层**  
- **JobGraph**：逻辑优化（算子链、分区策略）在 Client 完成，减少 JM 负担；提交单元小，便于序列化与传输。  
- **ExecutionGraph**：调度决策（并行度、Slot 分配、重试策略）在 JM 完成，依赖集群资源状态；便于调度优化与故障恢复。  
- **Task**：实际执行单元，TM 只需知道「运行什么算子、从哪里读、写到哪里」；轻量、可快速部署。

**顺序**：Client 建 JobGraph → 提交 JM → JM 建 ExecutionGraph、向 TM 申请 Slot、部署 Task → TM 执行 Task。

---

## Q5 [进阶] Flink 有哪几种集群部署模式？Per-Job、Session、Application 各适合什么场景？

**答案**

**是什么**  
- **Session 模式**：集群常驻，多个作业共享同一批 TaskManager；提交快、资源复用，但作业间互相争资源，单作业故障可能影响集群。适合**短作业、开发测试、小规模**。  
- **Per-Job 模式**：每个作业独占一个集群，作业结束则集群回收；资源隔离好、故障隔离好，但启停有开销。适合**生产上对隔离和稳定性要求高的作业**。  
- **Application 模式**：作业的 main 在集群内执行（而非 Client），无 Client 与集群的长连接；适合 **K8s/YARN 上作业多、Client 不便常驻** 的场景；1.11+ 推荐。

**为什么这样设计**  
- **Session**：资源复用、提交快，适合开发/测试；但隔离差，生产慎用。  
- **Per-Job**：隔离最好，故障不影响其他作业；但启停有开销，适合长期运行的生产作业。  
- **Application**：解决 Client 网络/权限问题，适合云原生、多租户；main 在集群内，便于 CI/CD。

**选型**：生产大作业、对 SLA 要求高常用 Per-Job 或 Application；开发/联调可用 Session。

**适用版本**：1.17；Application 模式在 1.11+ 支持并持续增强。

---

## Q6 [进阶] Flink 与 Spark Streaming（结构化流）在架构和模型上有什么本质区别？

**答案**

**是什么**  
- **计算模型**：Flink 是**真正的流**，逐条或微批处理，事件驱动；Spark Streaming 早期是**批的序列**（DStream 微批），Structured Streaming 是「流式表」模型，底层仍多按微批或连续处理执行。  
- **状态与语义**：Flink 原生**有状态**、**事件时间**、**Watermark**，支持 Exactly-Once、状态后端可配；Spark 需用 checkpoint 与 stateful 算子配合，语义与 Flink 类似但实现路径不同。  
- **延迟与吞吐**：Flink 可做到毫秒级延迟、背压自然传递；Spark 微批间隔影响延迟，背压通过调度节流。  
- **生态**：Flink 强调流批一体（DataStream + Table/SQL）；Spark 强调批为主、流为扩展。

**为什么有这些区别**  
- **Flink 设计**：从流计算出发，状态、时间、背压都是原生支持；适合低延迟、有状态场景。  
- **Spark 设计**：从批计算出发，流是批的扩展；适合批为主、流为辅的场景。

**选型**：强需求「低延迟 + 有状态 + 事件时间」时 Flink 更贴；已有 Spark 栈、以批为主可继续用 Spark。

---

## Q7 [生产] Client 在提交作业时做什么？为什么生产上有时用 Application 模式避免 Client？

**答案**

**是什么**  
**Client 职责**：  
- 执行用户 `main`，构建 StreamExecutionEnvironment、生成 JobGraph；  
- 将 JobGraph 提交给 JobManager（通过 REST 或 RPC）；  
- Session/Per-Job 下，Client 与集群保持连接，可接收进度与异常；作业结束后 Client 才退出。

**为什么用 Application 模式**  
- Client 在用户机器上跑，占用户机资源，且需能连到集群；集群在远端或 K8s 内时，Client 网络与权限不便。  
- Application 模式下，`main` 在 JobManager 所在容器/节点执行，无需常驻 Client；提交用 `flink run-application` 或 K8s/YARN 的 Application 提交，更适合**生产、CI/CD、多租户**。

**适用版本**：1.17；Application 模式在 1.11+ 推荐用于生产。

---

## Q8 [高级] JobManager 的调度算法是什么？如何分配 Slot？如何保证公平性？

**答案**

**调度算法**  
- **调度策略**：Flink 采用**延迟调度（Lazy Scheduling）**：先构建 ExecutionGraph，再按依赖顺序调度；上游完成后再调度下游，避免资源浪费。  
- **Slot 分配**：JM 维护 Slot Pool（可用 Slot 列表），按 ExecutionVertex 的资源需求（CPU、内存）匹配 Slot；优先分配本地 Slot（同一 TM），减少网络；若无匹配则等待。

**如何保证公平性**  
- **作业级公平**：多作业时，JM 按提交顺序或优先级分配 Slot；Session 模式下，先提交的作业优先获得资源。  
- **算子级公平**：同一作业内，按 ExecutionGraph 的拓扑顺序调度；上游先调度，下游等待上游完成。

**源码实现思路**  
- **调度器核心**：`SchedulerNG` 及其子类 `DefaultScheduler`。它通过 `ExecutionGraph` 追踪每个 `Execution` 的状态机（CREATED -> SCHEDULED -> DEPLOYING -> RUNNING）。
- **资源申请流**：`Scheduler` -> `SlotPool` (`DeclarativeSlotPoolBridge`) -> `ResourceManager`。
- **Slot 分配逻辑**：`SlotSelectionStrategy`（默认 `LocationPreferenceSlotSelectionStrategy`）。它会计算 `SlotProfile` 与可用 `TaskManagerSlot` 的匹配得分，得分考虑 **本地性（Locality）**：同一机器 > 同一机架 > 远程。

**优化**  
- **位置偏好**：优先分配同一 TM 的 Slot，减少网络；通过 `setPreferredLocations` 指定。  
- **资源预留**：大作业可预留 Slot，避免资源碎片；Session 模式下需权衡公平性。

**适用版本**：1.17；调度算法在 1.5+ 稳定，1.10+ 引入自适应调度。

---

## Q9 [高级] Flink 高可用中 Leader 选举是如何实现的？JM 故障后如何快速恢复？

**答案**

**Leader 选举实现**  
- **ZooKeeper 方案**：JM 在 ZK 上创建临时节点（如 `/leader/latch`），第一个创建成功的成为 Leader；其他 JM 监听该节点，Leader 挂掉后重新竞争。  
- **K8s 方案**：可用 K8s 的 Leader Election（通过 ConfigMap/Lease），或 Flink 的 K8s HA Controller；原理类似，通过锁机制选主。

**故障恢复流程**  
1. **检测**：Standby JM 检测到 Leader 心跳超时（或 ZK 节点消失）。  
2. **选举**：Standby JM 竞争成为新 Leader（创建临时节点或获取锁）。  
3. **恢复元数据**：新 Leader 从 HDFS/S3 读取 ExecutionGraph、Checkpoint 元数据（`high-availability.storageDir`）。  
4. **恢复作业**：从最新 Checkpoint 恢复所有作业；向 TM 重新部署 Task。

**如何保证快速恢复**  
- **元数据持久化**：ExecutionGraph、Checkpoint 元数据存 HDFS/S3，恢复时直接读取；避免重建图。  
- **Checkpoint 频率**：适当提高 Checkpoint 频率（如 1 分钟），减少恢复进度损失。  
- **Standby JM 预热**：Standby JM 可预加载元数据，选举后直接恢复；减少恢复时间。

**源码实现思路**  
- **核心接口**：`LeaderElectionService` 和 `LeaderContender`。
- **ZK 实现细节**：使用 Curator 库的 `LeaderLatch`。JM 启动时注册为 Contender，当被选为 Leader 时，回调 `grantLeadership`。
- **元数据存储**：`CheckpointRecoveryFactory` 负责从 HA 存储（如 `ZooKeeperCheckpointIDCounter`）恢复 Checkpoint ID。

**适用版本**：1.17；HA 机制在 1.2+ 支持，1.5+ 稳定。

---

## Q10 [高级] 如何设计一个支持 1000+ 作业、多租户、跨区域的高可用 Flink 平台？

**答案**

**架构设计**  
- **多集群架构**：按租户或业务线划分集群（如租户 A 用集群 1，租户 B 用集群 2）；或按区域划分（如北京集群、上海集群）。  
- **统一调度层**：上层调度系统（如 Flink Session Cluster Manager）管理多个 Flink 集群；作业提交到调度层，由调度层选择目标集群。  
- **资源隔离**：YARN/K8s 队列/命名空间隔离；不同租户用不同队列，限制资源上限（CPU、内存、Slot 数）。

**多租户实现**  
- **资源配额**：每个租户限制最大并行度、最大 Slot 数、最大状态大小；通过 YARN CapacityScheduler 或 K8s ResourceQuota 实现。  
- **优先级**：核心租户高优先级，优先分配资源；通过 YARN 队列权重或 K8s PriorityClass 实现。  
- **监控隔离**：每个租户独立的监控与告警；Metrics 按租户标签区分。

**跨区域部署**  
- **主备架构**：主区域运行作业，备区域 Standby；主区域故障时切换到备区域。  
- **数据同步**：Checkpoint/Savepoint 跨区域同步（如 HDFS 跨区域复制、S3 跨区域复制）；保证恢复时数据可用。  
- **网络优化**：跨区域网络延迟高，可考虑区域独立部署；或使用专线、CDN 优化。

**实际案例**  
- **大规模平台**：某公司支持 2000+ 作业，采用「多 Session 集群 + 统一调度」；按业务线划分集群，每集群 50–100 作业。  
- **多租户**：通过 YARN CapacityScheduler，10 个租户共享集群；核心租户 50% 资源，其他租户各 5%；资源隔离良好，故障互不影响。

**适用版本**：1.17；多租户与跨区域需结合 YARN/K8s 能力。

---

## Q11 [专家] 作业提交后一直处于 CREATED 状态，如何排查？可能的原因有哪些？

**答案**

**排查步骤**  
1. **检查 Slot 资源**：Web UI 看「Available Task Slots」是否为 0；若为 0，说明 Slot 不足，作业等待资源。  
2. **检查 ExecutionGraph**：Web UI 看 ExecutionGraph 是否构建成功；若失败，看 JM 日志里的异常。  
3. **检查调度器状态**：JM 日志看 `Scheduler` 是否正常；是否有调度异常或死锁。

**可能原因**  
- **Slot 不足**：总 Slot 数 < 作业最大并行度；需增加 TM 或减少 Slot 需求。  
- **资源不匹配**：作业要求的资源（CPU、内存）与可用 Slot 不匹配；需调整作业资源需求或 TM 资源配置。  
- **RPC 瓶颈与超时**：在大规模集群中，JM 与 RM 之间的 `slotRequest` 可能因为 **Akka 帧大小限制 (`akka.framesize`)** 或网络拥塞超时。
- **Jar 包分发失败**：`BlobServer` 无法将 Jar 包分发到 TM，导致 Task 无法部署。
- **调度器死锁**：罕见的线程死锁或 `JobMaster` 内部状态机卡死。

**如何验证**  
- **Slot 资源**：`curl http://jm:8081/taskmanagers` 看可用 Slot；或 Web UI 的「Task Managers」页面。  
- **调度器**：JM 日志搜索 "Scheduler"、"ExecutionGraph"；看是否有异常或卡住。  
- **Akka 日志**：搜索 "AskTimeoutException" 或 "Frame size exceeded"。

**解决方案**  
- **Slot 不足**：增加 TM（`flink run -t yarn-session` 或 K8s 扩容）；或降低作业并行度。  
- **配置调优**：增大 `akka.ask.timeout` 和 `akka.framesize`。
- **资源隔离**：使用 Slot Sharing Group 隔离。

**适用版本**：1.17；调度问题排查方法通用。

---

## Q12 [专家] 大规模作业（1000+ 并行度）提交时，如何优化调度性能？有哪些瓶颈？

**答案**

**瓶颈分析**  
- **ExecutionGraph 构建**：1000+ ExecutionVertex，构建 ExecutionGraph 耗时；JM 内存占用大。  
- **Slot 分配**：1000+ Slot 需要分配，分配算法复杂度 O(n²) 或更高；分配时间长。  
- **Task 部署**：1000+ Task 需要部署到 TM，网络 RPC 开销大；部署时间长。

**优化方案**  
- **分批调度**：不是一次性调度所有 ExecutionVertex，而是分批调度（如每批 100 个）；减少单次调度压力。  
- **并行部署**：Task 部署并行化，多个 Task 同时部署；减少总部署时间。  
- **资源预留**：大作业提交前预留 Slot，避免等待；Session 模式下可配置 Slot Pool 大小。

**源码优化思路**  
- **自适应调度器**：使用 `AdaptiveScheduler`。它允许作业在资源不足时以较低并行度启动，避免由于等待全部资源而导致的 CREATED 状态卡死。
- **批量资源申请**：在 `DeclarativeSlotPool` 中，Flink 1.12+ 引入了声明式资源管理，JM 向 RM 申请的是“资源集合”而非单个 Slot，极大减少了 RPC 次数。
- **部署优化**：通过 `TaskExecutorGateway.submitTask` 批量提交，并优化 `BlobServer` 的并发下载能力。

**实际案例**  
- **某公司**：2000 并行度作业，优化前调度耗时 5 分钟；优化后（分批调度 + 并行部署）降至 1 分钟。  
- **关键配置**：`scheduler-mode: reactive`（1.10+ 自适应调度）；`taskmanager.numberOfTaskSlots` 与并行度匹配。

**适用版本**：1.17；1.10+ 引入自适应调度，1.12+ 优化大规模调度性能。

---

## Q13 [专家] 如何设计一个支持动态扩缩容、资源自动调度的 Flink 平台？

**答案**

**动态扩缩容设计**  
- **指标采集**：采集作业的背压、吞吐、延迟、资源使用率；通过 Flink Metrics + Prometheus 实现。  
- **扩缩容策略**：背压高或吞吐不足时扩容（增加 TM 或提高并行度）；资源空闲时缩容（减少 TM 或降低并行度）。  
- **平滑扩缩容**：扩容时从 Savepoint 恢复，新 Task 逐步加入；缩容时先打 Savepoint，再停止多余 Task。

**资源自动调度**  
- **资源预测**：根据历史数据预测作业资源需求（CPU、内存、Slot）；提前预留资源。  
- **优先级调度**：高优先级作业优先分配资源；低优先级作业等待或降级。  
- **资源回收**：长时间空闲的作业自动停止或降级；释放资源给其他作业。

**实现方案**  
- **外部调度器**：上层调度系统（如 Kubernetes Operator、YARN ResourceManager）监控 Flink 指标，动态调整 TM 数量。  
- **Flink 自适应**：Flink 1.10+ 的 Reactive Mode 支持自适应调度；根据背压自动调整并行度（需配合外部资源管理）。

**实际案例**  
- **K8s Operator**：Flink K8s Operator 支持自动扩缩容；根据 Metrics 自动调整 Deployment 副本数。  
- **YARN 动态资源**：YARN CapacityScheduler 支持动态队列容量；根据负载自动调整队列资源。

**适用版本**：1.17；需结合 K8s Operator 或 YARN 动态资源管理。

---

## Q14 [专家] 跨区域部署时，如何保证 Checkpoint 跨区域同步的可靠性？网络抖动如何处理？

**答案**

**Checkpoint 跨区域同步**  
- **同步策略**：Checkpoint 先写本地存储（如 HDFS），再异步同步到远程区域（如 S3 跨区域复制）；或直接写跨区域存储（如 S3，自动跨区域复制）。  
- **可靠性保证**：同步失败时重试；或使用两阶段提交（本地确认 + 远程确认）；保证至少一个区域有完整 Checkpoint。

**网络抖动处理**  
- **重试机制**：Checkpoint 写入失败时重试（如 3 次）；重试间隔递增（如 1s、2s、4s）。  
- **超时设置**：Checkpoint 超时时间适当拉长（如 10 分钟），容忍网络抖动；但过长会影响恢复进度。  
- **降级策略**：网络持续不可用时，Checkpoint 只写本地；网络恢复后再同步到远程。

**实际案例**  
- **某公司跨区域部署**：主区域 HDFS，备区域 S3；Checkpoint 先写 HDFS，再异步同步到 S3；同步失败时本地保留，网络恢复后补同步。  
- **网络抖动**：跨区域延迟 50–200ms，Checkpoint 超时设为 5 分钟；偶发抖动（< 1 分钟）不影响，持续抖动时告警。

**适用版本**：1.17；Checkpoint 存储支持 HDFS、S3 等，跨区域同步依赖存储系统能力。
