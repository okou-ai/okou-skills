# 本地参考布局目录

优先使用用户保留的原始布局；只有原始布局不合适时，才按下表选择补充布局。点击布局名称读取对应 HTML，具体占位符和重复块直接看 HTML，不再维护另一套 JSON 元数据。路径相对于本文件。

容量仅供选版参考，不代表固定页数或保证内容能放下。选中的布局需要按用户原始 PPT 的样式调整，实际适配方式见 [README](../README.md)。

| 布局（HTML） | 类别 | 用途 | 容量提示 |
|---|---|---|---|
| [cover](../layouts/fragments/cover.html) | 开场与导航 | 开场标题与受众背景 | 一个标题、一个副标题、简短署名 |
| [toc](../layouts/fragments/toc.html) | 开场与导航 | 目录与阅读顺序 | 3–6 个简短章节，保留原顺序 |
| [section-divider](../layouts/fragments/section-divider.html) | 开场与导航 | 章节过渡 | 一个章节编号及简短摘要 |
| [close](../layouts/fragments/close.html) | 开场与导航 | 结论与下一步 | 一个结论及明确的下一步行动 |
| [statement](../layouts/fragments/statement.html) | 叙述 | 一个核心观点 | 一个论点及简短支撑 |
| [executive-summary](../layouts/fragments/executive-summary.html) | 叙述 | 决策摘要、依据和行动 | 一个决策及 2–4 条支撑发现 |
| [two-column](../layouts/fragments/two-column.html) | 叙述 | 两组独立叙述 | 两个中等长度的独立文字块 |
| [three-column](../layouts/fragments/three-column.html) | 叙述 | 三组并列叙述 | 三个简短的并列内容块 |
| [longform](../layouts/fragments/longform.html) | 叙述 | 结构化正文与补充说明 | 几段简短正文及一个侧栏 |
| [bullets](../layouts/fragments/bullets.html) | 叙述 | 无序发现或要点 | 3–5 个简短要点，不编造先后次序 |
| [numbered-list](../layouts/fragments/numbered-list.html) | 叙述 | 排名或有序要点 | 3–5 个有序要点，保留提供的顺序 |
| [todo-checklist](../layouts/fragments/todo-checklist.html) | 叙述 | 行动、负责人和完成状态 | 3–5 项行动，明确状态与负责人 |
| [comparison](../layouts/fragments/comparison.html) | 对比 | 按相同标准比较证据 | 两个可比较的方案，使用一致标准 |
| [pros-cons](../layouts/fragments/pros-cons.html) | 对比 | 同一选择的优点和限制 | 两组相对平衡的内容，不混成不同方案 |
| [versus](../layouts/fragments/versus.html) | 对比 | 两个主要指标的对照 | 两个带单位、口径一致的数值及依据 |
| [stat-highlight](../layouts/fragments/stat-highlight.html) | 指标 | 一个主要指标及其含义 | 一个突出数值及简短解释 |
| [kpi-grid](../layouts/fragments/kpi-grid.html) | 指标 | 一组并列指标 | 每行 2–4 个简短指标，更多内容需调整 |
| [dashboard](../layouts/fragments/dashboard.html) | 指标 | 指标、诊断及建议 | 一行简短指标及两个简短诊断块 |
| [scorecard](../layouts/fragments/scorecard.html) | 指标 | 评估标准、分数和状态 | 若干评分项，注明单位与阈值 |
| [period-comparison](../layouts/fragments/period-comparison.html) | 指标 | 两个时期与变化口径 | 两个时期及一个可比较的变化值 |
| [actual-vs-target](../layouts/fragments/actual-vs-target.html) | 指标 | 实际值与明确目标 | 实际值、目标和差异，单位一致 |
| [metric-deep-dive](../layouts/fragments/metric-deep-dive.html) | 指标 | 指标、趋势及驱动因素 | 一个指标及 2–3 个解释因素 |
| [table](../layouts/fragments/table.html) | 明细 | 相同表头下的记录 | 从 3–6 列、简短记录开始，实测内容适配 |
| [detail-summary](../layouts/fragments/detail-summary.html) | 明细 | 明细记录与简短结论 | 一个紧凑表格及一条支撑结论 |
| [case-study](../layouts/fragments/case-study.html) | 叙述 | 情境、干预和结果 | 一个案例，保留证据与因果限定 |
| [big-quote](../layouts/fragments/big-quote.html) | 叙述 | 一段署名引言 | 一段简短引用及其出处 |
| [quote-cards](../layouts/fragments/quote-cards.html) | 叙述 | 多个有出处的观点 | 2–3 段简短引用，不编造背书 |
| [process-steps](../layouts/fragments/process-steps.html) | 时间与流程 | 有明确联系的有序方法 | 3–4 个有序阶段，明确阶段关系 |
| [timeline](../layouts/fragments/timeline.html) | 时间与流程 | 按时间排序的事件 | 3–5 个事件，保留真实日期与顺序 |
| [roadmap](../layouts/fragments/roadmap.html) | 时间与流程 | 未来阶段及交付项 | 三个时间阶段，区分承诺与提议 |
| [gantt](../layouts/fragments/gantt.html) | 时间与流程 | 同一时间尺度上的任务区间 | 少量任务，明确起止日期与共享尺度 |
| [flow-diagram](../layouts/fragments/flow-diagram.html) | 关系图 | 有方向的分支与状态流转 | 3–6 个节点，只绘制有依据的联系 |
| [arch-diagram](../layouts/fragments/arch-diagram.html) | 关系图 | 系统、边界和接口 | 少量组件与明确接口，不暗示无依据的因果 |
| [mindmap](../layouts/fragments/mindmap.html) | 关系图 | 一个主题及其下级分支 | 一个根主题及少量标注分支 |
| [image-left](../layouts/fragments/image-left.html) | 图片 | 左侧图片证据与右侧叙述 | 一张有意义的图片及简短支撑文字 |
| [image-right](../layouts/fragments/image-right.html) | 图片 | 先叙述、后图片证据 | 简短叙述及一张有意义的图片 |
| [image-hero](../layouts/fragments/image-hero.html) | 图片 | 一张主要证据图片 | 一张提供的图片，不编造装饰素材 |
| [image-grid](../layouts/fragments/image-grid.html) | 图片 | 一组相关视觉内容 | 3–6 张相关图片及说明 |
| [team](../layouts/fragments/team.html) | 商业信息 | 人员、角色及职责 | 少量真实人员，不编造人物资料 |
| [pricing](../layouts/fragments/pricing.html) | 商业信息 | 可比较的方案和价格 | 2–3 个方案，带价格、单位及限定条件 |
| [chart-bar](../layouts/fragments/chart-bar.html) | 图表 | 在同一数值基线上比较大小 | 少量类别，使用共享尺度 |
| [chart-line](../layouts/fragments/chart-line.html) | 图表 | 数值随时间变化 | 少量有日期的观测值，保留缺口和单位 |
| [chart-pie](../layouts/fragments/chart-pie.html) | 图表 | 非负整体的构成 | 少量分项，明确总和与分母 |
| [chart-radar](../layouts/fragments/chart-radar.html) | 图表 | 多个可比较维度 | 明确归一化方式的可比较维度 |
| [stacked-bar](../layouts/fragments/stacked-bar.html) | 图表 | 可比较总量中的分项贡献 | 少量类别及标注系列，保留分段之和 |
| [waterfall](../layouts/fragments/waterfall.html) | 图表 | 两个总量间的正负贡献 | 起始总量、正负贡献及结束总量 |
| [funnel](../layouts/fragments/funnel.html) | 图表 | 连续阶段的量与分母 | 3–5 个真实阶段，区分数量和转化率 |
| [heatmap](../layouts/fragments/heatmap.html) | 图表 | 数值强度矩阵 | 紧凑矩阵，按用户配色绑定有量化含义的色阶 |
| [scatter-plot](../layouts/fragments/scatter-plot.html) | 图表 | 两个数值维度 | 少量观测值，明确单位与可比较坐标轴 |
| [bubble-chart](../layouts/fragments/bubble-chart.html) | 图表 | 两个坐标及第三个大小维度 | 第三个非负量由面积而非半径表达 |
| [forecast-scenarios](../layouts/fragments/forecast-scenarios.html) | 分析 | 明确条件的未来情景 | 少量情景，不把预测当成已观测结果 |
| [risk-recommendations](../layouts/fragments/risk-recommendations.html) | 分析 | 信号与可追责的应对 | 2–3 项有依据的风险、负责人及下一步 |
| [methods-definitions](../layouts/fragments/methods-definitions.html) | 分析 | 定义、计算公式与边界 | 少量定义或公式，注明单位及排除项 |
| [appendix-index](../layouts/fragments/appendix-index.html) | 开场与导航 | 参考资料与支持材料 | 少量真实引用，保留原始标识 |
