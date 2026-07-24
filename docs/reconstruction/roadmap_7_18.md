# Route 3 只读审查报告

## 审查结论

当前仓库还没有技术上唯一的 Route 3 入口，但已经可以确定一个最合理的正式入口候选：

- **正式入口候选**：[scripts/run_wikipedia_infobox_recipe.py](D:/Study/AI/My-research/Wikidata_Framework/scripts/run_wikipedia_infobox_recipe.py:333) 的 `main`
- **内部单段执行器**：[scripts/run_wikipedia_infobox_pipeline.py](D:/Study/AI/My-research/Wikidata_Framework/scripts/run_wikipedia_infobox_pipeline.py:743) 的 `main`

最近一次可见运行脚本 [run_route3_place50_fresh50_no_reuse_20260714_193621.sh](D:/Study/AI/My-research/Wikidata_Framework/tmp/run_route3_place50_fresh50_no_reuse_20260714_193621.sh) 使用 recipe 入口。产物 [walkthrough](D:/Study/AI/My-research/Wikidata_Framework/tmp/route3_place50_fresh50_no_reuse_gemini3flashpreview_2026_07_14_193621_artifacts/docs/walkthroughs/route3_place50_fresh50_no_reuse_gemini3flashpreview_2026_07_14_193621.md:11) 表明预处理、生成、rule-based gate、DuckDuckGo 和二阶段 grading 均在实际运行中到达。

证据标记：

- **[代码确认]**：从静态调用或明确分支条件直接确认。
- **[产物确认]**：由现有运行命令或产物确认。
- **[推断]**：证据较强，但缺少完整运行 provenance。
- **[未知]**：不能仅由现有代码或产物确认。

本次没有修改文件，没有运行生成、网络请求或测试。工作区原有的 `docs/human_notes/notes_for_later.txt` 修改和 `tmp/` 未跟踪文件仍然存在；它们在审查开始前已经存在。当前本地版本为：

- branch：`5-28`
- HEAD：`a23cd63cf1f4d5d4c91a2b07b8ccd5c156e97bd7`

近期 AWS 产物没有记录 Git SHA，因此不能证明该产物使用的就是这个 commit。

---

## 1. Route 3 的入口

### 正式入口候选

`run_wikipedia_infobox_recipe.py::main`

它负责：

- 按 answer type/segment 拆分任务；
- 生成每段命令；
- 调用底层 pipeline 子进程；
- 复用或跳过已完成 segment；
- 合并 accepted/rejected；
- 分配 Route 3 record ID；
- 写入汇总和 walkthrough。

这是最近运行证据使用的入口，最适合固定为今后的唯一正式入口。

### 其他仍可执行入口

`run_wikipedia_infobox_pipeline.py::main`

它既是 recipe 的子进程执行器，也可以被人工直接运行，支持：

- streaming page-ID 模式；
- URL-list 模式；
- validation-input 模式；
- endpoint resume；
- rerun pool；
- cached/fresh page 混合；
- single/all5 等不同生成模式。

因此它目前不只是内部模块，仍然是第二个实质入口。

历史 shell 脚本还会直接调用 pipeline。例如旧 all5 脚本只传 `--record-limit`，但当前 streaming 代码使用 `--stream-page-processing-target` 控制目标页数。旧脚本与当前代码的参数语义不再完全兼容。

**结论：**

- **[代码确认]** 当前存在多个可执行入口和多个运行分支。
- **[产物确认]** 最近一次可见运行使用 recipe。
- **[未知]** 论文正式数据此前是否全部由相同 commit、相同入口和相同参数生成。

---

## 2. Route 3 完整调用链

| 阶段 | 文件与 symbol | 调用者 → 被调用者 | Route 3 作用 | 副作用 | 可达性 |
|---|---|---|---|---|---|
| 总体编排 | `run_wikipedia_infobox_recipe.py::main` | CLI → `_segment_command`、`_segment_complete`、`_combine_segment_records` | 拆分 segment、启动 pipeline、合并结果 | 创建目录，写配置/输出，启动子进程 | **[产物确认]** |
| segment 命令 | `::_segment_command` | recipe `main` → pipeline CLI | 把 recipe 参数展开成完整 pipeline 参数 | 无直接写入；构造外部命令 | **[代码确认]** |
| pipeline 入口 | `run_wikipedia_infobox_pipeline.py::main` | recipe subprocess → `_run_streaming_page_id_pipeline` | 解析参数、构造 Settings/LLM/client | 创建 client；后续写输出 | **[代码确认]** recipe 固定走 streaming |
| 状态初始化 | `::_run_streaming_page_id_pipeline` | pipeline `main` → `PageIdStreamState`、reserve 函数、worker | 管理页 ID、并发 worker、resume/rerun | 状态文件、JSONL、summary、manifest | **[代码确认]** |
| 输入与样本选择 | `::_load_stream_excluded_page_ids`、`_reserve_stream_cached_page_archives`、`_reserve_stream_page_ids` | streaming runner → cache scan/search API | 选择 cached/fresh/rerun 页面 | 更新 used-ID/state；可能调用 MediaWiki | **[代码确认]** |
| 搜索采样 | `::_search_page_ids_with_retries`、`_stream_search_queries` | reserve → `WikipediaClient.search_page_ids` | 默认通过 `insource:"wikitable"` 等查询采样 | MediaWiki 请求与缓存 | 条件可达；recent run 使用 table-search |
| 单页处理 | `::_process_one_stream_page_id` | worker pool → generator + shared pipeline | 处理一个 page ID 并提交 decision | append accepted/rejected，更新 state | **[代码确认]** |
| 页面读取 | `WikipediaInfoboxTableGenerator.generate`、`_fetch_and_parse_page` | 单页 worker → generator | 加载页面 archive 或抓取 parse HTML | 网络、写 page archive | **[代码确认]** |
| 预处理 | `::_candidate_from_page` | `generate` → table parsing/ranking/filtering | 解析 infobox/wikitable、首段、表格评分和 source filters | 主要是内存处理；可读缓存 | **[代码确认]** |
| prompt 构造 | `build_route3_infobox_prompt`、`build_route3_wikitable_prompt` → `build_wikipedia_infobox_prompt` | `_candidate_from_page` → prompt builder | 构造 single/all5、answer type、reasoning type prompt | 无 | **[代码确认]** |
| 模型调用 | `::_complete_text_with_audit` → `OpenRouterCheapModelQAClient.complete_text_with_audit` | generator → OpenRouter client | 调用生成模型并保存请求/响应审计 | 网络调用；重试和 proxy/direct fallback | **[产物确认]** |
| 原始响应保存 | `complete_text_with_audit`、`::_source_metadata` | model client → generator metadata | 保存 request payload、raw text、response body、finish reason | 最终随 record 写 JSONL | **[产物确认]**，但 rerun 异常路径不完整 |
| 解析 | `parse_json_object` | generator → JSON parser | 从模型文本提取 JSON object | 无 | **[代码确认]** |
| 标准化 | `_normalize_generated_answer`、`_normalize_answer_type`、`GeneratedCandidate.__post_init__` | response parser → candidate | 标准化答案、Date/Number、answer type、reasoning type | 无 | **[代码确认]** |
| all5 展开 | `_candidates_from_all5_response`、`_candidate_from_single_model_response` | generator → slot candidates | 把一次 all5 响应拆成多个候选 | 无 | all5 参数下可达 |
| shared processing | `generation_pipeline.process_generated_candidates` | 单页 worker → validators/filter/grading/dedup | 执行共享 verification/filtering | DDG/LLM 请求，生成 rejection audit | **[代码确认]** |
| surface/规则检查 | rewrite guards、`validate_question_surface`、`evaluate_candidate_answer_type_gate` | shared pipeline → rule modules | 时间、歧义、自包含、类型和问题表面检查 | 可选 rewrite 时会调用模型 | **[代码确认]** |
| verification | `validate_generated_candidate` → `_validate_wikipedia_infobox_candidate` | shared pipeline → generator validators | 检查答案位于选中表格、URL、稳定性标记等 | 无 | **[代码确认]** |
| 长尾 filtering | `run_search_based_longtail_verifier` | shared pipeline → DDG client | 对完整问题和关键词查询做 answer leakage 检查 | DuckDuckGo 请求与审计记录 | **[产物确认]** |
| 二阶段 grading | `evaluate_model_panel` | shared pipeline → grader clients | 多模型答题与难度/正确性过滤 | 多次模型请求，保存 grader audit | 参数开启时可达；recent run 已开启 |
| 去重 | `process_generated_candidates` 内部 seen sets | shared pipeline → exact/subject checks | exact question 和 subject 级去重 | 无 | **[代码确认]**，但仅单次调用范围 |
| 单段输出 | `append_jsonl`、state `mark_*`/`save` | 单页 worker → IO/state | 增量写 accepted/rejected 和状态 | 非事务式文件写入 | **[代码确认]** |
| recipe 合并 | `_combine_segment_records` → `assign_unique_route3_record_ids` | recipe → route3 IDs | 合并 segment 并分配最终 ID | 覆盖或 append combined JSONL | **[代码确认]** |
| 最终报告 | recipe/pipeline summary、walkthrough、manifest | runner → IO | 汇总配置、失败阶段、吞吐 | 写 Markdown/JSON | **[产物确认]** |

### 关键顺序

实际主链可简化为：

```text
recipe main
  → pipeline subprocess
    → streaming state / page selection
      → process one page
        → fetch/cache/parse Wikipedia page
        → rank and filter tables
        → build prompt
        → generation model
        → parse and normalize response
        → shared validation
        → rule-based answer-type gate
        → DDG long-tail filter
        → optional second-stage grading
        → local dedup
        → append accepted/rejected
        → update stream state
  → combine segments
  → assign Route 3 IDs
  → final JSONL + summary + walkthrough
```

---

## 3. Route 3 核心依赖文件

### 直接决定生成行为

- [scripts/run_wikipedia_infobox_recipe.py](D:/Study/AI/My-research/Wikidata_Framework/scripts/run_wikipedia_infobox_recipe.py)
- [scripts/run_wikipedia_infobox_pipeline.py](D:/Study/AI/My-research/Wikidata_Framework/scripts/run_wikipedia_infobox_pipeline.py)
- [src/wikidata_simpleqa/wikipedia_infobox_generator.py](D:/Study/AI/My-research/Wikidata_Framework/src/wikidata_simpleqa/wikipedia_infobox_generator.py)
- [src/wikidata_simpleqa/wikipedia_streaming.py](D:/Study/AI/My-research/Wikidata_Framework/src/wikidata_simpleqa/wikipedia_streaming.py)
- [src/wikidata_simpleqa/generation_pipeline.py](D:/Study/AI/My-research/Wikidata_Framework/src/wikidata_simpleqa/generation_pipeline.py)
- [src/wikidata_simpleqa/generator_validators.py](D:/Study/AI/My-research/Wikidata_Framework/src/wikidata_simpleqa/generator_validators.py)
- [src/wikidata_simpleqa/rule_based_answer_type_gate.py](D:/Study/AI/My-research/Wikidata_Framework/src/wikidata_simpleqa/rule_based_answer_type_gate.py)
- [src/wikidata_simpleqa/grading.py](D:/Study/AI/My-research/Wikidata_Framework/src/wikidata_simpleqa/grading.py)
- [src/wikidata_simpleqa/generation_models.py](D:/Study/AI/My-research/Wikidata_Framework/src/wikidata_simpleqa/generation_models.py)
- [src/wikidata_simpleqa/route3_quality_rules.py](D:/Study/AI/My-research/Wikidata_Framework/src/wikidata_simpleqa/route3_quality_rules.py)
- [src/wikidata_simpleqa/page_id_lists.py](D:/Study/AI/My-research/Wikidata_Framework/src/wikidata_simpleqa/page_id_lists.py)
- [src/wikidata_simpleqa/route3_ids.py](D:/Study/AI/My-research/Wikidata_Framework/src/wikidata_simpleqa/route3_ids.py)

### 基础支撑依赖

- `config.py`
- `cheap_model_qa.py`
- `llm_rewrite.py`
- `search_client.py`
- `search_cli.py`
- `wikipedia_client.py`
- `network.py`
- `io.py`
- `text_normalization.py`
- `entity_normalization.py`
- `date_reference.py`
- `number_reference.py`
- `validators.py`
- `geographic_leakage.py`
- `constants.py`
- `models.py`
- `reasoning.py`

---

## 4. A/B/C/D 分类

分类基于“当前 recipe → streaming pipeline”调用链，而不是目录名。

### A. Route 3 核心代码

直接决定当前生成结果：

- `scripts/run_wikipedia_infobox_recipe.py`
- `scripts/run_wikipedia_infobox_pipeline.py`
- `wikipedia_infobox_generator.py`
- `wikipedia_streaming.py`
- `generation_pipeline.py`
- `generator_validators.py`
- `rule_based_answer_type_gate.py`
- `grading.py`
- `generation_models.py`
- `route3_quality_rules.py`
- `page_id_lists.py`
- `route3_ids.py`

其中 grading、rewrite、pageview 等带参数开关，但 recent run 已实际启用 second-stage grading。

### B. Route 3 支撑代码

第一组是正常支撑：

- 配置、网络、OpenRouter、DDG、Wikipedia client；
- JSONL IO；
- 文本、日期、数字和实体标准化；
- schema/model；
- 通用 surface validators；
- rewrite client 和 prompt 常量。

第二组是**启动期意外依赖的历史代码**。`generation_pipeline.py` 顶层导入了旧架构，导致 Route 3 启动时仍需要这些模块能成功 import：

- `domain_templates.py`
- `generators.py`
- `route1_multihop.py`
- `route4_two_hop.py`
- `route1_hidden_entity.py`
- `route1_validators.py`
- `ambiguity.py`
- `candidate_harvester.py`
- `composed_harvester.py`
- `canonical_questions.py`
- `route4_template_catalog.py`
- `route4_two_hop_template_catalog.py`
- `single_hop_template_catalog.py`
- `sparql_queries.py`
- `subject_resources.py`
- `wikidata_client.py`
- `date_answers.py`

**[代码确认]** 这些模块中的 Route 1/Route 4 生成函数没有进入 Route 3 主算法，但模块目前属于 import-time 依赖，不能删除。

### C. 已确认与当前 Route 3 调用链无关的历史入口

以下脚本不在 recipe 的导入或子进程调用链内：

- `scripts/generate_pilot.py`
- `scripts/generate_selected_templates.py`
- `scripts/generate_stage5_pilot.py`
- `scripts/generate_stage5b_pilot.py`
- `scripts/run_stage5b_workflow.py`
- `scripts/run_kelm_half_pipeline.py`
- `scripts/run_route1_hidden_entity_two_hop_pipeline.py`
- `scripts/run_route1_multihop_pipeline.py`
- `scripts/run_route4_two_hop_pipeline.py`
- Route 4 catalog/export/salvage 脚本
- `scripts/tmp_filter_route3_passed_all.py`
- `scripts/tmp_apply_route3_answer_type_redirects.py`
- `scripts/tmp_build_route3_repair_filter_outputs.py`
- `scripts/tmp_pageview_longtail_analysis.py`
- 独立 OpenRouter evaluation/prediction batch 脚本

包内的 `pipeline.py`、`workflow.py`、`kelm_generator.py`、`concurrency.py` 也不在当前 recipe 的本地 import closure 内。

这里的“无关”只表示当前 Route 3 正式候选调用链不会执行，不表示可以立即删除。

### D. 暂时无法确认

- `scripts/finalize_wikipedia_stream_batch.py`
- `scripts/run_rule_based_qa_gate.py`
- `scripts/run_final_llm_qa_filter.py`
- `scripts/manage_route3_page_id_list.py`
- `scripts/generate_wikipedia_table_urls.py`
- `scripts/extract_wikipedia_raw_pages.py`
- `scripts/build_wikipedia_accepted_qa_review.py`
- `tmp/` 中各种 Route 3 rerun、repair、package shell 脚本
- pipeline 的 URL-list、validation-input、direct rerun 和 endpoint-resume 分支
- 运行时选择的 `ddgs` backend/fallback
- 由环境变量、缓存存在性、used-ID 文件和 rerun pool 触发的行为

这些代码没有被当前 recipe 自动调用，但文档或历史运维过程可能把它们当作正式生成后的收尾步骤。

验证方法：

1. 明确论文数据唯一 runbook；
2. 固定从入口到 final release 的完整命令序列；
3. 给每个现有数据文件补充或核对 lineage；
4. 对一次小规模 rehearsal 记录进程命令和 import trace；
5. 明确 finalization、rule gate、LLM judge 和 rebalancing 是否属于论文方法。

---

## 5. Route 3 对历史目录代码的依赖

存在两种依赖。

第一种是实际共享依赖，例如：

- 通用模型客户端；
- 通用 validation；
- 通用 rewrite；
- schema、normalization、IO。

这些应保留为 B 类。

第二种是 `generation_pipeline.py` 顶层导入造成的启动期依赖。虽然 Route 3 不执行 Route 1/Route 4 的生成逻辑，但删除相应模块会使 Route 3 在 import 阶段失败。

静态 import closure 包含约 46 个本地模块；未发现 closure 内使用 `importlib` 或 `__import__` 进行本地动态导入的证据。

所以当前不能把“没有执行旧 route 函数”等同于“旧模块可以删除”。

---

## 6. 可能调用错误版本的风险

### 高风险

1. **segment 复用不校验版本**

`_segment_complete` 主要检查 accepted/rejected/summary 是否存在以及数量是否满足目标，不校验：

- Git SHA；
- prompt hash；
- model/temperature/max tokens；
- filter thresholds；
- cache policy；
- dependency versions；
- 完整参数 fingerprint。

相同 run ID 下可能静默复用由不同配置生成的 segment。

2. **resume 与 reset/append 组合不安全**

recipe 启动子进程时传递 `--reset-stream-state`。如果同一 run ID 的不完整任务重新执行：

- state 会重置；
- 已有 accepted/rejected JSONL 仍可能继续 append；
- 页面可能重复处理；
- API/LLM 可能重复调用；
- summary 可能覆盖为混合运行结果。

3. **写输出与写 state 不具备事务性**

单页提交顺序是 append JSONL 后更新 state。两者之间崩溃会造成：

- record 已写但 state 未记账；
- resume 后重复请求和重复输出。

`PageIdStreamState.save` 和 page archive 写入也不是原子替换。

4. **全局去重缺失**

`process_generated_candidates` 的 seen sets 在每次调用时新建，而 streaming 每页调用一次。因此当前去重范围主要是：

- 同一页；
- 同一次候选处理。

它不覆盖：

- 不同页面；
- 不同 segment；
- 已存在 endpoint；
- recipe 合并后的全部 records。

`_combine_segment_records` 只合并和分配 ID，没有全局去重。

### 中风险

5. **多个同类实现**

包内集成的 `rule_based_answer_type_gate.py` 与独立脚本 `run_rule_based_qa_gate.py` 不是完全相同的实现。当前主链使用包内版本，独立脚本是否还应作为正式收尾未知。

6. **all5 与 answer-type 约束可以形成模糊组合**

specific answer type 与 `--route3-answer-type-mode all5` 可以同时出现；all5 prompt 会生成五种 slot，而不只是指定类型。

7. **兼容参数可覆盖当前参数**

`--small-model` 等兼容 alias 仍可能改变 generation model，容易造成命令表面与实际 resolved config 不一致。

8. **缓存影响结果但 provenance 不完整**

页面 archive、搜索缓存、rule-gate lexicon、used page-ID 列表都会影响选择或判断。当前没有统一记录这些输入的内容 hash。

9. **rerun 失败不完整保存原始审计**

正常进入 accepted/rejected serialization 的候选会保存完整 LLM audit。但被标记为 retryable rerun 的页面不一定写入完整 rejected record，模型请求和原始响应可能只剩 state 中的简化原因。

### 版本一致性结论

- **[代码确认]** 没有发现显式命名的 Route 3a/Route 3b。
- **[代码确认]** 实际存在 recipe/direct pipeline、single/all5、infobox/wikitable、cached/fresh、URL/streaming 等多个变体。
- **[产物确认]** 2026-07-14 的可见运行使用 Gemini 3 Flash Preview、4096 tokens、single、Place、infobox+wikitable、second-stage grading。
- **[代码确认]** 代码默认 generation model 是 GPT-4.1 mini、1200 tokens、second-stage off；与该运行不同。
- **[代码确认]** `docs/design.md` 的示例又包含 Gemini 3.5 Flash、all5、infobox-only，和最近运行不同。
- **[推断]** 目前版本选择主要依赖 shell 参数和手工 run script，而不是一个不可变的正式配置。
- **[未知]** 哪组参数代表论文最终方法。

文档也存在不一致：设计文档一处把 answer-type gate 放在 DDG 前，与代码一致；另一处又把它描述成 long-tail 后的独立阶段。根目录没有提供一个能够覆盖当前事实的统一正式 README/runbook。

---

## 7. 正式生成前必须处理的问题

在不改变 prompt、算法和过滤标准的前提下，至少要完成：

1. 指定 recipe 为唯一正式入口，pipeline 定义为内部 worker。
2. 固定一份完整 resolved config，而不只是保存命令行显式参数。
3. 记录 Git SHA、dirty 状态、prompt hash、模型参数、filter thresholds 和依赖版本。
4. 给 segment 增加配置 fingerprint；fingerprint 不同禁止复用。
5. 区分 new run 与 resume；默认禁止在已有 run directory 上继续写。
6. 解决 state/output 非事务导致的重复调用和重复记录。
7. 为 rerun/exception 路径保留完整原始模型 request/response audit。
8. 添加跨页、跨 segment、最终合并后的全局去重。
9. 明确 finalization、独立 rule gate、final LLM judge、rebalancing 是否属于正式方法。
10. 固定或记录页面 cache、搜索 cache、lexicon 和 used-ID 输入。
11. 建立离线 golden baseline 和小规模端到端测试。
12. 正式 batch 必须使用唯一 run ID，并默认拒绝覆盖已有输出。

---

## 8. 可留到正式生成后的清理

- 删除 Route 1、Route 2、Route 4 或历史实验代码；
- 移动历史文件和重新设计目录结构；
- 抽象统一所有 route；
- 合并仓库内所有重复实现；
- 清理 `tmp/` 历史脚本和归档；
- 重命名遗留 CLI flags；
- 合并多个 OpenRouter client/JSON parser；
- 重构 `generation_pipeline.py` 的宽泛顶层 import；
- 重写历史文档；
- 做大规模性能优化。

不过，历史模块的 import-time 依赖应在正式生成前记录清楚；实际拆除可以之后再做。
