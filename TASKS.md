# pyspthin 开发任务拆分

本文件将 [docs.md](/Users/jarviski/workspace/spThin/docs.md:1) 中的需求整理为一份可执行的开发任务清单。

## 1. 项目定位

- 项目名称：`pyspthin`
- Python 包名：`pyspthin`
- 推荐源码目录：`src/pyspthin/`
- 目标：在尽量保持原始 R 包 `spThin` 算法语义的前提下，实现一个现代、可维护、可并行、面向大规模数据的 Python 版本。

## 2. 核心原则

- v1 只支持经纬度输入，不支持投影坐标。
- thinning 语义必须优先对齐 R `spThin`，而不是追求不同目标的“更优算法”。
- 生产实现不得构造完整稠密距离矩阵。
- 并行必须由用户显式指定，不实现自动调度器。
- 默认输出必须保留输入中的全部原始列，并通过稳定的 `record_id` 回表恢复原始整行。
- 与 R 版的兼容性验证必须进入主线开发流程，不能放到最后补。

## 3. 建议目录结构

```text
.
├── pyproject.toml
├── README.md
├── TASKS.md
├── docs/
├── scripts/
├── benchmarks/
├── tests/
├── src/
│   └── pyspthin/
│       ├── __init__.py
│       ├── api.py
│       ├── config.py
│       ├── models.py
│       ├── validate.py
│       ├── logging.py
│       ├── io/
│       ├── distance/
│       ├── graph/
│       ├── algorithm/
│       ├── parallel/
│       └── plotting/
└── data/
```

## 4. 里程碑总览

- `P0`：冻结语义基线与验收口径
- `P1`：建立 `pyspthin` 项目骨架
- `P2`：完成输入模型、校验与记录身份机制
- `P3`：完成距离后端与稀疏冲突图
- `P4`：完成 thinning 核心算法
- `P5`：完成对外 API、结果对象、CSV/日志输出
- `P6`：完成并行与随机性控制
- `P7`：完成测试、R 回归与 benchmark
- `P8`：完成文档、打包与 v1 发布准备

## 5. 详细任务拆分

### P0 冻结语义基线与验收口径

#### T0-1 整理 R 版语义基线

目标：
明确 Python 版必须保持一致的行为。

具体工作：
- 阅读并整理以下 R 文件：
  - `spThin-R/R/thin.algorithm.R`
  - `spThin-R/R/thin.R`
  - `spThin-R/R/summary_thin.R`
  - `spThin-R/R/plot_thin.R`
- 输出一份语义对照清单，至少覆盖：
  - 冲突定义：距离严格小于阈值
  - replicate 起点：每个 replicate 都从同一原始冲突关系开始
  - 删除策略：每轮删除当前冲突数最大的点
  - tie-breaking：并列最大时随机删一个
  - 停止条件：不存在冲突时停止
  - replicate 结果排序：按保留记录数降序
  - summary 统计口径
  - plot 统计口径

输出物：
- `docs/compatibility_checklist.md`

依赖：
- 无

验收标准：
- Python 实现的每个核心模块都能映射到这份清单。
- 文档中明确列出“必须一致”和“允许不同”的点。

#### T0-2 建立 R 参考执行脚本

目标：
让后续 Python 结果可以与 R 版自动对比。

具体工作：
- 编写一个 R 脚本，接受固定输入数据和参数。
- 脚本输出以下信息：
  - 每个 replicate 的保留记录数
  - 最大保留记录数
  - summary 表
  - 可选：每个 replicate 的记录身份或坐标输出
- 固定随机种子和运行方式，确保结果可重复。

输出物：
- `spThin-R/scripts/run_r_reference.R`

依赖：
- T0-1

验收标准：
- 本地可对小样本数据重复执行。
- 输出格式稳定，便于 Python 测试直接读取。

#### T0-3 准备统一测试与 benchmark 数据集

目标：
避免测试、回归、benchmark 各自使用不同数据，导致比较口径混乱。

具体工作：
- 准备 4 类数据：
  - 手工可验证小样本
  - 真实中样本
  - 高密冲突样本
  - 大规模性能样本
- 为每类数据记录：
  - 数据来源
  - 行数
  - 物种数
  - 空间分布特征
  - 推荐阈值

输出物：
- `tests/fixtures/`
- `benchmarks/datasets/`
- `docs/datasets.md`

依赖：
- 无

验收标准：
- 单元测试、R 回归、benchmark 都复用同一套基准数据。

### P1 建立 pyspthin 项目骨架

#### T1-1 初始化 Python 包结构

目标：
建立标准 `src` 布局，明确包名为 `pyspthin`。

具体工作：
- 创建 `pyproject.toml`
- 创建 `src/pyspthin/__init__.py`
- 创建 `tests/`
- 创建 `benchmarks/`
- 创建 `scripts/`
- 在包入口暴露最基本的 API 名称占位

输出物：
- `pyproject.toml`
- `src/pyspthin/`

依赖：
- 无

验收标准：
- `pip install -e .` 能安装成功。
- `python -c "import pyspthin"` 能通过。

#### T1-2 配置开发工具链

目标：
让开发环境可重复搭建，并具备最基本的质量检查能力。

具体工作：
- 确定 Python 版本为 `3.12`
- 配置运行时依赖：
  - `numpy`
  - `pandas`
  - `scipy`
  - `scikit-learn`
  - `pydantic` v2
  - `matplotlib`
  - `psutil`
- 配置开发依赖：
  - `pytest`
  - `hypothesis`
  - `ruff`
  - `mypy` 或 `pyright`
- 建立依赖锁定方案

输出物：
- `requirements.in`
- `requirements-dev.in`
- 锁定文件或等价依赖管理配置

依赖：
- T1-1

验收标准：
- 开发者能在新环境中完整安装并运行测试命令。

#### T1-3 建立基础 CI 命令约定

目标：
把常用检查流程固定下来。

具体工作：
- 约定并实现以下命令：
  - lint
  - type-check
  - test
  - compare-r
  - bench
- 在 README 或贡献文档中写清楚运行方式

输出物：
- `README.md` 或 `docs/development.md`

依赖：
- T1-2

验收标准：
- 团队成员不需要猜测如何运行质量检查。

### P2 输入模型、校验与记录身份机制

#### T2-1 定义配置模型

目标：
用 Pydantic 明确所有公共配置项。

具体工作：
- 设计 `ThinConfig`
- 设计 `ThinManyConfig`
- 设计输出与日志相关配置模型
- 至少覆盖以下参数：
  - `thin_par`
  - `reps`
  - `n_jobs`
  - `parallel_mode`
  - `species_col`
  - `lat_col`
  - `long_col`
  - `record_id_col`
  - `seed`
  - `write_csv`
  - `write_log`

输出物：
- `src/pyspthin/config.py`

依赖：
- T1-1

验收标准：
- 配置错误在执行核心算法前即可被拦截。

#### T2-2 实现输入表校验

目标：
让 `thin(...)` 和 `thin_many(...)` 在进入算法前就完成数据层面的合法性校验。

具体工作：
- 检查必需列是否存在
- 检查经纬度列是否可转换为数值
- 检查经度范围是否位于 `[-180, 180]`
- 检查纬度范围是否位于 `[-90, 90]`
- 定义缺失值处理策略
- 定义重复记录处理策略
- 对可安全修正的问题发出 warning
- 对有歧义的问题直接报错

输出物：
- `src/pyspthin/validate.py`

依赖：
- T2-1

验收标准：
- 不会静默交换经纬度列。
- 不会在高风险输入上继续计算。

#### T2-3 实现稳定 record_id 机制

目标：
确保 thinning 结果能回到输入表的原始整行。

具体工作：
- 支持用户显式传入 `record_id_col`
- 若未提供，则自动生成稳定唯一的 `record_id`
- 建立 `record_id -> 行位置` 映射
- 规定输出阶段基于 `record_id` 回表，不依赖经纬度重建结果

输出物：
- `src/pyspthin/models.py`
- `src/pyspthin/validate.py`

依赖：
- T2-2

验收标准：
- 任一输出记录都能唯一映射回输入中的一行。
- 默认输出保留输入全部原始列。

### P3 距离后端与稀疏冲突图

#### T3-1 定义距离后端抽象

目标：
将“距离/邻域搜索”与“thinning 主算法”解耦。

具体工作：
- 定义后端接口，至少包括：
  - 坐标标准化
  - 阈值单位转换
  - 半径邻域查询
  - 冲突边构建
- 约定地球半径常数并统一记录

输出物：
- `src/pyspthin/distance/base.py`

依赖：
- T2-2

验收标准：
- 核心算法层不直接依赖 `BallTree` 实现细节。

#### T3-2 实现 haversine 邻域搜索后端

目标：
用适合经纬度的索引结构取代 R 版的稠密距离矩阵。

具体工作：
- 使用 `BallTree(metric="haversine")`
- 将经纬度转为弧度
- 将公里阈值转换为弧度半径
- 获取阈值范围内邻居
- 处理自环、重复边、边界值判断
- 明确“严格小于阈值”的比较语义

输出物：
- `src/pyspthin/distance/haversine.py`

依赖：
- T3-1

验收标准：
- 小样本下冲突边结果与 R 版判定一致或仅存在可解释的极小浮点差异。

#### T3-3 实现稀疏冲突图存储

目标：
在不使用稠密矩阵的情况下保存冲突关系，并供多个 replicate 复用。

具体工作：
- 设计紧凑邻接表示
- 支持快速读取某点邻居
- 支持初始度数计算
- 支持只读共享使用
- 记录边数、节点数、平均度等元数据

输出物：
- `src/pyspthin/graph/conflict_graph.py`

依赖：
- T3-2

验收标准：
- 生产路径中不存在 `N x N` 稠密距离矩阵分配。

#### T3-4 实现内存风险保护

目标：
在冲突图过密时提前告警或中止，而不是把机器打爆。

具体工作：
- 基于边数和节点数估算图存储成本
- 设计可配置的风险阈值
- 当风险过高时给出明确异常或 warning
- 在日志中记录风险判断依据

输出物：
- `src/pyspthin/graph/guards.py`

依赖：
- T3-3

验收标准：
- 对明显高风险数据，系统能在主计算前透明失败或预警。

### P4 thinning 核心算法

#### T4-1 实现单 replicate 贪心删点算法

目标：
复刻 R `thin.algorithm()` 的核心行为。

具体工作：
- 基于冲突图计算每个点的初始冲突数
- 找到当前最大冲突数对应的候选点
- 若候选点有多个，随机选一个删除
- 删除后更新受影响点的冲突数
- 持续迭代，直到无冲突或剩余记录数不再需要继续

输出物：
- `src/pyspthin/algorithm/greedy.py`

依赖：
- T3-3

验收标准：
- 小规模样本上可逐轮手工验证删除顺序和停止条件。

#### T4-2 实现 replicate 执行器

目标：
支持在同一冲突图上重复执行 thinning。

具体工作：
- 为每个 replicate 重置状态
- 记录 replicate 级别元数据：
  - `replicate_id`
  - `seed`
  - `retained_record_ids`
  - `retained_count`
  - 耗时
- 在完成所有 replicate 后按 `retained_count` 降序排序

输出物：
- `src/pyspthin/algorithm/runner.py`

依赖：
- T4-1

验收标准：
- replicate 间互不污染。
- 结果排序规则与 R 版一致。

#### T4-3 设计结构化结果对象

目标：
用强类型对象替代无类型字典和裸列表。

具体工作：
- 设计 `ReplicateResult`
- 设计 `ThinResult`
- 设计 `ThinManyResult`
- 结果对象中保留：
  - 配置快照
  - 图统计信息
  - replicate 列表
  - 排序后的最佳结果引用

输出物：
- `src/pyspthin/models.py`

依赖：
- T4-2

验收标准：
- `summary_thin`、`plot_thin`、CSV 输出都可直接消费结果对象。

#### T4-4 实现回表恢复原始记录

目标：
把 retained ids 恢复成输入中的完整原始行。

具体工作：
- 根据 `record_id` 批量回表
- 默认保留全部原始列
- 附加运行元数据列：
  - `record_id`
  - `replicate_id`
  - `replicate_rank`
  - `retained_count`
  - `species`

输出物：
- `src/pyspthin/io/restore.py`

依赖：
- T2-3
- T4-3

验收标准：
- 输出不丢失用户输入中的附加列。

### P5 对外 API、CSV 输出与日志

#### T5-1 实现 thin(...)

目标：
提供单物种主入口。

具体工作：
- 接受 pandas DataFrame 输入
- 连接配置校验、数据校验、冲突图构建、replicate 执行、结果排序
- 支持是否返回内存中的 replicate 数据
- 支持是否写出 CSV
- 支持是否写日志

输出物：
- `src/pyspthin/api.py`

依赖：
- T2-2
- T4-4

验收标准：
- 能跑通一个单物种端到端示例。

#### T5-2 实现 thin_many(...)

目标：
提供多物种批处理入口。

具体工作：
- 按 `species_col` 分组
- 管理每个物种的输入校验和结果收集
- 要求用户显式指定 `parallel_mode`
- 汇总物种级结果

输出物：
- `src/pyspthin/api.py`

依赖：
- T5-1

验收标准：
- 多物种输入下可以得到按物种聚合的结构化结果。

#### T5-3 实现 CSV 输出

目标：
让用户可以将最佳结果或指定 replicate 写出为文件。

具体工作：
- 默认写出原始行子集，而不是仅写坐标列
- 支持输出目录不存在时自动创建
- 处理文件重名策略
- 在文件中附加必要元数据列

输出物：
- `src/pyspthin/io/csv_writer.py`

依赖：
- T4-4
- T5-1

验收标准：
- 写出的 CSV 可直接用于下游分析，不丢失原始信息。

#### T5-4 实现运行日志

目标：
让每次运行的配置和结果都可追踪。

具体工作：
- 记录开始时间、结束时间、耗时
- 记录关键配置：
  - `thin_par`
  - `reps`
  - `seed`
  - `parallel_mode`
  - `n_jobs`
- 记录汇总结果：
  - 最大保留数
  - replicate 分布
  - 冲突边数
  - 风险警告

输出物：
- `src/pyspthin/logging.py`

依赖：
- T5-1

验收标准：
- 用户可仅凭日志复盘一次运行的关键条件和结果。

#### T5-5 实现 summary_thin(...) 与 plot_thin(...)

目标：
对齐 R 包的辅助分析能力。

具体工作：
- `summary_thin(...)` 输出：
  - 最大保留数
  - 达到最大值的 replicate 数量
  - 保留数频次表
- `plot_thin(...)` 输出：
  - 累积最大值曲线
  - 对数曲线
  - 保留数直方图
- 输入统一为 Python 结果对象

输出物：
- `src/pyspthin/plotting/summary.py`
- `src/pyspthin/plotting/plot.py`

依赖：
- T4-3

验收标准：
- 对相同结果对象，summary 和图形输出逻辑稳定。

### P6 并行与随机性控制

#### T6-1 设计 RNG 拆分机制

目标：
确保串行与并行在相同 master seed 下都可复现。

具体工作：
- 明确 master seed 的来源与默认规则
- 设计 replicate 级 seed 派生方案
- 设计 species 级任务的 seed 派生方案
- 禁止依赖全局随机状态实现可复现

输出物：
- `docs/randomness.md`
- `src/pyspthin/parallel/random_state.py`

依赖：
- T4-2

验收标准：
- 同一输入和 master seed 下，重复运行结果稳定可追踪。

#### T6-2 实现 rep 并行

目标：
支持单物种多 replicate 并行执行。

具体工作：
- 实现 `parallel_mode="rep"`
- 控制 worker 数量
- 复用只读冲突图
- 收集 worker 返回结果并统一排序

输出物：
- `src/pyspthin/parallel/rep.py`

依赖：
- T6-1

验收标准：
- `n_jobs=1` 与 `n_jobs>1` 的结果满足可复现要求。

#### T6-3 实现 species 并行

目标：
支持多物种任务的物种级并行。

具体工作：
- 实现 `parallel_mode="species"`
- 每个 worker 完整处理一个物种
- 管理物种结果汇总
- 默认不启用嵌套并行

输出物：
- `src/pyspthin/parallel/species.py`

依赖：
- T5-2
- T6-1

验收标准：
- 多物种批处理中不会因为嵌套并行导致资源失控。

#### T6-4 并行内存行为验证

目标：
确认并行不会破坏稀疏图带来的内存优势。

具体工作：
- 观察不同 `n_jobs` 下的峰值内存
- 检查冲突图是否被重复复制
- 必要时改进共享只读状态或内存映射策略

输出物：
- `benchmarks/parallel_memory.py`
- `docs/parallel.md`

依赖：
- T6-2
- T6-3

验收标准：
- 并行后峰值内存增长可解释且受控。

### P7 测试、R 回归与 benchmark

#### T7-1 编写单元测试

目标：
覆盖核心模块的功能正确性。

具体工作：
- 测试配置模型校验
- 测试坐标校验与受控转换
- 测试 `record_id` 自动生成和显式校验
- 测试冲突边构建
- 测试贪心删点逻辑
- 测试 replicate 排序
- 测试回表行为

输出物：
- `tests/unit/`

依赖：
- P2
- P3
- P4

验收标准：
- 每个核心模块至少有对应单元测试。

#### T7-2 编写性质与不变量测试

目标：
验证算法输出满足基本数学与数据不变量。

具体工作：
- 检查最终保留集中任意两点距离不小于阈值
- 检查输出中不存在输入之外的记录
- 检查 replicate 结果按保留数非增排序
- 检查输出记录可唯一映射回原始输入
- 检查默认输出包含全部原始列

输出物：
- `tests/property/`

依赖：
- T7-1

验收标准：
- 随机生成数据集时也能持续通过这些不变量。

#### T7-3 编写 R 回归测试

目标：
把“与 R 兼容”从口头目标变成自动化检查。

具体工作：
- 调用 `spThin-R/scripts/run_r_reference.R`
- 对固定数据集比较：
  - 最大保留数
  - replicate 平均保留数
  - 保留数分布
  - summary 口径
- 明确可接受偏差阈值

输出物：
- `tests/regression/`

依赖：
- T0-2
- T7-1

验收标准：
- 达到 `docs.md` 定义的兼容性验收目标。

#### T7-4 编写 benchmark 工具

目标：
衡量运行时间、峰值内存和冲突图规模表现。

具体工作：
- 覆盖不同维度：
  - 小、中、大、超大数据规模
  - 均匀、聚集、高聚集空间分布
  - 稀疏、中等、高密冲突半径
  - `n_jobs=1,2,4,...`
- 记录：
  - 总运行时间
  - 峰值内存
  - 冲突边数
  - 保留记录数汇总

输出物：
- `benchmarks/run_benchmarks.py`

依赖：
- T3-4
- T6-4

验收标准：
- benchmark 结果可重复收集并形成表格或报告。

#### T7-5 失败路径与边界条件测试

目标：
确保系统在异常情况下透明失败。

具体工作：
- 测试非法经纬度
- 测试缺失关键列
- 测试空数据集
- 测试单条记录输入
- 测试超大阈值导致高密冲突图
- 测试日志或 CSV 输出路径异常

输出物：
- `tests/failure/`

依赖：
- T5-4
- T7-1

验收标准：
- 错误信息具体明确，不静默失败。

### P8 文档、打包与 v1 发布准备

#### T8-1 编写用户文档

目标：
让用户理解 `pyspthin` 的使用方式和与 R 版的关系。

具体工作：
- 编写安装说明
- 编写快速开始
- 编写单物种与多物种示例
- 编写与 R `spThin` 的兼容性说明
- 编写限制与已知风险说明

输出物：
- `README.md`
- `docs/usage.md`
- `docs/compatibility.md`

依赖：
- T5-5
- T7-3

验收标准：
- 新用户可只看文档完成一次基本使用。

#### T8-2 编写开发者文档

目标：
降低后续维护成本。

具体工作：
- 说明项目结构
- 说明测试与 benchmark 运行方式
- 说明随机性与并行设计
- 说明如何新增距离后端

输出物：
- `docs/development.md`

依赖：
- T6-4
- T7-4

验收标准：
- 新维护者能理解主要设计边界和扩展点。

#### T8-3 打包与发布前检查

目标：
为 v1 发布做最终质量关口。

具体工作：
- 检查包元数据与版本号
- 检查导出 API
- 检查许可证与引用信息
- 跑完整检查流程：
  - lint
  - type-check
  - unit tests
  - regression tests
  - benchmarks

输出物：
- 发布检查清单

依赖：
- P1 至 P8 前序任务全部完成

验收标准：
- 满足本文件中的 v1 完成定义后方可发布。

## 6. v1 完成定义

只有满足以下条件，`pyspthin` 才可视为 v1 完成：

- 已实现 `thin(...)`
- 已实现 `thin_many(...)`
- 已实现 `summary_thin(...)`
- 已实现 `plot_thin(...)`
- 生产实现不构造完整稠密距离矩阵
- 默认输出保留输入中的全部原始列
- 结果可通过 `record_id` 稳定回表
- 支持 `parallel_mode="rep"` 与 `parallel_mode="species"`
- 同一 master seed 下结果可复现
- 与 R `spThin` 在阈值语义和结果分布上达到兼容性目标
- 已具备单元测试、R 回归测试与 benchmark 工具

## 7. 建议开发顺序

推荐按以下顺序推进：

1. 完成 `P0`，冻结语义基线与验收口径。
2. 完成 `P1`，建立 `pyspthin` 包骨架和开发工具链。
3. 完成 `P2`，先把输入校验和 `record_id` 机制打牢。
4. 完成 `P3`，建立 haversine 邻域搜索与稀疏冲突图。
5. 完成 `P4`，实现 replicate 级 thinning 核心算法。
6. 完成 `P5`，打通用户 API、回表恢复、CSV 和日志。
7. 完成 `P6`，再加入并行和可复现随机性控制。
8. 完成 `P7`，补齐测试、R 回归和 benchmark。
9. 完成 `P8`，收口文档和发布准备。

## 8. 不纳入 v1 的事项

以下内容明确不纳入 v1：

- GPU 加速
- 分布式运行
- 投影坐标对外支持
- 自动并行模式 `auto`
- 动态调度器、负载均衡器、内存预算调度器
- 嵌套并行默认启用
- 最大独立集、模拟退火、Poisson-disk sampling 等替代性优化目标算法

## 9. 当前建议先落地的首批任务

如果要马上开工，建议先创建以下 issue：

- `T0-1` 整理 R 版语义基线
- `T1-1` 初始化 `pyspthin` 包结构
- `T2-1` 定义配置模型
- `T2-2` 实现输入表校验
- `T3-1` 定义距离后端抽象
- `T3-2` 实现 haversine 邻域搜索后端
- `T4-1` 实现单 replicate 贪心删点算法
- `T7-1` 编写单元测试骨架

这 8 个任务完成后，项目就具备了进入核心算法验证阶段的基础条件。
