已修订。没有发现新的、需要暂停讨论的高危边界；但有一个重要实施顺序约束：

`question_targets_mutable_fact` 目前仍被 `route1_validators.py` 导入，而 Route 3 启动又可能通过旧的顶层 import 加载 Route 1 模块。因此删除该函数时，必须同步移除旧模块中的 import/use，确保 Route 3 启动不因历史依赖中断。除此之外不修复 Route 1。

本轮只更新计划，没有修改文件。

# 修订后的最小稳定化 milestones

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

## M3：实现最小可靠运行与 resume

### 五个核心改动

1. `segment_manifest.json`
2. segment fingerprint
3. 原子 page-attempt ledger
4. state 从 ledger 恢复
5. accepted/rejected/summary 从 ledger 重建

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
- table ranking/filter配置；
- DDG；
- second-stage。

正式运行要求 clean worktree。

### 复用规则

```text
same fingerprint + complete
→ reuse

same fingerprint + incomplete
→ resume

different fingerprint
→ new 或 top-up
```

### Page-attempt ledger

每页一个原子文件：

```text
p<canonical_page_id>_attempt001.json
```

保存：

- generation raw audit；
-全部 single/all5 candidates；
- DDG；
- second-stage；
- accepted/rejected/rerun；
- candidate IDs；
- timings。

使用临时文件加 `os.replace`。

### State 和派生输出

- state 只是运行时缓存；
- resume 先扫描 ledger；
- committed page 不重复 generation；
- JSONL/summary 从 ledger 重建；
- page archive 使用临时文件加 `os.replace`；
- archive hash 写入 provenance。

### 运行模式

- new：新目录；
- resume：同 segment/fingerprint；
- top-up：同 run-group、新 segment。

### 验证

- commit 前中断可重试；
- commit 后、state 前中断不重复调用；
- JSONL 中断后可重建；
- fingerprint 改变拒绝复用；
- top-up 不修改旧 segment；
- all5 的 slots 在同一个 page-attempt 中提交。

### 停止条件

- committed page 被重复 generation；
- state 比 ledger 权威；
-不同 fingerprint 被复用；
- top-up 覆盖旧 segment。

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

与原计划一致：

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
- Markdown two-model answers。

### XLSX 规范英文列名

列严格改为：

```text
id
question
reference_answer
wikipedia_url
topic
delete
edited_question
edited_reference_answer
edit_reason
```

不再使用中文列名。

规则：

- `delete` 默认 `No`；
-可选 `Yes/No`；
- `topic` 使用十项下拉列表；
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
-生成新 MD/XLSX；
-直到没有 Q/A 编辑。

### 验证

-列名和顺序精确匹配；
- delete 默认 No；
- round-trip 不改变 ID；
- answer 编辑清空 aliases；
-旧 DDG/grading 不复用；
- revision history 完整；
-只有最新 accepted 出现在下一轮 MD/XLSX。

### 停止条件

-仍生成中文列；
-列名被自动本地化；
-修改后未重跑完整 post-generation pipeline；
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

与原计划一致：

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

## M8：端到端 baseline 和小规模 rehearsal

### 离线流程

```text
recipe
→ worker
→ page ledger
→ accepted/rejected
→ projection
→ English-column MD/XLSX review artifacts
→ apply edits
→ revalidation
→ finalization
→ CSV
```

覆盖：

- single/all5；
- infobox/wikitable；
- Person gate 删除后的 candidate；
-不含 preferred table ranking bonus；
- new/resume/top-up；
-人工删除和修改；
-最终 page dedup/rebalance。

### 小规模网络 rehearsal

不超过 10 个 primary pages：

-唯一 new run；
-cache all/fill；
-中断并 resume；
-top-up；
-生成 MD/英文列 XLSX；
-模拟一条删除和一条编辑；
-生成 final CSV。

批量评测脚本只做 mocked 或极小独立验证，不修改其 prompt。

### 停止条件

除原计划条件外增加：

-任何已删除 gate 仍影响 accept/reject 或 ranking；
-删除 `question_targets_mutable_fact` 后 Route 3 import 失败；
- temporal/current 正式 guards 被误删；
-评测 prompt snapshot 变化；
-XLSX 仍含中文列。

---

# 更新后的非目标

- 不恢复或优化 Route 1/2；
-不恢复 KELM；
-不删除整个旧路线目录；
-不统一所有路线抽象；
-不引入 SQLite；
-不修改 SimpleQA Verified batch prediction/judge prompt；
-不把两个批量评测脚本合并进 generation/second-stage；
-不改变 DDG 和 second-stage 正式阈值；
-不运行正式批量生成。