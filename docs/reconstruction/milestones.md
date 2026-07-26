# 修订后的最小稳定化 milestones

## 全局实施约束

- 每个代码 milestone 测试通过后单独提交一个 commit；前一个 milestone 未通过时不得进入下一个。
- 新增或修改的代码注释和 docstring 使用规范英文。
- 不做未列入本计划的兼容层、fallback、heuristic 或顺手重构。
- 遇到会改变正式方法、评测语义、事实口径或无法安全恢复的高危设计问题时停止实施并报告。
- `question_targets_mutable_fact` 目前仍被 `route1_validators.py` 导入，而 Route 3 启动又可能通过旧的顶层 import 加载 Route 1 模块。删除该函数时，必须同步移除旧模块中的 import/use，确保 Route 3 启动不因历史依赖中断；除此之外不修复 Route 1。

## M0：冻结正式设计、历史边界和保留工具

### 工作

更新：

- `AGENTS.md`
- `docs/design.md`
- `docs/default_settings.md`
- `docs/contract.md`
- `docs/compatibility_legacy_settings.md`

明确：

- Route 3 是唯一正式生成路线；
- recipe 是唯一用户入口；
- worker 是内部 segment 执行器；
- Route 1/2、KELM 和旧 finalization 是历史代码；
- 本轮新增列出的旧 rule-based gates 均不属于正式方法。

特别保留：

- `scripts/run_openrouter_batch_predictions.py`
- `scripts/judge_openrouter_batch_predictions.py`

两者是正式保留的 SimpleQA Verified 风格评测工具，但不属于 Route 3 数据生成或 finalization。

不得修改：

- `judge_openrouter_batch_predictions.py` 中的 `GRADER_TEMPLATE`；
- `run_openrouter_batch_predictions.py` 中模型接收问题的 prompt/message 构造；
-判分标签、prompt 示例、默认不可解析映射等 SimpleQA Verified 判分语义。

### 验证

- 当前文档不再把旧 gate 描述为正式 Route 3 方法；
- 两个 OpenRouter 脚本仍被列为保留工具；
- generation、人工审核和 finalization 不会调用这两个批量评测脚本。

### 停止条件

- 文档仍把旧 finalization、KELM 或已删除 gates 写成正式方法；
- 两个评测脚本被错误归为待删除历史代码；
-评测 prompt 被计划性“整理”或改写。

---

## M1：定义字段、ID 和 artifact schema

### Stable candidate ID

ID 由以下不可变字段构造：

```text
run_group_id
+ segment_id
+ canonical_page_id
+ original_candidate_slot
```

- single 使用固定 slot；
- all5 使用原 answer-type slot；
-人工修改 Q/A 不改变 ID；
- top-up 使用新 segment ID；
- final CSV 沿用该 ID。

### 不可变 provenance

保留：

- run/segment/page attempt；
- canonical page ID/URL；
- selected table 和 table type；
- page archive hash；
- generation prompt/request/raw response；
-原始 Q/A、aliases、search queries；
- answer type；
- generation model/参数；
- recipe seed。

### Revision 字段

保存：

- revision number；
- authoritative question/reference answer；
- active aliases/search queries；
- topic；
- delete flag；
- edit reason；
- source validation；
- integrated answer-type gate；
- DDG；
- second-stage answers/grading；
- accepted/rejected/rerun 状态。

### 人工编辑字段规则

- 人工 question 为唯一 authoritative question；
-旧 canonical/rewritten question 不得覆盖人工输入；
-只改 question：保留 answer、aliases 和 search queries；
-改 reference answer：清空 active aliases；
-原 answer/aliases 仅保留在 revision history；
-修改必须仍是同一 selected-table fact；
-改问其他事实必须删除并重新 generation；
-清空旧 DDG/second-stage 结果后重跑；
- selected table、answer type、candidate ID 不变。

### 验证

schema round-trip 覆盖：

- single/all5；
- question-only edit；
- answer-only edit；
- Q/A 同时修改；
-删除；
-多轮 revision。

### 停止条件

- ID 随编辑变化；
-原始 generation audit 被覆盖；
-修改后仍使用旧 aliases、DDG 或 grading；
- selected-table evidence 丢失。

---

## M2：收紧正式入口、固定方法并清理旧 gates

### M2.1 唯一入口和正式参数

唯一用户入口：

- `run_wikipedia_infobox_recipe.py`

内部 worker：

- `run_wikipedia_infobox_pipeline.py`

保留用户配置：

- `page-attempt-count`；
- answer type；
- single/all5；
- infobox/wikitable/both；
- generation model/max tokens；
- cache reuse/fresh；
- run ID、seed；
-并发和网络运行参数。

合法组合：

- specific answer type 只能 single；
- `AllTypes` 只能 all5；
-禁止 specific answer type + all5。

`page-attempt-count` 表示 primary page 数，不表示 accepted QA 数；自动 rerun 不额外消耗 primary page budget。

### M2.2 正式默认值

```text
generation_model = google/gemini-3-flash-preview
generation_max_tokens = 4096
reasoning_type = single_fact
second_stage_enabled = true
second_stage_threshold = 0.1

second_stage_answer_models:
  openai/gpt-4.1-mini
  google/gemini-3-flash-preview

second_stage_grader:
  openai/gpt-4.1-mini

cache_reuse = all
cache_fresh = fill
page_source = table-search
search_query = insource:"wikitable"
```

保留当前 DDG、second-stage、table filters 和 prose-leakage 的正式参数值。

### M2.3 删除旧功能接口

从正式 recipe/worker 删除：

- KELM rewrite 和隐藏 `--enable-rewrite`；
- LLM table choice；
- reasoning-type 参数；
- extra prompt；
- pageview prefilter；
- broad/custom/random page discovery；
- REST first-paragraph fallback；
- table filter 开关；
- prose-leakage 开关；
- minimum table score 参数；
- URL-list；
-旧 validation CLI。

内部固定：

-当前 table filter modes 开启；
- prose-leakage scoring 开启；
- minimum table score 使用当前值。

### M2.4 删除指定旧 rule-based gates

删除下列代码、输出字段、兼容处理、对应测试和当前文档说明：

1. `preferred_table_context`
2. `no_oversized_tables`
3. `person_common_words_minus_common_names`
4. `question_unambiguous`
5. `stable_answer`
6. `rewrite_guard_passed`
7. `high_sitelink_count`
8. `high_claim_count`
9. `relation_family_not_allowed`
10. `short_subject_label`
11. `wikipedia_infobox_incomplete_tie_answer`
12. `question_targets_mutable_fact`
13. `_uses_generic_table_source_wording`

具体边界：

#### `preferred_table_context`

这是当前仍会增加 `+2.5` table score 的 ranking signal，不只是占位字段。删除：

- `PREFERRED_TABLE_HINTS`；
- `preferred_context_hits` 计算；
- `+2.5` score；
- ranking reason；
- metadata 输出。

这是本轮明确授权的 table ranking 行为变化。其他 ranking/filtering 保持不变。

#### `no_oversized_tables`

当前只剩常量和未调用的 table-size rejection helper。删除：

- oversized reason 常量；
-未调用 helper；
-对应测试/import。

不新增替代 gate。

#### `person_common_words_minus_common_names`

删除 Person common-word/common-name gate：

- Person 不再因该 ratio 被拒绝；
-不新增替代 heuristic；
-其他 answer-type gates 保留；
- Person 仍需通过 source validation、DDG 和 second-stage。

#### `question_unambiguous`、`stable_answer`、`rewrite_guard_passed`

从 Route 3 validation 输出和合取判定中删除。

Route 3 的 shared validation 保留真正有效的：

- `answer_in_evidence`；
- selected-table provenance；
-已有 generation pipeline surface/time checks。

特别注意：

- 删除 `rewrite_guard_passed` 字段，不等于删除实际 surface validation；
-删除 `stable_answer` 占位，不等于允许 live/current 问题；
-正式的 temporal/current wording guards 继续保留。

#### popularity/relation/short-label gates

删除：

- `run_fact_level_longtail_prefilter`；
- `build_removed_prefilter_stub`；
- `prefilter_longtail_features` 的占位赋值；
- sitelink/claim/relation/short-label rule 输出；
-对应测试和文档。

Route 3 长尾判断只保留正式 DDG 和 second-stage。

#### `wikipedia_infobox_incomplete_tie_answer`

删除：

- `_tie_completion_problem`；
- warning metadata；
- `SOURCE_STAGE_NON_BLOCKING_NOTES` 兼容；
- worker 中旧 rejected-record 恢复逻辑；
- walkthrough/summary 特殊处理；
-对应测试。

不新增替代 tie detector。

#### `question_targets_mutable_fact`

删除：

- `validators.py` 中函数；
- `generator_validators.py` import；
- `route1_validators.py` import/use；
-对应单元测试。

但保留 Route 3 当前真正执行的：

- post-generation temporal/live wording checks；
- `validate_question_surface` 中仍有效的时间和 mutable-status 限制；
- AGENTS.md 的 current/latest/live-status 政策。

#### `_uses_generic_table_source_wording`

删除 dead helper 以及仅由它使用的 import、regex/常量。它当前未被调用，不改变行为。

### M2.5 固定自动化流程

```text
table/source checks
→ generation
→ parse/normalize
→有效 surface/time guards
→ integrated answer-type gate（不含 Person common-word gate）
→ answer-in-selected-table validation
→ DDG
→ second-stage grading
```

DDG 和 second-stage 错误进入 rerun。

### M2.6 移除过早去重

从 `process_generated_candidates` 移除：

- `seen_subject_resources`；
-局部 exact-question 去重。

页面级去重只在人工审核后的 finalization 执行。

### 验证

新增或调整测试：

- `preferred_table_context` 不再影响 table score/order；
- no oversized helper 不存在；
-原先只因 Person common-word gate 失败的 candidate 不再被该规则拒绝；
- Route 3 validation 只保留实际有效检查；
-旧 popularity/relation/short-label prefilter 不再生成 metadata；
- incomplete-tie warning 不再出现；
- `_uses_generic_table_source_wording` 不存在；
- `question_targets_mutable_fact` 删除后 Route 3 import/startup 正常；
-删除上述函数后 temporal/current 问题仍被现有正式 guards 拒绝；
- all5 同页面候选不会被提前 dedup；
- prompt 内容未改变；
-除 `preferred_table_context` 和明确删除的 gates 外，table ranking/filtering baseline 不变。

### 停止条件

- 删除旧函数导致 Route 3 import 失败；
-删除 `stable_answer` 等占位时误删实际 temporal/surface guards；
- Person candidate 被新的未批准 heuristic 替代拒绝；
- `preferred_table_context` 残留在 score 或 metadata；
- DDG/second-stage 顺序变化；
- generation prompt 出现非预期改变。

---

## M3：实现最小可靠运行、resume 和 page lifecycle

### 权威层次

正式 Route 3 运行使用四层对象：

1. `segment_manifest.json`：固定 fingerprint 和 target，并记录派生的 segment 状态；
2. immutable page allocation：定义该 segment 消耗的 primary-page budget；
3. page attempt 和外部调用记录：记录页面执行、不可安全重复的调用和恢复位置；
4. accepted/rejected/summary/state：全部是可重建的派生输出或运行时缓存。

`state` 不得创建、删除或重新解释 page allocation，也不得成为 retry、resume 或 top-up 的事实来源。

### Segment fingerprint

包含：

- Git SHA；
- prompt hash；
- resolved result-affecting config；
- model/max tokens；
- answer/source mode；
- `page-attempt-count`；
- seed；
- cache policy；
- table ranking/filter 配置；
- DDG；
- second-stage。

正式运行要求 clean worktree。

### 复用规则

```text
same fingerprint + complete
→ reuse

same fingerprint + incomplete
→ resume original segment and attempts

different fingerprint
→ new run or explicit top-up segment
```

旧 schema 的 incomplete segment 不提供兼容 resume 或自动迁移。

### Allocation 和 attempt

```text
page allocation
├── attempt001：primary execution
└── attempt002：the only allowed page-level rerun
```

- primary-page 数量由 unique allocations 计算，不由调度路径传入布尔字段；
- allocation 已提交但尚未开始的页面在 resume 后继续 `attempt001`；
-中断本身不创建新 attempt；
-只有明确、已记录的 DDG/OpenRouter infrastructure failure，或用户明确授权重试的 ambiguous OpenRouter call，可以创建 `attempt002`；
- retry 资格从 ledger 推导并跨进程生效；
-不得创建 `attempt003`；
- unexpected Python exception 使 segment 保持 incomplete 并报告，不得自动归入 rerun；
- all5 的 slots 在同一个 terminal page attempt 中原子提交。

Terminal attempt 保存：

- generation raw audit；
-全部 single/all5 candidates；
- DDG；
- second-stage；
- accepted/rejected/retry outcome；
- candidate IDs；
- timings；
-所引用的外部调用记录。

### 最小持久化边界

正式运行只持久化不能安全、廉价重算的边界：

```text
immutable allocation
→ Wikipedia page archive
→ OpenRouter call intent/response records
→ DDG candidate-verifier result
→ terminal page-attempt ledger
```

- page preparation 和 deterministic validation 是便宜的本地确定性计算，不建立独立 checkpoint；
- resume 或 attempt002 通过稳定 call/result key 复用已完成的外部调用，不无条件重复 generation、DDG 或 model calls；
-独立 artifact 使用同目录唯一临时文件，关闭后通过 `os.replace` 发布；本阶段不以断电后的文件系统持久性为目标，不要求每个 artifact 做 `fsync`；
- archive hash 写入 provenance，OpenRouter request hash 绑定 request intent 和 response；不建立通用 stage hash graph。

### State、索引和派生输出

- worker 启动时扫描 allocation/attempt ledger 一次并建立内存索引；
- page commit 在锁内更新索引，不得每页重新扫描完整 ledger；
- accepted/rejected/summary 在启动恢复、批次边界或 segment 结束时重建，不得每页全量重写；
- discovery state 只保留 offset 和非权威 telemetry；
- committed terminal page 不重复任何已持久化外部调用。

### 运行模式

- initial run：新 run-group、新 segment；
- resume：同 segment、同 fingerprint，继续原 allocations/attempts；
- rerun：同 allocation 的 `attempt002`，不是独立 run mode；
- top-up：同 run-group、新 segment，只分配从未分配过的新页面。

### 验证

- allocation 后、attempt 前中断仍恢复为 `attempt001`；
-外部 response record 持久化后中断不重复调用；
- terminal ledger 后、projection 前中断可完整重建；
- fingerprint 改变拒绝复用；
-跨多次 resume 仍最多一个 `attempt002`；
- top-up 不修改旧 segment 且不重复旧 page ID；
- 2000 个 mocked allocations 不产生逐页全 ledger 扫描或全 JSONL 重写。

### 停止条件

- state 比 allocation/attempt ledger 权威；
-中断预留页被归为 rerun；
- retry 次数在新进程中重置；
- unexpected exception 被 blanket catch 后自动重试；
-不同 fingerprint 被复用；
- top-up 覆盖或修改旧 segment；
- page commit 仍有明显的 O(N²) 全量扫描/重写路径。

---

## M4：人工审核前数量预测

自动化 accepted 产生后，写入 manifest：

- accepted 总数；
- canonical unique pages；
-多 QA pages；
-页面分配后的各 answer-type 数量；
- rebalance `N`；
-各类预计最终目标；
-预计最终总数。

页面分配规则：

-单 QA page 直接计数；
-多 QA page 按 canonical page ID 升序；
-只在页面实际存在的 answer types 中选择；
-优先当前去重后数量较少的类型；
-再比较人工审核前去重前总 QA 数；
-再用 recipe seed；
-每次分配后更新数量；
-同页同类型多条时按较低 DDG overall hit rate，再按 candidate ID。

这里只预测数量，不做 topic 题目选择。

### 验证和停止条件

-输入顺序不影响结果；
- seed 被记录；
-不能把页面分给不存在的 answer type；
-预测不得提前执行具体 topic 删除。

---

## M5：建立人工审核循环

### 每个 run 的 Markdown

仅展示 accepted：

- stable candidate ID；
- question/reference answer；
- answer type；
- Wikipedia URL/page ID；
- Markdown selected table；
- Markdown two-model answers；
-自动 topic；
-自动 `human_edited`。

每个 Markdown 文件最多写 50 个 QA，后缀使用实际的首尾编号。例如 68 个 QA：

```text
review_1-50.md
review_51-68.md
```

两个小模型分别使用独立标题；model response 和 judge reason 分别转为 blockquote，不能让回复自身的 Markdown 与 review 文档结构混合。

### 自动 topic 分类

在生成 Markdown/XLSX 前，用 `openai/gpt-4.1-mini` 根据 question 和 reference answer 选择一个正式 topic：

- temperature `0`；
- max tokens `256`；
- bounded concurrency；
- prompt 要求只返回十项枚举中的一个精确标签；
-调用 Route 3 durable OpenRouter executor；
- review state 保留 request、完整原始 response、raw text 和 parsed topic；
- durable response record 保留原始 HTTP body；
-非法回复直接把 candidate 标为 rejected，不重试、不 fallback、不进入 review MD/XLSX。

### Statistics JSON

生成 Markdown/XLSX 时，在 XLSX 同目录写入 `statistics.json`：

-人工审核前原始 QA 总数；
-各 answer type 原始数量和百分比，百分数保留两位小数；
-预计最终 QA 总数和各 answer type 数量。

如果原始 QA 中至少一个 answer type 数量为 0，则跳过预测，并在 JSON 和 CLI 输出中列出缺失类型及风险。


### XLSX 规范英文列名

列严格改为：

```text
id
question
reference_answer
wikipedia_url
topic
human_edited
delete
edited_question
edited_reference_answer
edit_reason
```

不再使用中文列名。

规则：

- `delete` 默认 `No`；
-可选 `Yes/No`；
- `topic` 由 GPT-4.1-mini 自动填写，XLSX 只读展示，不提供下拉；
- `human_edited` 由 revision history 自动填写，默认 `No`，人工修改 Q/A 后为 `Yes`，不得人工修改；
-进入 finalization 前 topic 必须完整合法。

Topic 枚举：

```text
Science & technology
Politics
Art
Other
Geography
Sports
Music
TV shows
History
Video games
```

### XLSX 校验

拒绝：

-重复/未知 ID；
-非法 topic；
-finalization 时空 topic；
-人工修改 topic；
-人工修改 `human_edited`；
-非法 delete 值；
- `delete=Yes` 同时存在 edited Q/A。

允许：

-只改 question；
-只改 reference answer；
-同时修改两者。

### Revision 循环

-删除行不再验证；
-编辑行创建 revision；
-按 M1 字段规则重建 active candidate；
-重新执行 generation 后 checks、DDG 和 second-stage；
-对最新 accepted revision 重新执行 topic 分类；
-生成新 MD/XLSX；
-直到没有 Q/A 编辑。

### 验证

-列名和顺序精确匹配；
- delete 默认 No；
- round-trip 不改变 ID；
- topic 没有下拉且人工修改会被拒绝；
- `human_edited` 初始为 No，Q/A 编辑后为 Yes；
-每个 Markdown shard 最多 50 题且后缀范围正确；
-两个模型的 response/reason 不会污染 Markdown 结构；
- topic 原始 OpenRouter response 可审计；
-非法 topic response 不进入 review；
- answer 编辑清空 aliases；
-旧 DDG/grading 不复用；
- revision history 完整；
-只有最新 accepted 出现在下一轮 MD/XLSX。

### 停止条件

-仍生成中文列；
-列名被自动本地化；
-修改后未重跑完整 post-generation pipeline；
- topic 或 `human_edited` 可由人工改写；
- topic raw response 未持久化；
-原始 generation 数据被覆盖。

---

## M6：正式 finalization

### 运行条件

-无未处理编辑；
-无 rerun；
-全部 active rows 有合法 topic；
- XLSX ID 与 candidate revision 一一对应。

### Canonical page 去重

沿用 M4 页面分配算法。

每个 canonical page 最多一题。

不使用旧：

- similarity dedup；
- subject URL dedup；
- domain round-robin。

### Answer-type rebalance

比例：

```text
Person  19.8%
Place   14.6%
Number  18.5%
Date    22.2%
Other   24.9%
```

计算：

```text
N = min(ceil(n_i / p_i))
target_i = min(n_i, ceil(N * p_i))
```

最终总数允许不等于 `N`。

如果页面去重后至少一个 answer type 数量为 0，则跳过 answer-type rebalance，直接输出页面去重后的全部 candidates，避免空 CSV。

### Topic 多样性

全局迭代：

-只从超额 answer type 删除；
-优先全局数量最大的 topic；
-并列使用 recipe seed；
-每次删除后更新全局数量；
-不拟合 answer-type × topic 分布。

### CSV

严格为：

```text
id
problem
answer
topic
answer_type
urls
```

`urls` 为 JSON 数组字符串。

### 验证和停止条件

-每页最多一题；
-各类达到 target；
-相同 seed 可复现；
-输入顺序不影响结果；
-所有 ID 可追溯；
-旧 `final_selection.py` 不能被调用。

---

## M7：保护 SimpleQA Verified 批量评测工具

这是新增的独立里程碑，避免在 Route 3 清理时误伤评测代码。

### 工作

保留且不重构：

- [run_openrouter_batch_predictions.py](D:/Study/AI/My-research/Wikidata_Framework/scripts/run_openrouter_batch_predictions.py)
- [judge_openrouter_batch_predictions.py](D:/Study/AI/My-research/Wikidata_Framework/scripts/judge_openrouter_batch_predictions.py)

明确它们的角色：

```text
final CSV / evaluation input
→ run_openrouter_batch_predictions.py
→ model predictions
→ judge_openrouter_batch_predictions.py
→ SimpleQA Verified grading
```

它们不是：

- generation filter；
- second-stage filter；
-人工审核；
-finalization。

### Prompt 保护

增加一个最小 regression test，但不修改脚本 prompt：

-固定 `GRADER_TEMPLATE` 的完整 snapshot 或 SHA256；
-固定 `question/target/predicted_answer` 插值后的 prompt snapshot；
-固定 prediction runner 的 user-message 构造；
-固定 `A/B/C → CORRECT/INCORRECT/NOT_ATTEMPTED`；
-固定不可解析时的现有默认行为。

测试只保护现状，不抽象 prompt，也不把 prompt 移到共享模块。

### 本阶段 OpenRouter 调用层边界

- Route 3 内部允许抽取一个只执行单次物理 HTTP 请求的 thin transport；
- Route 3 generation、second-stage QA 和 GPT-4.1-mini grading 统一经过 Route 3 durable executor；
- durable executor 负责 request/response journaling、ambiguous、circuit 和 page-attempt retry policy；
- thin transport 不拥有 prompt、解析、retry、fallback、checkpoint 或 page state；
-两个独立批量评测脚本不 import Route 3 durable executor，也不在本轮迁移到统一 OpenRouter 调用层；
-批量评测脚本现有 prompt、message、retry、输出和 resume 契约保持不变；
- `run_openrouter_night_batch.py` 不再使用。

当前批量 prediction/judge 不获得 Route 3 的新 circuit 或 ambiguous 人工处置语义。尤其是 batch judge 的现有 `status=error` 结果会被相同 judge model 的 resume 视为已有结果；本轮不顺手修复。第一次正式大规模独立评测前，如果仍需要该能力，应另立最小评测稳定化 milestone，本文件不预设其 circuit、CLI 或恢复实现。

M8 rehearsal 不运行大规模独立批量评测。

### 验证

-两个脚本仍能通过 mocked OpenRouter response 测试；
- prompt hash/snapshot 完全不变；
- batch prediction 输出仍能被 judge 脚本读取；
- Route 3 生成和 finalization 测试不 import 或调用这两个脚本。

### 停止条件

- `GRADER_TEMPLATE` 任意字符变化；
-prompt 示例被缩短或格式化；
-message role/content 结构变化；
-判分映射变化；
-评测脚本被合并进 second-stage grading。

---

## M8：根治恢复漏洞并完成端到端 rehearsal

M8 先完成 Route 3 的最小稳定化，再运行真实 rehearsal。以下子里程碑必须顺序执行；每个子里程碑测试通过后单独提交一个 commit。

### M8-S0：更新正式设计契约

#### 工作

在改代码前更新 `docs/design.md`、本文件和相关 contract/runbook 描述：

-删除“stale in-progress 自动进入 rerun pool”；
-删除“top-up 搬运旧 rerun pool”；
-定义 allocation、attempt、外部调用记录和 terminal ledger；
-定义 initial run、resume、rerun、top-up 的条件和顺序；
-定义 OpenRouter ambiguous、批量人工处置和 circuit；
-定义 DDG candidate-verifier result 和 circuit；
-定义 batch prediction/judge 不接入 Route 3 durable executor；
-明确独立夜间评测编排脚本不再使用。

#### 验证

-正式文档不存在相互冲突的 retry/top-up 语义；
- `git diff --check` 通过。

#### Commit

```text
docs(reconstruction): define durable page lifecycle
```

#### 停止条件

-设计仍允许 state 或 generic rerun pool 决定页面身份；
-批量评测 prompt/判分语义被纳入改写范围。

### M8-S1：建立 page allocation、attempt schema 和 ledger index

#### 工作

在 `route3_run_ledger.py` 中建立：

- immutable page allocation；
- page-attempt schema v2；
- segment-level in-memory ledger index；
-从 allocation 推导 primary-page 数量；
-从最高 attempt 推导页面状态；
- manifest 状态：`incomplete` 或 `complete`，并用 `blocking_reasons` 集合记录 `external_service` 和/或 `ambiguous`。
- `status` 和 `blocking_reasons` 从 allocation、attempt 和 external-call records 派生，不得自行创建 allocation 或 retry。

Allocation 至少保存：

```text
run_group_id
segment_id
canonical_page_id
allocation_ordinal
page_source: cache | fresh
allocated_at
```

`attempt001` 从 schema 推导为 primary；`attempt002` 推导为唯一 rerun。旧 schema 的 incomplete segment 明确拒绝 resume，不添加 migration fallback。

启动时只扫描一次 allocation/attempt 文件并建立索引；每次 commit 在锁内更新索引。删除逐页 `load_page_attempts()` 和逐页全量 JSONL rebuild 的 O(N²) 正式路径。accepted/rejected/summary 只在恢复、批次边界或 segment 结束时重建。

#### 验证

-同 run-group/page ID 不能重复 primary allocation；
- allocation 无 attempt 时是 pending primary；
- `attempt001/002` 类型推导正确；
- 2000 个 mocked allocations 只做一次启动扫描；
- schema v1 incomplete segment 被拒绝。

#### Commit

```text
refactor(route3): separate page allocations from attempts
```

#### 停止条件

- primary-page 数量仍依赖调用方布尔字段；
- state 能创建或释放 allocation；
- page commit 仍全量扫描 ledger 或重写完整 endpoints。

### M8-S2：建立最小持久化与提交边界

#### 工作

正式运行只建立以下持久化边界：

```text
allocation record
→ Wikipedia page archive
→ external-call records
→ terminal page-attempt ledger
→ derived projections
```

要求：

- page preparation 和 deterministic validation 不建立独立 checkpoint，可在同一 attempt 内安全重算；
- all5 使用稳定 slot key，并在一个 terminal page attempt 中提交；
- attempt002 通过稳定 call/result key 和 request hash 复用已完成的外部调用；
-独立 artifact 使用同目录唯一临时文件，关闭后以 `os.replace` 发布；不为所有本地阶段增加 `fsync`；
- terminal page-attempt ledger 是页面结果的权威来源；
-不建立通用 stage hash graph、stage lock registry 或确定性本地阶段 checkpoint。

#### 验证

- allocation 后中断仍恢复为 `attempt001`；
-外部 response 已持久化后中断不产生重复调用；
- terminal ledger 后、projection 前中断可从 ledger 重建；
- deterministic local work 中断后可重算，且不创建 `attempt002`。

#### Commit

```text
feat(route3): establish minimal durable boundaries
```

#### 停止条件

- attempt002 无条件重新 generation；
- all5 slot 跨 terminal attempts 混合提交；
- summary/state 覆盖已提交 terminal ledger；
-新增通用 stage checkpoint/hash graph。

### M8-S3：建立 Route 3 thin OpenRouter transport 和 durable executor

#### 调用层边界

Thin transport 只负责：

```text
send_once(payload)
→ one physical HTTP request
→ raw response or typed transport error
```

Thin transport 不拥有 prompt、解析、retry、fallback、checkpoint、circuit 或 page state。

Route 3 durable executor 负责：

- request intent；
- raw response/explicit HTTP error 原子落盘；
- request hash 和 call key；
- ambiguous 分类；
- circuit integration；
- page-attempt retry policy。

覆盖：

- Gemini 3 Flash generation；
- second-stage QA calls；
- GPT-4.1-mini grading calls。

删除 low-integer answer 的额外 GPT-4.1-mini snippet judge；Number candidates 与其他答案类型执行相同的 DDG long-tail verification，不增加替代 heuristic。

正式 Route 3 不允许 OpenRouter client 内部隐藏重试、代理转直连或模型 fallback。当前未启用的 rewrite 不顺手扩展。批量 prediction/judge 不 import 该 executor。

稳定 call key：

```text
generation
second_stage_answer/<slot>/<model>
second_stage_grade/<slot>/<answer-model>
revision/<revision-number>/second_stage_answer/<slot>/<model>
revision/<revision-number>/second_stage_grade/<slot>/<answer-model>
```
call key 属于 allocation 下的 logical call，不包含 attempt number，使 `attempt002` 可以复用 `attempt001` 已完成的相同请求。原始 candidate 使用前三种 key；人工编辑产生的新 revision 使用 revision namespace，避免改变后的 request 与原始 request 发生 hash 冲突。

调用顺序：

```text
persist intent
→ send once
→ immediately persist raw response or explicit HTTP error
→ return to caller
```

#### 状态语义

-无 intent：可调用；
- response 已持久化：直接复用；
-明确 HTTP error 已持久化：definite outcome，再按 status code 分类为 retryable 或 non-retryable failure；
- intent 存在但无 response：`ambiguous_external_call`；
- raw response 存在但解析失败：确定性 rejection，不重试。

#### 验证

Mock：

- intent 前崩溃；
- intent 后、发送前崩溃；
-请求可能送达但无响应；
-响应返回后、写盘前崩溃；
-响应写盘后、page ledger 前崩溃；
-明确 429；
-不可解析模型文本；
-同 call key resume 不产生第二次物理调用；
-protected evaluation prompt/message snapshot 完全不变。

#### Commit

```text
feat(route3): journal OpenRouter calls durably
```

#### 停止条件

-一个 formal logical call 仍能在 ledger 不知情时执行多次；
- API key 或 secret 写入 artifact；
- protected evaluation prompt、labels 或 unparseable mapping 改变。

### M8-S4：持久化 DDG candidate-verifier result

#### 工作

以 candidate 为边界持久化 long-tail verifier 结果：

- key 由 allocation、candidate slot 和 segment fingerprint 构造；人工编辑后的结果额外包含 revision number；
- verifier 完成后一次保存最终 decision，以及完整 query strings、titles/snippets/URLs 和 request audit；
- resume 复用已完成的 candidate-verifier result；
- verifier 中途被打断时只重跑当前 candidate 的有限 query 集合；
-保留现有 DDG endpoint、bounded retry、cooldown 和 fallback 顺序；
-不增加 query-level checkpoint、新搜索 fallback 或 cheap-model rejection gate。

DDG 是只读且不计费的，因此进程中断后重复当前 candidate 的少量查询是可接受边界。它不使用 OpenRouter 的 intent-without-response 人工 quarantine；已完成的 candidate-verifier result 不得因 page resume 重跑。

#### 验证

-三个 candidates 在第二个 verifier 中断，resume 复用第一个、重跑第二个 verifier，再执行第三个；
-已持久化 candidate result、audit 和排序不变；
-正常 long-tail reject 不进入 retry/circuit；
-现有 DDG client 耗尽有限尝试后产生 typed infrastructure failure；
-query 文本和阈值不变。

#### Commit

```text
feat(route3): persist DDG verifier results
```

#### 停止条件

- resume 重跑已完成 candidate 的 DDG verifier；
-为每条 DDG query 建立独立 checkpoint；
-新增 fallback 或 heuristic；
-内容 rejection 被计为网络故障。

### M8-S5：加入 OpenRouter/DDG circuit 和 ambiguous 批量处置

#### Circuit 范围

只实现两个 circuit：

```text
openrouter
duckduckgo
```

连续基础设施失败阈值固定为 3，并记录在 manifest/summary；本阶段不暴露阈值调节 CLI。一个成功操作清零对应 service 的连续失败计数。

OpenRouter：

- `401/402` 第一次即打开 circuit；
- `403` 是当前调用的 definite non-retryable failure，不自动重试，也不单独打开全局 circuit；
-明确 `408/429/5xx` 和 transport ambiguity 计入连续失败；
- circuit 打开后不启动新 OpenRouter calls。

DDG：

-只有逻辑 verifier 耗尽现有有限 transport 尝试后才计为 infrastructure failure；
- circuit 打开后不启动新 DDG verifier calls。

Circuit 打开时：

-已在途 calls 允许落账；
-等待 calls 的页面保持原 attempt pending；
-未发送 call 不消耗 rerun；
-worker 停止分配新 pages；
-segment 保持 `status: incomplete`，并添加对应 `blocking_reasons`；
-不切换模型、endpoint、代理或新增 fallback。

Circuit 不在同一次 invocation 内自动关闭或自动恢复调用。用户确认服务恢复后，显式执行 same-fingerprint resume；新 invocation 从零开始统计连续失败，page-attempt 资格仍由既有 ledger 决定。

#### Ambiguous 人工处置

Recipe 是唯一用户入口，增加：

```text
--resolve-ambiguous retry
--resolve-ambiguous abandon
```

规则：

-参数缺省：隔离 affected allocation；circuit 未打开时继续健康页面；生成 report；segment 保持 `incomplete`、将 `ambiguous` 加入 `blocking_reasons`，且不得 complete/top-up；
- `retry`：为仍有资格的 calls 创建 `attempt002`，并记录可能重复费用；
- `abandon`：提交 `abandoned_ambiguous` terminal outcome；
-只允许在 same-fingerprint resume 中使用；
-处置动作不改变 fingerprint，但必须进入 audit；
-默认批量作用于当前 segment 的 unresolved calls；
- attempt002 再 ambiguous 时不能创建 attempt003，只能 abandon。

输出：

```text
ambiguous_external_calls.json
ambiguous_external_calls.md
```

至少包含 page/allocation/attempt、call purpose、call key、model、request hash、intent time、error、retry eligibility 和可能重复计费说明。

#### 验证

-连续 2 次失败不 trip；第 3 次 trip；成功后清零；
- OpenRouter 401/402 立即 trip；
- OpenRouter 403 终结当前调用，但不立即 trip；
-trip 后新 mocked physical calls 不增长，除已在途 calls；
-circuit-before-send 页面仍是原 attempt；
- `retry/abandon` 行为和 audit 正确；
- attempt003 永远被拒绝；
-无需逐条同步人工批准即可继续健康页面并最终批量 resolve。

#### Commit

```text
feat(route3): stop systemic external service failures
```

#### 停止条件

-circuit 通过 fallback 继续调用；
-circuit-open 页面被算作 rerun；
-人工处置需要逐 call 交互；
-未明确授权就自动重试 ambiguous call。

### M8-S6：替换 generic rerun pool 和页面调度状态机

#### 工作

正式 worker 固定顺序：

```text
rebuild ledger index
→ load and quarantine unresolved ambiguity
→ resume unfinished attempts
→ fill missing primary allocations
→ complete primary phase
→ run eligible attempt002
→ commit terminal attempts
→ rebuild projections
```

删除正式路径中的：

- generic `rerun_pool`；
- `recover_stale_in_progress()`；
-调用方 `primary_page_attempt` 参数；
-top-up rerun seed/clear；
-每次进程启动重新获得 retry；
- `except Exception → rerun`；
-accepted-target cancellation 后把未执行预留页放入 rerun。

只有 typed DDG/OpenRouter infrastructure failure 可以产生 `retryable_failure`。意外异常必须保留 traceback、使 segment incomplete 并向上抛出。

分配和 dispatch 使用有界小批次；不一次创建 2000 个 futures。预分配但未启动的页面保持 primary pending。

#### Segment complete

必须同时满足：

- primary allocation count 等于 target；
-每个 allocation 有 terminal outcome；
-无未决 external-call record；
-无 retry pending；
-无 ambiguous call；
-无 circuit-blocked 未完成工作；
-projection 可从 ledger 完整重建。

#### 验证

-预留页中断后仍执行 `attempt001`；
- retryable attempt001 只产生一个 attempt002；
-跨多次 resume 无 attempt003；
-circuit-open page 不消耗 retry；
-unexpected exception 不进入 retry；
-all5 slots 原子终结。

#### Commit

```text
refactor(route3): derive reruns from attempt history
```

#### 停止条件

-裸 page-ID list 仍同时表达多种 rerun 原因；
-resume/top-up 调度路径能够自行指定 primary/secondary；
-意外代码错误被自动重试。

### M8-S7：统一 cache、resume 和 top-up 去重

#### 工作

唯一性由 run-group allocations 统一提供：

```text
eligible cache
= cached archive IDs
- current segment allocations
- all prior run-group allocations
```

Fresh discovery 在 allocation 前使用同一排除集合。

Top-up：

-要求旧 segments complete；
-要求 generation protocol compatibility fingerprint 一致；
-新 segment ID；
-只分配 run-group 从未分配的新页面；
-不读取、转移或清空旧 rerun/state；
-不修改任何旧 segment；
-rejected、retry_exhausted、abandoned pages 仍属于旧 allocation，不能重新抽取。

`state` 只保留 discovery offsets 和非权威 telemetry。

#### 验证

-同 segment cache resume 不重复；
-cache/fresh 不会分配同一 page ID；
- 20-page initial segment 加 10-page top-up 得到 30 个 unique allocations；
-旧 rejected/abandoned pages 不进入 top-up；
-旧 segment files 在 top-up 前后 hash 不变。

#### Commit

```text
fix(route3): enforce run-group page uniqueness
```

#### 停止条件

-cache 和 fresh 使用不同的唯一性来源；
-top-up 修改旧 segment；
-top-up 重新引入旧失败页面。

### M8-S8：修复 recipe projection、CLI 和根目录 runbook

#### 工作

-修复 `accepted_records` 在赋值前使用；
-worker 完成后先从 ledger 重建 segment result，再做 pre-review quantity prediction；
- `_segment_complete()` 只读取 allocation/attempt 派生状态；
-带 blocking reasons 的 incomplete segment 不产生伪 complete projection；
-recipe 暴露 resume、ambiguous resolve 和 top-up 的唯一用户 CLI；
-根目录 README/runbook 记录 initial run、status、resume、circuit recovery、ambiguous retry/abandon、top-up、review、apply edits 和 final CSV；
-明确 worker 是内部执行器；
-明确 `run_openrouter_night_batch.py` 不使用；
-新增和修改的注释/docstring 使用英文。

#### 验证

-fresh recipe subprocess 不出现 `UnboundLocalError`；
-零 accepted records 的数量预测正常；
-带 blocking reasons 的 segment 不标记 complete；
-complete segment 重建 projection 不调用网络；
-CLI help、runbook 和实际参数一致；
-protected batch evaluation tests 通过。

#### Commit

```text
fix(route3): project recipe outputs from durable ledgers
```

#### 停止条件

-recipe 仍根据 summary/state 猜测 authoritative records；
-runbook 把 worker、旧 finalization 或夜间脚本写成正式用户入口；
-protected evaluation contract 改变。

### M8-S9：离线 fault injection 和真实 rehearsal

#### 离线验收

使用 fake page archives、DDG、OpenRouter 和 fake XLSX：

```text
3-page all5 initial target
→ targeted interruption
→ resume
→ definite rerun
→ ambiguous report and batch resolution
→ DDG/OpenRouter circuit trip and resume
→ 2-page top-up
→ review MD/XLSX
→ simulated delete/edit
→ revalidation
→ final CSV
```

必须断言：

-总计 5 个 unique primary allocations；
-预留未执行页仍是 attempt001；
-每个 allocation 最多 attempt002；
-generation response 不重复调用；
-已完成 DDG candidate-verifier result 不重复执行；
-circuit trip 后不启动新 calls，除已在途 calls；
-top-up 与旧 3 页零重叠；
-accepted/rejected/summary 删除后可从 ledger 重建；
-fake XLSX delete/edit 正确进入 final CSV；
-protected evaluation prompt hashes 不变；
-全量测试通过。

#### Commit

```text
test(route3): prove crash-safe rehearsal lifecycle
```

#### 真实 rehearsal 人工门

离线验收提交后运行唯一真实 rehearsal：

1. 新 run-group，20 个真实 primary pages，all5；
2. cache `all` 优先、fresh `fill` 补足；
3.部分页面完成后受控中断目标 worker；
4. resume 同一 segment 并完成原 20 页；
5.检查 cache、allocation、OpenRouter call records、DDG candidate-verifier results 和 attempt 类型；
6.新 top-up segment 拉取 10 个真实新页面；
7.确认 20 与 10 的 canonical page ID 交集为空，总计 30 个真实 unique primary pages；
8. generation 使用 Gemini 3 Flash，判断使用规定的 GPT-4.1-mini；
9.生成真实 review Markdown 和英文列 XLSX；
10.暂停，由用户真实审核问题质量；
11.接收用户返回的 XLSX；
12. apply edits、revalidation、finalization；
13.向用户展示最终 CSV。

约束：

-单次 generation 测试最多 20 个真实 pages；
- top-up 只生成 10 个真实新 pages；
-单纯拉取 pages 不超过 200；
-真实 review 前可使用 fake XLSX 做无人工测试；
-不运行独立夜间评测编排脚本；
-不运行大规模 batch prediction/judge；
-真实运行 artifacts 不因测试本身自动提交进 Git。

若真实 rehearsal 暴露代码缺陷：停止网络运行，添加最小复现测试，回到对应子里程碑修复并单独 commit；不得通过重复大规模调用试到成功。

### M8 总停止条件

-任何已删除 gate 仍影响 accept/reject 或 ranking；
- temporal/current 正式 guards 被误删；
- generation/DDG/second-stage 顺序或阈值发生未批准改变；
- protected evaluation prompt snapshot 变化；
- retry 出现 attempt003；
-state/rerun pool 再次成为页面事实来源；
-top-up 出现 page overlap 或修改旧 segment；
-circuit 自动切换模型/endpoint/proxy；
-未授权自动重试 ambiguous OpenRouter call；
-XLSX 含非英文 review columns。

---

# 更新后的非目标

- 不恢复或优化 Route 1/2；
-不恢复 KELM；
-不删除整个旧路线目录；
-不统一所有路线或所有 OpenRouter workflow 抽象；
-不引入 SQLite；
-不修改 SimpleQA Verified batch prediction/judge prompt；
-不把两个批量评测脚本合并进 generation/second-stage；
-不在本轮给两个批量评测脚本接入 Route 3 durable executor、circuit 或 ambiguous state；
-不改变 DDG 和 second-stage 正式阈值；
-除指定的 20-page initial run 和 10-page top-up rehearsal 外，不运行正式批量生成；
-不运行大规模独立 batch prediction/judge。