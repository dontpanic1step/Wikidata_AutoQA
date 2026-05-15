# Product Manufacturer Walkthrough, Branch 5-13-restored

Generated from the latest rerun artifacts:

- `outputs/product_manufacturer_walk_accepted.jsonl`
- `outputs/product_manufacturer_walk_rejected.jsonl`
- `outputs/product_manufacturer_walk_summary.json`

## Run Configuration

- `target_time`: `"2024-11-07"`
- `date_upper_bound`: `"2024-11-07"`
- `pilot_total`: `1`
- `harvest_limit_per_template`: `20`
- `timeout_seconds`: `20.0`
- `route1_subject_seed_window_granularity`: `"day"`
- `enabled_routes`: `["route1_wikidata_light"]`
- `duckduckgo_top_k`: `10`
- `search_longtail_thresholds`: `{"full_question": 1.0, "keyword_queries": 1.0, "overall": 1.0}`
- `rewrite_enabled`: `true`
- `second_stage_grading_enabled`: `true`
- `second_stage_grading_accuracy_threshold`: `1.0`
- `second_stage_grading_models`: `["openai/gpt-4.1-mini", "google/gemini-3-flash-preview"]`
- `second_stage_grader_model`: `"openai/gpt-4.1-mini"`

## Outcome

- Accepted: `1`
- Rejected: `0`
- Generated candidates: `2`
- The previous empty-subject-label / `wbsearchentities response missing search key` failure did not recur.
- Wikidata client errors recorded in this run: `0`

## Accepted QA

- Canonical question: `"Which company manufactured the product PlayStation 5 Pro?"`
- Rewritten question: `"Who is the manufacturer of the PlayStation 5 Pro?"`
- Gold answer: `"Sony Interactive Entertainment"`
- Answer aliases: `["Sony Computer Entertainment, Inc.", "SCE", "Sony Computer Entertainment", "SIE", "Sony Interactive Entertainment Inc.", "Sony Interactive", "PlayStation C.A.M.P.", "SCEI", "SIE LLC.", "Sony Interactive Entertainment LLC", "SONY INTERACTIVE ENTERTAINMENT AMERICA LLC"]`
- Subject entity: `{"name": "PlayStation 5 Pro", "qid": "Q124983919", "wikipedia_title": "PlayStation 5 Pro", "url": "https://en.wikipedia.org/wiki/PlayStation_5_Pro"}`
- Answer entity: `{"name": "Sony Interactive Entertainment", "qid": "Q18594", "wikipedia_title": "", "url": ""}`
- Evidence: `{"text": "PlayStation 5 Pro manufacturer Sony Interactive Entertainment", "url": "https://en.wikipedia.org/wiki/PlayStation_5_Pro", "source_title": "PlayStation 5 Pro", "section": "wikidata_statement", "retrieved_at": "2026-05-15"}`
- Template key: `"product_manufacturer"`
- Domain: `"Economy and Business"`
- Question family: `"which_company_manufactured_product"`
- Answer type: `"Organization"`
- Target time: `"2024-11-07"`

## Pipeline Trace

1. Heavy direct WDQS path was attempted first and timed out.
2. Day-window subject-seed WDQS fallback was attempted for `2024-11-07` and timed out.
3. API-light fallback used `wbsearchentities` plus `wbgetentities` seed lookup.
4. The Route 1 validator accepted the `PlayStation 5 Pro` candidate and avoided blank-label ambiguity search failure.
5. LLM rewrite produced the natural question and five search queries.
6. DuckDuckGo stage-1 filtering passed because thresholds were set to `1.0`.
7. Cheap-model rejection is disabled for SimpleQA Verified alignment; the model panel ran as grading/evaluation rather than rejection-by-answer.
8. Both small QA models answered correctly and the grader judged both answers `CORRECT`.

## Timings And Bottlenecks

- Summary timings: `{"candidate_generation_seconds": 44.6957, "candidate_processing_seconds": 17.7009, "output_write_seconds": 0.004, "total_seconds": 62.4025}`
- Candidate processing timings: `{"rewrite_seconds": 4.01, "number_reference_margin_seconds": 0.0, "duckduckgo_search_seconds": 0.1799, "second_stage_grading_seconds": 13.5084, "total_processing_seconds": 17.7007}`
- Summary bottlenecks: `[{"phase": "candidate_generation_seconds", "seconds": 44.6957}, {"phase": "candidate_processing_seconds", "seconds": 17.7009}, {"phase": "output_write_seconds", "seconds": 0.004}]`
- Candidate bottlenecks: `[{"phase": "second_stage_grading_seconds", "seconds": 13.5084}, {"phase": "rewrite_seconds", "seconds": 4.01}, {"phase": "duckduckgo_search_seconds", "seconds": 0.1799}]`

The main bottleneck was still Wikidata candidate generation. The two WDQS paths consumed most of the run time before the API-light fallback succeeded. The second-largest candidate-level bottleneck was second-stage model grading.

## Wikidata Problems Recorded

- `direct_candidate_query_used`: Using the heavy direct WDQS candidate query as the default single-fact Route 1 harvest path. Context: `{"domain": "product_manufacturer", "subject_type_qid": "Q2424752", "date_property_pid": "P577", "target_property_pid": "P176"}`
- `direct_candidate_query_failed`: The direct WDQS candidate query failed before validation could start. Context: `{"domain": "product_manufacturer", "error_type": "TimeoutError", "error_message": "The read operation timed out"}`
- `subject_seed_fallback_used`: The direct WDQS candidate query returned no candidates; trying the light subject-seed fallback with local claim extraction. Context: `{"domain": "product_manufacturer", "subject_type_qid": "Q2424752", "date_property_pid": "P577", "target_property_pid": "P176"}`
- `windowed_subject_seed_query_failed`: One subject-seed WDQS window failed; continuing with later windows. Context: `{"domain": "product_manufacturer", "window_start": "2024-11-07", "window_end": "2024-11-07", "error_type": "TimeoutError", "error_message": "The read operation timed out"}`
- `subject_seed_query_failed`: All subject-seed WDQS windows failed or returned no rows before local claim extraction could start. Context: `{"domain": "product_manufacturer", "query_count": 1}`
- `subject_seed_path_returned_no_candidates`: The light subject-seed fallback returned no candidates. Context: `{"domain": "product_manufacturer"}`
- `api_light_seed_fallback_used`: Using wbsearchentities + wbgetentities seed fallback after WDQS paths failed. Context: `{"domain": "product_manufacturer", "seed_count": 5}`

## Rewrite Output

- Rewritten question: `Who is the manufacturer of the PlayStation 5 Pro?`
- Search queries:
- `manufacturer of PlayStation 5 Pro`
- `PlayStation 5 Pro production company`
- `company behind PlayStation 5 Pro`
- `who makes PlayStation 5 Pro`
- `PlayStation 5 Pro maker`

## DuckDuckGo Stage 1 Summary

- Passed: `True`
- Triggered rule: ``
- Duration seconds: `0.1799`
- Category hit rates: `{"full_question": {"query_count": 1, "total_results": 10, "answer_hit_results": 5, "title_hit_results": 3, "snippet_hit_results": 5, "answer_hit_rate": 0.5}, "keyword_queries": {"query_count": 5, "total_results": 49, "answer_hit_results": 11, "title_hit_results": 7, "snippet_hit_results": 10, "answer_hit_rate": 0.22448979591836735}, "answer_probe": {"query_count": 0, "total_results": 0, "answer_hit_results": 0, "title_hit_results": 0, "snippet_hit_results": 0, "answer_hit_rate": 0.0}, "overall": {"query_count": 6, "total_results": 59, "answer_hit_results": 16, "title_hit_results": 10, "snippet_hit_results": 15, "answer_hit_rate": 0.2711864406779661}}`

`answer_hit` is the stored string-inclusion result. It is `true` when the normalized title or snippet matched the gold answer or one of its accepted aliases. Number-margin hit lists were empty because this template answer type is `Organization`, not `Number`.

## DuckDuckGo Evidence Appendix

### full_question: `Who is the manufacturer of the PlayStation 5 Pro?`

- Result count: `10`
- Title hits: `3`
- Snippet hits: `5`
- Answer-hit results: `5`
- Exact question hit: `False`

1. Title: Sony Interactive Entertainment Launches PlayStation 5 Pro
   URL: `//duckduckgo.com/l/?uddg=https%3A%2F%2Fsonyinteractive.com%2Fen%2Fpress%2Dreleases%2F2024%2Fsony%2Dinteractive%2Dentertainment%2Dlaunches%2Dplaystation%2D5%2Dpro%2F&rut=be5d4e754638be8da9af0d98d4cf8f3b4a1bfcdc664080e18bd5a42351df9e0a`
   Snippet: Today, Sony Interactive Entertainment expands the PlayStation®5 (PS5®) family of products with the release of the new PlayStation®5 Pro (PS5®Pro) console - the company's most advanced and innovative gaming console to date.
   String inclusion answer_hit: `True`
   Title number-margin hits: `[]`
   Snippet number-margin hits: `[]`

2. Title: PlayStation 5 Pro | PlayStation Wiki | Fandom
   URL: `//duckduckgo.com/l/?uddg=https%3A%2F%2Fplaystation.fandom.com%2Fwiki%2FPlayStation_5_Pro&rut=617c849b3058e03bd99f24af57adf18696c97bf875865bafb04973326f31911f`
   Snippet: Not to be confused with PlayStation 5 or PlayStation 5 Slim. The PlayStation 5 Pro, otherwise known as PS5 Pro, is a game console developed by Sony Interactive Entertainment. It released on November 7th 2024. The PlayStation 5 Pro was formally announced by Sony on September 10, 2024, following industry rumors since March 2024. Among other changes, the new console has three primary improvements ...
   String inclusion answer_hit: `True`
   Title number-margin hits: `[]`
   Snippet number-margin hits: `[]`

3. Title: Sony has released a brand new PS5 Pro - TechRadar
   URL: `//duckduckgo.com/l/?uddg=https%3A%2F%2Fwww.techradar.com%2Fgaming%2Fsony%2Dhas%2Dreleased%2Da%2Dbrand%2Dnew%2Dps5%2Dpro%2Dheres%2Deverything%2Dyou%2Dneed%2Dto%2Dknow%2Dabout%2Dthe%2Dnew%2Dmodel&rut=0ee6570889f62de63ce5e9480670a76dfd12dfaf254158fd0dadd87015763287`
   Snippet: Sony has released a brand new PlayStation 5 Pro model, featuring several improvements to the original console, but don't expect them to be anything significant.
   String inclusion answer_hit: `False`
   Title number-margin hits: `[]`
   Snippet number-margin hits: `[]`

4. Title: Sony Interactive Entertainment Launches the PlayStation 5 Pro
   URL: `//duckduckgo.com/l/?uddg=https%3A%2F%2Fwww.techpowerup.com%2F328544%2Fsony%2Dinteractive%2Dentertainment%2Dlaunches%2Dthe%2Dplaystation%2D5%2Dpro&rut=b0168862f41cf54f31700a235bd13d3cc15bc4066bbc19885c93b21e85777c55`
   Snippet: Today, Sony Interactive Entertainment expands the PlayStation 5 (PS5) family of products with the release of the new PlayStation 5 Pro (PS5 Pro) console - the company's most advanced and innovative gaming console to date. PlayStation 5 Pro was designed with deeply engaged players and game creators in mind and includes key performance features that allow games to run with higher fidelity ...
   String inclusion answer_hit: `True`
   Title number-margin hits: `[]`
   Snippet number-margin hits: `[]`

5. Title: PS5 Pro - The Ultimate Guide to Specs, Price, and Release Date
   URL: `//duckduckgo.com/l/?uddg=https%3A%2F%2Fwccftech.com%2Froundup%2Fps5%2Dpro%2Deverything%2Dyou%2Dneed%2Dto%2Dknow%2Dabout%2Dsonys%2Dnew%2Dconsole%2F&rut=881ae80d0feb59cf3c08e413d9d02ad91d126a53e210e23bbc8708dfd052c397`
   Snippet: Here's everything you need to know about PS5 Pro, the new Sony console due to be released worldwide on November 7, 2024.
   String inclusion answer_hit: `False`
   Title number-margin hits: `[]`
   Snippet number-margin hits: `[]`

6. Title: Sony Interactive Entertainment Launches PlayStation 5 Pro
   URL: `//duckduckgo.com/l/?uddg=https%3A%2F%2Fwww.businesswire.com%2Fnews%2Fhome%2F20241107646698%2Fen%2FSony%2DInteractive%2DEntertainment%2DLaunches%2DPlayStation%2D5%2DPro%2F&rut=fa2a0a7b762548618edeaf7c116d07c5f9a1101ab8d73ec092ecafed4aeeaf03`
   Snippet: Today, Sony Interactive Entertainment expands the PlayStation®5 (PS5®) family of products with the release of the new PlayStation®5 Pro (PS5®Pro) cons
   String inclusion answer_hit: `True`
   Title number-margin hits: `[]`
   Snippet number-margin hits: `[]`

7. Title: PlayStation®5 Pro | Witness Play Unleashed (US)
   URL: `//duckduckgo.com/l/?uddg=https%3A%2F%2Fwww.playstation.com%2Fen%2Dus%2Fps5%2Fps5%2Dpro%2F&rut=8d7f33f13396da53c5729baf5af4b18977423ba75de665d1268184e1d7ef00de`
   Snippet: Witness Play Unleashed ™ With the PlayStation®5 Pro console, the world's greatest game creators can enhance their games with incredible features like advanced ray tracing, super sharp image clarity for your 4K TV, and high frame rate gameplay.*
   String inclusion answer_hit: `False`
   Title number-margin hits: `[]`
   Snippet number-margin hits: `[]`

8. Title: Sony announces PlayStation 5 Pro: Updates and release date revealed
   URL: `//duckduckgo.com/l/?uddg=https%3A%2F%2Fwww.thenationalnews.com%2Farts%2Dculture%2F2024%2F09%2F11%2Fplaystation%2D5%2Dpro%2Ddetails%2Drelease%2Ddate%2F&rut=b34a49e1fb6fe276a33d46538d84b1e941dca84f10affc1619e7549feb3f6294`
   Snippet: Sony has unveiled its long-awaited PlayStation 5 Pro, an enhanced version of the PlayStation 5. In a nine-minute technical presentation video released on Tuesday, the Japanese company announced that the new console will contain three major upgrades on the PS5, which was launched back in 2020. The ...
   String inclusion answer_hit: `False`
   Title number-margin hits: `[]`
   Snippet number-margin hits: `[]`

9. Title: PlayStation 5 - Wikipedia
   URL: `//duckduckgo.com/l/?uddg=https%3A%2F%2Fen.wikipedia.org%2Fwiki%2FPlayStation_5&rut=9ae1b77eff06902815bf9effd013ed216d1f6ee352e6a2713e51df56a2b7953c`
   Snippet: The PlayStation 5 (PS5) is the home video game console developed by Sony Interactive Entertainment for the fifth iteration of their PlayStation brand. It was announced as the successor to the PlayStation 4 in April 2019, was launched on November 12, 2020, in Australia, Japan, New Zealand, North America, and South Korea, and was released worldwide a week later. The PS5 is part of the ninth ...
   String inclusion answer_hit: `True`
   Title number-margin hits: `[]`
   Snippet number-margin hits: `[]`

10. Title: Where Does Sony Build Its PlayStation 5 Consoles? - SlashGear
   URL: `//duckduckgo.com/l/?uddg=https%3A%2F%2Fwww.slashgear.com%2F1914020%2Fwhere%2Ddoes%2Dsony%2Dbuild%2Dplaystation%2D5%2Dconsoles%2F&rut=65cd55c41368189efcc135097da532c5720f2558875c81663bc02414b57ad48f`
   Snippet: Sony say that PlayStation 5 consoles are made in Japan. However, some consoles are made in China and even the ones made in Japan have Chinese components.
   String inclusion answer_hit: `False`
   Title number-margin hits: `[]`
   Snippet number-margin hits: `[]`

### keyword_query_1: `manufacturer of PlayStation 5 Pro`

- Result count: `10`
- Title hits: `2`
- Snippet hits: `2`
- Answer-hit results: `3`
- Exact question hit: `False`

1. Title: PlayStation®5 Pro | Witness Play Unleashed (US)
   URL: `//duckduckgo.com/l/?uddg=https%3A%2F%2Fwww.playstation.com%2Fen%2Dus%2Fps5%2Fps5%2Dpro%2F&rut=8d7f33f13396da53c5729baf5af4b18977423ba75de665d1268184e1d7ef00de`
   Snippet: Discover the PlayStation 5 Pro console, with incredible features like advanced ray tracing, super sharp image clarity for your 4K TV, and high frame rate gameplay
   String inclusion answer_hit: `False`
   Title number-margin hits: `[]`
   Snippet number-margin hits: `[]`

2. Title: Sony Interactive Entertainment Launches PlayStation 5 Pro
   URL: `//duckduckgo.com/l/?uddg=https%3A%2F%2Fsonyinteractive.com%2Fen%2Fpress%2Dreleases%2F2024%2Fsony%2Dinteractive%2Dentertainment%2Dlaunches%2Dplaystation%2D5%2Dpro%2F&rut=be5d4e754638be8da9af0d98d4cf8f3b4a1bfcdc664080e18bd5a42351df9e0a`
   Snippet: Today, Sony Interactive Entertainment expands the PlayStation®5 (PS5®) family of products with the release of the new PlayStation®5 Pro (PS5®Pro) console - the company's most advanced and innovative gaming console to date.
   String inclusion answer_hit: `True`
   Title number-margin hits: `[]`
   Snippet number-margin hits: `[]`

3. Title: Sony has released a brand new PS5 Pro - here's everything ... - TechRadar
   URL: `//duckduckgo.com/l/?uddg=https%3A%2F%2Fwww.techradar.com%2Fgaming%2Fsony%2Dhas%2Dreleased%2Da%2Dbrand%2Dnew%2Dps5%2Dpro%2Dheres%2Deverything%2Dyou%2Dneed%2Dto%2Dknow%2Dabout%2Dthe%2Dnew%2Dmodel&rut=0ee6570889f62de63ce5e9480670a76dfd12dfaf254158fd0dadd87015763287`
   Snippet: Sony has released a brand new PlayStation 5 Pro model, featuring several improvements to the original console, but don't expect them to be anything significant.
   String inclusion answer_hit: `False`
   Title number-margin hits: `[]`
   Snippet number-margin hits: `[]`

4. Title: Where Does Sony Build Its PlayStation 5 Consoles? - SlashGear
   URL: `//duckduckgo.com/l/?uddg=https%3A%2F%2Fwww.slashgear.com%2F1914020%2Fwhere%2Ddoes%2Dsony%2Dbuild%2Dplaystation%2D5%2Dconsoles%2F&rut=65cd55c41368189efcc135097da532c5720f2558875c81663bc02414b57ad48f`
   Snippet: Sony say that PlayStation 5 consoles are made in Japan. However, some consoles are made in China and even the ones made in Japan have Chinese components.
   String inclusion answer_hit: `False`
   Title number-margin hits: `[]`
   Snippet number-margin hits: `[]`

5. Title: Sony PlayStation 5 vs. PlayStation 5 Pro: Is the PSSR Boost ... - PCMag
   URL: `//duckduckgo.com/l/?uddg=https%3A%2F%2Fwww.pcmag.com%2Fcomparisons%2Fsony%2Dplaystation%2D5%2Dvs%2Dplaystation%2D5%2Dpro%2Dis%2Dpssr%2Dboost%2Dworth%2D899%2Dprice%2Dtag&rut=1a6ce16793817898c747ab2ad5f4ed5e2fcf9bfbaa945afd494a0bb082c02231`
   Snippet: The PlayStation 5 Pro now costs at least $250 more than the base PS5—but does the enhanced ray tracing, upscaling, and frame rates make it the superior console and value? I break down the ...
   String inclusion answer_hit: `False`
   Title number-margin hits: `[]`
   Snippet number-margin hits: `[]`

6. Title: PS5 Pro - The Ultimate Guide to Specs, Price, and Release Date
   URL: `//duckduckgo.com/l/?uddg=https%3A%2F%2Fwccftech.com%2Froundup%2Fps5%2Dpro%2Deverything%2Dyou%2Dneed%2Dto%2Dknow%2Dabout%2Dsonys%2Dnew%2Dconsole%2F&rut=881ae80d0feb59cf3c08e413d9d02ad91d126a53e210e23bbc8708dfd052c397`
   Snippet: Here's everything you need to know about PS5 Pro, the new Sony console due to be released worldwide on November 7, 2024.
   String inclusion answer_hit: `False`
   Title number-margin hits: `[]`
   Snippet number-margin hits: `[]`

7. Title: PlayStation 5 Pro | PlayStation Wiki | Fandom
   URL: `//duckduckgo.com/l/?uddg=https%3A%2F%2Fplaystation.fandom.com%2Fwiki%2FPlayStation_5_Pro&rut=617c849b3058e03bd99f24af57adf18696c97bf875865bafb04973326f31911f`
   Snippet: Not to be confused with PlayStation 5 or PlayStation 5 Slim. The PlayStation 5 Pro, otherwise known as PS5 Pro, is a game console developed by Sony Interactive Entertainment. It released on November 7th 2024. The PlayStation 5 Pro was formally announced by Sony on September 10, 2024, following industry rumors since March 2024. Among other changes, the new console has three primary improvements ...
   String inclusion answer_hit: `True`
   Title number-margin hits: `[]`
   Snippet number-margin hits: `[]`

8. Title: PlayStation 5 Pro: The console is officially available! Price, new ...
   URL: `//duckduckgo.com/l/?uddg=https%3A%2F%2Fwww.futura%2Dsciences.com%2Fen%2Fplaystation%2D5%2Dpro%2Dthe%2Dconsole%2Dis%2Dofficially%2Davailable%2Dprice%2Dnew%2Dfeatures%2Dand%2Dspecifications_21094%2F&rut=9e91c89fb2ee766dd8823e404a45ad371d0f0ad22bd05e567dc62832a85eaf66`
   Snippet: The wait is finally over for gamers — the PlayStation 5 Pro has officially arrived. Sony's latest release cements its position as a truly high-end console, offering a massive leap in ...
   String inclusion answer_hit: `False`
   Title number-margin hits: `[]`
   Snippet number-margin hits: `[]`

9. Title: Sony Interactive Entertainment Launches the PlayStation 5 Pro
   URL: `//duckduckgo.com/l/?uddg=https%3A%2F%2Fwww.techpowerup.com%2F328544%2Fsony%2Dinteractive%2Dentertainment%2Dlaunches%2Dthe%2Dplaystation%2D5%2Dpro&rut=b0168862f41cf54f31700a235bd13d3cc15bc4066bbc19885c93b21e85777c55`
   Snippet: The PlayStation 5 Pro console is available now at a manufacturer's suggested retail price (MSRP) of $699.99 USD, £699.99 GBP, €799.99 EUR, and ¥119,980 JPY (including tax). It will include a 2 TB solid state drive, a DualSense wireless controller, and a copy of Astro's Playroom pre-installed in every PlayStation 5 Pro purchase.
   String inclusion answer_hit: `True`
   Title number-margin hits: `[]`
   Snippet number-margin hits: `[]`

10. Title: PlayStation 5 Pro Console - PlayStation 5 - Best Buy
   URL: `//duckduckgo.com/l/?uddg=https%3A%2F%2Fwww.bestbuy.com%2Fproduct%2Fplaystation%2D5%2Dpro%2Dconsole%2Dplaystation%2D5%2FJXHQ37TR86&rut=abb05ce8bc522352744932ee698caf76dd5b333de12db8cb021f9d8e8c99417c`
   Snippet: Shop PlayStation 5 Pro Console PlayStation 5 products at Best Buy. Find low everyday prices and buy online for delivery or in-store pick-up. Price Match Guarantee.
   String inclusion answer_hit: `False`
   Title number-margin hits: `[]`
   Snippet number-margin hits: `[]`

### keyword_query_2: `PlayStation 5 Pro production company`

- Result count: `10`
- Title hits: `2`
- Snippet hits: `3`
- Answer-hit results: `3`
- Exact question hit: `False`

1. Title: Where Does Sony Build Its PlayStation 5 Consoles? - SlashGear
   URL: `//duckduckgo.com/l/?uddg=https%3A%2F%2Fwww.slashgear.com%2F1914020%2Fwhere%2Ddoes%2Dsony%2Dbuild%2Dplaystation%2D5%2Dconsoles%2F&rut=65cd55c41368189efcc135097da532c5720f2558875c81663bc02414b57ad48f`
   Snippet: Sony, a company based out of Tokyo, Japan, states that its PlayStation 5 consoles are manufactured at the Kisarazu site in Chiba, Japan, which has been in operation since 1953.
   String inclusion answer_hit: `False`
   Title number-margin hits: `[]`
   Snippet number-margin hits: `[]`

2. Title: About Us (US) - PlayStation
   URL: `//duckduckgo.com/l/?uddg=https%3A%2F%2Fwww.playstation.com%2Fen%2Dus%2Fcorporate%2Fabout%2Dus%2F&rut=307cb869fc64d9afbb6b97efc30c53cad93a86fe3bb7b86ca6319028db98a152`
   Snippet: PlayStation 5 Launched in 2020, PlayStation 5 introduced new innovations that have taken play to extraordinary new heights, including an ultra-fast SSD, Tempest 3D Audio technology, and a generation of games that harness the console's lightning speed and graphical capabilities to create incredible new experiences. (Vertical stand sold separately)
   String inclusion answer_hit: `False`
   Title number-margin hits: `[]`
   Snippet number-margin hits: `[]`

3. Title: Our Company - Sony Interactive Entertainment
   URL: `//duckduckgo.com/l/?uddg=https%3A%2F%2Fsonyinteractive.com%2Fen%2Four%2Dcompany%2F&rut=4a5b8447f7fa4cae9357cf2b638947cd6f1f4f6acebde12a54c96a8b304c312e`
   Snippet: Learn about Sony Interactive Entertainment, a global gaming and entertainment company behind PlayStation and groundbreaking interactive experiences.
   String inclusion answer_hit: `True`
   Title number-margin hits: `[]`
   Snippet number-margin hits: `[]`

4. Title: Sony has released a brand new PS5 Pro - here's everything ... - TechRadar
   URL: `//duckduckgo.com/l/?uddg=https%3A%2F%2Fwww.techradar.com%2Fgaming%2Fsony%2Dhas%2Dreleased%2Da%2Dbrand%2Dnew%2Dps5%2Dpro%2Dheres%2Deverything%2Dyou%2Dneed%2Dto%2Dknow%2Dabout%2Dthe%2Dnew%2Dmodel&rut=0ee6570889f62de63ce5e9480670a76dfd12dfaf254158fd0dadd87015763287`
   Snippet: Sony has released a brand new PlayStation 5 Pro model, featuring several improvements to the original console, but don't expect them to be anything significant.
   String inclusion answer_hit: `False`
   Title number-margin hits: `[]`
   Snippet number-margin hits: `[]`

5. Title: Sony's PlayStation 5 Pro Is a Rethink of Game Console Business Model ...
   URL: `//duckduckgo.com/l/?uddg=https%3A%2F%2Fwww.bloomberg.com%2Fnews%2Fnewsletters%2F2024%2D09%2D17%2Fsony%2Ds%2Dplaystation%2D5%2Dpro%2Dis%2Da%2Drethink%2Dof%2Dgame%2Dconsole%2Dbusiness%2Dmodel&rut=0371993d0413e1d0cd5d352c04dd3bed50ce1503d27bb7f2d66e899e23424a0d`
   Snippet: The company offered a head-scratching peek at its future strategy when it announced its priciest console to date with the upcoming PlayStation 5 Pro.
   String inclusion answer_hit: `False`
   Title number-margin hits: `[]`
   Snippet number-margin hits: `[]`

6. Title: PS5 Pro - The Ultimate Guide to Specs, Price, and Release Date
   URL: `//duckduckgo.com/l/?uddg=https%3A%2F%2Fwccftech.com%2Froundup%2Fps5%2Dpro%2Deverything%2Dyou%2Dneed%2Dto%2Dknow%2Dabout%2Dsonys%2Dnew%2Dconsole%2F&rut=881ae80d0feb59cf3c08e413d9d02ad91d126a53e210e23bbc8708dfd052c397`
   Snippet: Here's everything you need to know about PS5 Pro, the new Sony console due to be released worldwide on November 7, 2024.
   String inclusion answer_hit: `False`
   Title number-margin hits: `[]`
   Snippet number-margin hits: `[]`

7. Title: The PS5 Pro had a truly shocking development timeline
   URL: `//duckduckgo.com/l/?uddg=https%3A%2F%2Fwww.pocket%2Dlint.com%2Fps5%2Dpro%2Dwas%2Da%2Dfive%2Dyear%2Dproject%2F&rut=16693a6c430a72a7e7b91df782a1d4d7ee293caae20e5fa4b15a7a15ab61e33a`
   Snippet: The PlayStation 5 Pro launches November 7th with a hefty price tag of $700. The Pro is launching four years after the PlayStation 5 first made its debut in 2020. The PS5 Pro features a brand-new ...
   String inclusion answer_hit: `False`
   Title number-margin hits: `[]`
   Snippet number-margin hits: `[]`

8. Title: PlayStation 5 Pro | PlayStation Wiki | Fandom
   URL: `//duckduckgo.com/l/?uddg=https%3A%2F%2Fplaystation.fandom.com%2Fwiki%2FPlayStation_5_Pro&rut=617c849b3058e03bd99f24af57adf18696c97bf875865bafb04973326f31911f`
   Snippet: Not to be confused with PlayStation 5 or PlayStation 5 Slim. The PlayStation 5 Pro, otherwise known as PS5 Pro, is a game console developed by Sony Interactive Entertainment. It released on November 7th 2024. The PlayStation 5 Pro was formally announced by Sony on September 10, 2024, following industry rumors since March 2024. Among other changes, the new console has three primary improvements ...
   String inclusion answer_hit: `True`
   Title number-margin hits: `[]`
   Snippet number-margin hits: `[]`

9. Title: Sony Interactive Entertainment Launches PlayStation 5 Pro
   URL: `//duckduckgo.com/l/?uddg=https%3A%2F%2Fsonyinteractive.com%2Fen%2Fpress%2Dreleases%2F2024%2Fsony%2Dinteractive%2Dentertainment%2Dlaunches%2Dplaystation%2D5%2Dpro%2F&rut=be5d4e754638be8da9af0d98d4cf8f3b4a1bfcdc664080e18bd5a42351df9e0a`
   Snippet: Today, Sony Interactive Entertainment expands the PlayStation®5 (PS5®) family of products with the release of the new PlayStation®5 Pro (PS5®Pro) console - the company's most advanced and innovative gaming console to date.
   String inclusion answer_hit: `True`
   Title number-margin hits: `[]`
   Snippet number-margin hits: `[]`

10. Title: The PlayStation 5 Pro has finally been unveiled - Game Developer
   URL: `//duckduckgo.com/l/?uddg=https%3A%2F%2Fwww.gamedeveloper.com%2Fbusiness%2Fthe%2Dplaystation%2D5%2Dpro%2Dhas%2Dfinally%2Dbeen%2Dunveiled&rut=da49694c2c6942bb9b35c96cd2d603722ed4b866dabc48448e7a89795a5675f9`
   Snippet: The company launched a PlayStation 4 Pro to pack more power into its last-generation machine. Microsoft has also taken a similar approach, bolstering the Xbox One range with the launch of the more powerful Xbox One X and slimline Xbox One S.
   String inclusion answer_hit: `False`
   Title number-margin hits: `[]`
   Snippet number-margin hits: `[]`

### keyword_query_3: `company behind PlayStation 5 Pro`

- Result count: `9`
- Title hits: `1`
- Snippet hits: `2`
- Answer-hit results: `2`
- Exact question hit: `False`

1. Title: PlayStation - Wikipedia
   URL: `//duckduckgo.com/l/?uddg=https%3A%2F%2Fen.wikipedia.org%2Fwiki%2FPlayStation&rut=27f2d7afa583842522815ae8bcebdd701bc8ecee9410faa94f4f9c18b1fc89e6`
   Snippet: PlayStation was the brainchild of Ken Kutaragi, a Sony executive who managed one of the company's hardware engineering divisions and was later dubbed "The Father of the PlayStation". [4][5] One of two known remaining prototypes of Sony's original "PlayStation", a Super NES with a built-in CD-ROM drive [6] Until 1991, Sony had little direct involvement with the video game industry. The company ...
   String inclusion answer_hit: `False`
   Title number-margin hits: `[]`
   Snippet number-margin hits: `[]`

2. Title: PlayStation 5 Pro Teardown: An inside look at the most advanced ...
   URL: `//duckduckgo.com/l/?uddg=https%3A%2F%2Fblog.playstation.com%2F2025%2F04%2F21%2Fplaystation%2D5%2Dpro%2Dteardown%2Dan%2Dinside%2Dlook%2Dat%2Dthe%2Dmost%2Dadvanced%2Dplaystation%2Dconsole%2Dto%2Ddate%2F&rut=262d8b6f5fff6606b7bcc69d0677c60010fc2f5f63f8a3e541ccc98f93c4da94`
   Snippet: PlayStation 5 Pro console — the most innovative PlayStation console to date — elevates gaming experiences to the next level with features like upgraded GPU, advanced ray tracing, and PlayStation Spectral Super Resolution (PSSR) - an AI-driven upscaling that delivers super sharp image clarity with high framerate gameplay. Today we're providing a closer look at the console's internal ...
   String inclusion answer_hit: `False`
   Title number-margin hits: `[]`
   Snippet number-margin hits: `[]`

3. Title: Sony Interactive Entertainment
   URL: `//duckduckgo.com/l/?uddg=https%3A%2F%2Fsonyinteractive.com%2Fen%2F&rut=b03c7f202ef4b1a1c54a6c4a4c5df83f09133856f2383f343415b7f83fd938ac`
   Snippet: Sony Interactive Entertainment, the company behind PlayStation, is a global pioneer in video game entertainment.
   String inclusion answer_hit: `True`
   Title number-margin hits: `[]`
   Snippet number-margin hits: `[]`

4. Title: Who owns PS5? - Games Learning Society
   URL: `//duckduckgo.com/l/?uddg=https%3A%2F%2Fwww.gameslearningsociety.org%2Fwiki%2Fwho%2Downs%2Dps5%2F&rut=63a3a4507c310d5b78b2254fa176c6c0cfa425af06b0f1d750d61f08d6f59cb1`
   Snippet: Who Owns the PS5? Unveiling the Power Behind the PlayStation The PlayStation 5 (PS5) has become a cultural phenomenon, dominating living rooms and sparking conversations worldwide. But behind the sleek design and immersive gaming experience lies a complex corporate structure. So, who exactly owns the PS5? The short and definitive answer is: Sony Interactive Entertainment LLC (SIE). However ...
   String inclusion answer_hit: `True`
   Title number-margin hits: `[]`
   Snippet number-margin hits: `[]`

5. Title: PS5 vs. PS5 Slim vs. PS5 Pro: What's the Difference, and ... - WIRED
   URL: `//duckduckgo.com/l/?uddg=https%3A%2F%2Fwww.wired.com%2Fstory%2Fps5%2Dvs%2Dps5%2Dslim%2Dvs%2Dps5%2Dpro%2Dwhats%2Dthe%2Ddifference%2Dand%2Dwhich%2Done%2Dshould%2Dyou%2Dget%2F&rut=9092135aed835ff112c5fdb24757def2539e79df83a319f94d4a465664f52fe7`
   Snippet: The PS5 Pro features the new PlayStation Spectral Super Resolution that lets the game engine calculate lower-resolution versions of frames, and then apply the upscaling technique to make the ...
   String inclusion answer_hit: `False`
   Title number-margin hits: `[]`
   Snippet number-margin hits: `[]`

6. Title: Sony has released a brand new PS5 Pro - here's everything ... - TechRadar
   URL: `//duckduckgo.com/l/?uddg=https%3A%2F%2Fwww.techradar.com%2Fgaming%2Fsony%2Dhas%2Dreleased%2Da%2Dbrand%2Dnew%2Dps5%2Dpro%2Dheres%2Deverything%2Dyou%2Dneed%2Dto%2Dknow%2Dabout%2Dthe%2Dnew%2Dmodel&rut=0ee6570889f62de63ce5e9480670a76dfd12dfaf254158fd0dadd87015763287`
   Snippet: Sony has released a brand new PlayStation 5 Pro model, featuring several improvements to the original console, but don't expect them to be anything significant.
   String inclusion answer_hit: `False`
   Title number-margin hits: `[]`
   Snippet number-margin hits: `[]`

7. Title: The big PlayStation 5 Pro tech interview with Mark Cerny and Mike ...
   URL: `//duckduckgo.com/l/?uddg=https%3A%2F%2Fwww.digitalfoundry.net%2Farticles%2Fdigitalfoundry%2D2024%2Dsony%2Dps5%2Dpro%2Dtech%2Dinterview%2Dwith%2Dmark%2Dcerny%2Dand%2Dmike%2Dfitzgerald&rut=7aba6e08c8498a920c6dca3f655b6266c6f1610413710eeda9a2ba1bc633860b`
   Snippet: Here's the full interview with PS5 Pro lead system architect Mark Cerny and Insomniac Games core technology director, Mike Fitzgerald. Digital Foundry: I wanted to start off here by talking about PSSR, PlayStation Spectral Super Resolution. There has been a little bit of a difference in terms of approach between developers like Naughty Dog and Square Enix in terms of the modes that they're ...
   String inclusion answer_hit: `False`
   Title number-margin hits: `[]`
   Snippet number-margin hits: `[]`

8. Title: The PS5 Pro had a truly shocking development timeline
   URL: `//duckduckgo.com/l/?uddg=https%3A%2F%2Fwww.pocket%2Dlint.com%2Fps5%2Dpro%2Dwas%2Da%2Dfive%2Dyear%2Dproject%2F&rut=16693a6c430a72a7e7b91df782a1d4d7ee293caae20e5fa4b15a7a15ab61e33a`
   Snippet: The PlayStation 5 Pro launches November 7th with a hefty price tag of $700. The Pro is launching four years after the PlayStation 5 first made its debut in 2020. The PS5 Pro features a brand-new ...
   String inclusion answer_hit: `False`
   Title number-margin hits: `[]`
   Snippet number-margin hits: `[]`

9. Title: PlayStation®5 Design Story | Stories - Sony Group Portal
   URL: `//duckduckgo.com/l/?uddg=https%3A%2F%2Fwww.sony.com%2Fen%2FSonyInfo%2Fdesign%2Fstories%2FPS5%2F&rut=9650338c0518f5fe1207ce51f86bb428211fcb3f8f630eafd1451a81f590e1ab`
   Snippet: The design concept is "five dimensions." This is a story of the design process that led to the creation of PlayStation®️5, a product that represents the designers' attempt to create a new generation of gaming experience—one that feels as if the world inside a game has merged with physical space.
   String inclusion answer_hit: `False`
   Title number-margin hits: `[]`
   Snippet number-margin hits: `[]`

### keyword_query_4: `who makes PlayStation 5 Pro`

- Result count: `10`
- Title hits: `1`
- Snippet hits: `1`
- Answer-hit results: `1`
- Exact question hit: `False`

1. Title: Sony PlayStation 5 vs. PlayStation 5 Pro: Is the PSSR Boost ... - PCMag
   URL: `//duckduckgo.com/l/?uddg=https%3A%2F%2Fwww.pcmag.com%2Fcomparisons%2Fsony%2Dplaystation%2D5%2Dvs%2Dplaystation%2D5%2Dpro%2Dis%2Dpssr%2Dboost%2Dworth%2D899%2Dprice%2Dtag&rut=1a6ce16793817898c747ab2ad5f4ed5e2fcf9bfbaa945afd494a0bb082c02231`
   Snippet: The PlayStation 5 Pro now costs at least $250 more than the base PS5—but does the enhanced ray tracing, upscaling, and frame rates make it the superior console and value? I break down the ...
   String inclusion answer_hit: `False`
   Title number-margin hits: `[]`
   Snippet number-margin hits: `[]`

2. Title: PlayStation®5 Pro | Witness Play Unleashed (US)
   URL: `//duckduckgo.com/l/?uddg=https%3A%2F%2Fwww.playstation.com%2Fen%2Dus%2Fps5%2Fps5%2Dpro%2F&rut=8d7f33f13396da53c5729baf5af4b18977423ba75de665d1268184e1d7ef00de`
   Snippet: PlayStation ® 5 Pro Play PS5® games with the most impressive visuals ever possible on a PlayStation console.
   String inclusion answer_hit: `False`
   Title number-margin hits: `[]`
   Snippet number-margin hits: `[]`

3. Title: Sony has released a brand new PS5 Pro - here's everything ... - TechRadar
   URL: `//duckduckgo.com/l/?uddg=https%3A%2F%2Fwww.techradar.com%2Fgaming%2Fsony%2Dhas%2Dreleased%2Da%2Dbrand%2Dnew%2Dps5%2Dpro%2Dheres%2Deverything%2Dyou%2Dneed%2Dto%2Dknow%2Dabout%2Dthe%2Dnew%2Dmodel&rut=0ee6570889f62de63ce5e9480670a76dfd12dfaf254158fd0dadd87015763287`
   Snippet: Sony has released a brand new PlayStation 5 Pro model, featuring several improvements to the original console, but don't expect them to be anything significant.
   String inclusion answer_hit: `False`
   Title number-margin hits: `[]`
   Snippet number-margin hits: `[]`

4. Title: Sony Interactive Entertainment Launches PlayStation 5 Pro
   URL: `//duckduckgo.com/l/?uddg=https%3A%2F%2Fsonyinteractive.com%2Fen%2Fpress%2Dreleases%2F2024%2Fsony%2Dinteractive%2Dentertainment%2Dlaunches%2Dplaystation%2D5%2Dpro%2F&rut=be5d4e754638be8da9af0d98d4cf8f3b4a1bfcdc664080e18bd5a42351df9e0a`
   Snippet: Today, Sony Interactive Entertainment expands the PlayStation®5 (PS5®) family of products with the release of the new PlayStation®5 Pro (PS5®Pro) console - the company's most advanced and innovative gaming console to date.
   String inclusion answer_hit: `True`
   Title number-margin hits: `[]`
   Snippet number-margin hits: `[]`

5. Title: PS5 vs. PS5 Slim vs. PS5 Pro: What's the Difference, and ... - WIRED
   URL: `//duckduckgo.com/l/?uddg=https%3A%2F%2Fwww.wired.com%2Fstory%2Fps5%2Dvs%2Dps5%2Dslim%2Dvs%2Dps5%2Dpro%2Dwhats%2Dthe%2Ddifference%2Dand%2Dwhich%2Done%2Dshould%2Dyou%2Dget%2F&rut=9092135aed835ff112c5fdb24757def2539e79df83a319f94d4a465664f52fe7`
   Snippet: The PS5 Pro features the new PlayStation Spectral Super Resolution that lets the game engine calculate lower-resolution versions of frames, and then apply the upscaling technique to make the ...
   String inclusion answer_hit: `False`
   Title number-margin hits: `[]`
   Snippet number-margin hits: `[]`

6. Title: PlayStation 5 vs. PlayStation 5 Pro: Comparing Every PS5 - CNET
   URL: `//duckduckgo.com/l/?uddg=https%3A%2F%2Fwww.cnet.com%2Ftech%2Fgaming%2Fps5%2Dslim%2Dvs%2Dps5%2Ddigital%2Dvs%2Dps5%2Dpro%2Devery%2Dfeature%2Dcompared%2F&rut=3f2063ce3149945324b2a770ddf402afe44273578d0e70fcd15f7ea73e2dd1e1`
   Snippet: Oscar Gonzalez is a Texas native who covered video games, conspiracy theories, misinformation and cryptocurrency. There are three variants of the PS5 console -- Digital, Slim and Pro -- so the ...
   String inclusion answer_hit: `False`
   Title number-margin hits: `[]`
   Snippet number-margin hits: `[]`

7. Title: Sony Makes PlayStation 5 Price Hike Official: PS5 Pro ... - TechPowerUp
   URL: `//duckduckgo.com/l/?uddg=https%3A%2F%2Fwww.techpowerup.com%2F347817%2Fsony%2Dmakes%2Dplaystation%2D5%2Dprice%2Dhike%2Dofficial%2Dps5%2Dpro%2Dusd%2D899%2D99%2Dfrom%2Dapril%2D2&rut=d6f974d1b164cc183ed4ab709a7bf8c67fba04ef596feb3ccdc9566c06ff2f95`
   Snippet: A recent leak claimed that Sony would be increasing the price of the PlayStation 5 across the board by as much as €100 in Europe, although it was unclear at the time whether the US and other international markets would see the same price increases. Now, thanks to an official PlayStation Blog post, S...
   String inclusion answer_hit: `False`
   Title number-margin hits: `[]`
   Snippet number-margin hits: `[]`

8. Title: Where Does Sony Build Its PlayStation 5 Consoles? - SlashGear
   URL: `//duckduckgo.com/l/?uddg=https%3A%2F%2Fwww.slashgear.com%2F1914020%2Fwhere%2Ddoes%2Dsony%2Dbuild%2Dplaystation%2D5%2Dconsoles%2F&rut=65cd55c41368189efcc135097da532c5720f2558875c81663bc02414b57ad48f`
   Snippet: Sony say that PlayStation 5 consoles are made in Japan. However, some consoles are made in China and even the ones made in Japan have Chinese components.
   String inclusion answer_hit: `False`
   Title number-margin hits: `[]`
   Snippet number-margin hits: `[]`

9. Title: PS5 Pro Year One: Was It Worth It? | Digital Foundry
   URL: `//duckduckgo.com/l/?uddg=https%3A%2F%2Fwww.digitalfoundry.net%2Ffeatures%2Fps5%2Dpro%2Dyear%2Done%2Dwas%2Dit%2Dworth%2Dit&rut=5d06f5a151dd27653f4520beff80c98dbdb32f3f6bab80e5c85eb120563e7722`
   Snippet: We met last year's PlayStation 5 Pro with a comprehensive, technical analysis of what it brought to the PS5 party, as much in technical specs as in launch-window game testing. But early impressions don't tell the full story of a mid-generation hardware refresh. That leads us to today, the one-year anniversary of its November 2024 launch, with an opportunity to review the full PS5 Pro games ...
   String inclusion answer_hit: `False`
   Title number-margin hits: `[]`
   Snippet number-margin hits: `[]`

10. Title: PS5 Pro - The Ultimate Guide to Specs, Price, and Release Date
   URL: `//duckduckgo.com/l/?uddg=https%3A%2F%2Fwccftech.com%2Froundup%2Fps5%2Dpro%2Deverything%2Dyou%2Dneed%2Dto%2Dknow%2Dabout%2Dsonys%2Dnew%2Dconsole%2F&rut=881ae80d0feb59cf3c08e413d9d02ad91d126a53e210e23bbc8708dfd052c397`
   Snippet: Here's everything you need to know about PS5 Pro, the new Sony console due to be released worldwide on November 7, 2024.
   String inclusion answer_hit: `False`
   Title number-margin hits: `[]`
   Snippet number-margin hits: `[]`

### keyword_query_5: `PlayStation 5 Pro maker`

- Result count: `10`
- Title hits: `1`
- Snippet hits: `2`
- Answer-hit results: `2`
- Exact question hit: `False`

1. Title: Create Games for PlayStation | Unity
   URL: `//duckduckgo.com/l/?uddg=https%3A%2F%2Funity.com%2Fsolutions%2Fplaystation&rut=9763d2158518a71d9bd88a622b2e7d86710eb578dd6a3feded7988b41127a5de`
   Snippet: Create, launch, and operate your game with a comprehensive game development platform for PlayStation 5 and PlayStation 5 Pro.
   String inclusion answer_hit: `False`
   Title number-margin hits: `[]`
   Snippet number-margin hits: `[]`

2. Title: PlayStation 30th Anniversary range | Limited Edition consoles and ...
   URL: `//duckduckgo.com/l/?uddg=https%3A%2F%2Fwww.playstation.com%2Fen%2Dus%2F30th%2Danniversary%2Dcollection%2F&rut=0677c1bb757ef7f6c1cc84b4a06d097122eb8be7de7043fb3776737d5d250f99`
   Snippet: PlayStation®5 Pro Console - 30 th Anniversary Limited Edition Bundle 30 years of PlayStation history combines with the future of play in this incredible limited-edition bundle.
   String inclusion answer_hit: `False`
   Title number-margin hits: `[]`
   Snippet number-margin hits: `[]`

3. Title: Custom PlayStation 5 Pro Hand-Painted Consoles - Craft by Merlin
   URL: `//duckduckgo.com/l/?uddg=https%3A%2F%2Fcraftbymerlin.com%2Fblogs%2Fnews%2Fcustom%2Dplaystation%2D5%2Dpro%2Dhand%2Dpainted%2Dconsoles&rut=e8c6ba6f508abbe37b8e9265d340185a8e2f9e44980033e9c0a789e8b2d0cdf9`
   Snippet: Discover Craft by Merlin's custom PlayStation 5 Pro hand-painted consoles. Unique designs, brand-new devices, 1-year global warranty. Elevate your gaming setup with style and individuality.
   String inclusion answer_hit: `False`
   Title number-margin hits: `[]`
   Snippet number-margin hits: `[]`

4. Title: Sony Interactive Entertainment Launches PlayStation 5 Pro
   URL: `//duckduckgo.com/l/?uddg=https%3A%2F%2Fsonyinteractive.com%2Fen%2Fpress%2Dreleases%2F2024%2Fsony%2Dinteractive%2Dentertainment%2Dlaunches%2Dplaystation%2D5%2Dpro%2F&rut=be5d4e754638be8da9af0d98d4cf8f3b4a1bfcdc664080e18bd5a42351df9e0a`
   Snippet: Today, Sony Interactive Entertainment expands the PlayStation®5 (PS5®) family of products with the release of the new PlayStation®5 Pro (PS5®Pro) console - the company's most advanced and innovative gaming console to date.
   String inclusion answer_hit: `True`
   Title number-margin hits: `[]`
   Snippet number-margin hits: `[]`

5. Title: Sony PlayStation 5 vs. PlayStation 5 Pro: Is the PSSR Boost ... - PCMag
   URL: `//duckduckgo.com/l/?uddg=https%3A%2F%2Fwww.pcmag.com%2Fcomparisons%2Fsony%2Dplaystation%2D5%2Dvs%2Dplaystation%2D5%2Dpro%2Dis%2Dpssr%2Dboost%2Dworth%2D899%2Dprice%2Dtag&rut=1a6ce16793817898c747ab2ad5f4ed5e2fcf9bfbaa945afd494a0bb082c02231`
   Snippet: The PlayStation 5 Pro now costs at least $250 more than the base PS5—but does the enhanced ray tracing, upscaling, and frame rates make it the superior console and value? I break down the ...
   String inclusion answer_hit: `False`
   Title number-margin hits: `[]`
   Snippet number-margin hits: `[]`

6. Title: PS5 Custom Controller Creator
   URL: `//duckduckgo.com/l/?uddg=https%3A%2F%2Fwww.evilcontrollers.com%2Fps5%2Dcustom%2Dcontroller%2Dcreator&rut=690f642ed8341869c2337d8da83d9c4ecb6dfa6fc75c1b1be326539b79ef03df`
   Snippet: Create the ultimate PS5 custom controller with our controller creator, featuring endless customization.
   String inclusion answer_hit: `False`
   Title number-margin hits: `[]`
   Snippet number-margin hits: `[]`

7. Title: PlayStation 5 Pro Custom Skin, Wrap & Cover - Slickwraps
   URL: `//duckduckgo.com/l/?uddg=https%3A%2F%2Fwww.slickwraps.com%2Fproducts%2Fplaystation%2D5%2Dpro%2Dcustom&rut=e905ffd08641e1031baf7f03b02d9776a3e2cddb0c6e3e30a7719ee6e61e6359`
   Snippet: Personalize your PlayStation 5 Pro like never before with our Custom Skin option. Whether you want to showcase your unique style, favorite artwork, or promote your brand, our custom skins provide the perfect canvas to express yourself. Each skin is made from high-quality, durable materials that protect your device from scratches and daily wear while ensuring a seamless, bubble-free application ...
   String inclusion answer_hit: `False`
   Title number-margin hits: `[]`
   Snippet number-margin hits: `[]`

8. Title: PS5 Pro: all the news about Sony's next console | The Verge
   URL: `//duckduckgo.com/l/?uddg=https%3A%2F%2Fwww.theverge.com%2F24240801%2Fps5%2Dpro%2Ddetails%2Dplaystation%2Devent%2Dseptember%2D2024&rut=58a3d7e75a2ac8e569bd041f0ace7ba17fc484d264b3dbbf0a69eafadf87dca2`
   Snippet: Sony's PlayStation 5 Pro will go on sale on November 7th for $699.99, with a 2TB SSD, no optical disc drive, Wi-Fi 7, and upgraded GPU.
   String inclusion answer_hit: `False`
   Title number-margin hits: `[]`
   Snippet number-margin hits: `[]`

9. Title: PlayStation 5 Pro | PlayStation Wiki | Fandom
   URL: `//duckduckgo.com/l/?uddg=https%3A%2F%2Fplaystation.fandom.com%2Fwiki%2FPlayStation_5_Pro&rut=617c849b3058e03bd99f24af57adf18696c97bf875865bafb04973326f31911f`
   Snippet: Not to be confused with PlayStation 5 or PlayStation 5 Slim. The PlayStation 5 Pro, otherwise known as PS5 Pro, is a game console developed by Sony Interactive Entertainment. It released on November 7th 2024. The PlayStation 5 Pro was formally announced by Sony on September 10, 2024, following industry rumors since March 2024. Among other changes, the new console has three primary improvements ...
   String inclusion answer_hit: `True`
   Title number-margin hits: `[]`
   Snippet number-margin hits: `[]`

10. Title: Cinch Gaming Custom PS5 and Xbox Controllers
   URL: `//duckduckgo.com/l/?uddg=https%3A%2F%2Fwww.cinchgaming.com%2F&rut=f4be4b7f6a892e6cb874ec58156c843fa55ffbead1f8eeb605029176e0f8e1ff`
   Snippet: Cinch Gaming creates custom PlayStation (PS5) and Xbox (Series X and Xbox One) gaming controllers. Perfect for Warzone, Fortnite, Halo, Call of Duty and any esports games. The #1 pro esports controller is all next gen. Add Click Triggers (Digital Triggers) for instant mouse click shooting on PC. PS5 and Xbox Series X.
   String inclusion answer_hit: `False`
   Title number-margin hits: `[]`
   Snippet number-margin hits: `[]`

## Cheap-Model QA And Grader Judgement

- Cheap-model rejection features: `{"enabled": false, "reason": "cheap_model_longtail_rejection_removed_for_simpleqa_verified_alignment"}`
- Panel enabled: `True`
- Panel question: `Who is the manufacturer of the PlayStation 5 Pro?`
- Reference answer for grading: `Sony Interactive Entertainment`
- Accuracy threshold: `1.0`
- Accuracy: `1.0`
- Attempt rate: `1.0`
- Duration seconds: `13.5084`

### Model: `openai/gpt-4.1-mini`

- Small-model answer: The manufacturer of the PlayStation 5 Pro is Sony.
- Answer duration seconds: `3.5354`
- Grader judgement: `CORRECT`
- Grader reason: Sony is an acceptable alias for Sony Interactive Entertainment, the manufacturer of the PlayStation 5 Pro.
- Grading method: `llm_grader`
- Grading duration seconds: `3.8982`

### Model: `google/gemini-3-flash-preview`

- Small-model answer: The manufacturer of the PlayStation 5 Pro is **Sony Interactive Entertainment**.
- Answer duration seconds: `1.6916`
- Grader judgement: `CORRECT`
- Grader reason: The predicted answer matches the reference answer exactly and is an accepted alias.
- Grading method: `llm_grader`
- Grading duration seconds: `4.3831`

## Notes And Problems

- WDQS was the practical bottleneck: both the heavy direct path and the day-window subject seed path timed out.
- The API-light fallback was necessary for this successful walkthrough.
- DuckDuckGo results were mostly cache hits in the final rerun, so search elapsed time was low.
- The PowerShell profile emitted a broken conda-hook warning after command completion: `D:\python2022\Scripts\conda.exe` was not found. This did not affect the completed run.
- The stage-1 threshold bug found during rerun was fixed: title answer hits now respect configured thresholds instead of rejecting unconditionally.
