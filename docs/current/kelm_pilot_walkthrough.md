# KELM 10-Record Pilot Walkthrough

This note walks through the latest 10-record KELM pilot run from:

- [data/kelm/quadruples-train.tsv](D:/Study/AI/My-research/Wikidata_Framework/data/kelm/quadruples-train.tsv)

Run command:

```powershell
python scripts\run_kelm_half_pipeline.py --record-limit 10 --enable-rewrite
```

Artifacts:

- accepted: [outputs/kelm_half_pipeline_accepted.jsonl](D:/Study/AI/My-research/Wikidata_Framework/outputs/kelm_half_pipeline_accepted.jsonl)
- rejected: [outputs/kelm_half_pipeline_rejected.jsonl](D:/Study/AI/My-research/Wikidata_Framework/outputs/kelm_half_pipeline_rejected.jsonl)
- summary: [outputs/kelm_half_pipeline_summary.json](D:/Study/AI/My-research/Wikidata_Framework/outputs/kelm_half_pipeline_summary.json)

Summary:

- generated: `10`
- accepted: `0`
- rejected: `10`

## Outcome buckets

- `entity_grounding_failed`: `3`
- `unsupported_relation_record`: `4`
- `search_longtail_verifier_rejected`: `2`
- `search_longtail_verifier_error`: `0` after the isolated Case 4 rerun

## Important run note

The pipeline is currently configured with `duckduckgo_top_k = 10`, but in these stored artifacts the recorded DuckDuckGo query rows still returned `5` results per query. So the walkthrough below reports the actual observed result counts from the JSONL, not the configured maximum.

Case 4 was rerun separately after the network recovered. The walkthrough below reflects the rerun outcome for that case rather than the earlier transient transport error.

## Case 1

Serialized triples:
`Mikhail Belyaev date of death 01 January 1918, allegiance Russian Empire, position held minister of war, country of citizenship Russian Empire, date of birth 23 December 1863`

Original KELM sentence:
`Mikhail Alekseyevich Belyaev (Russian: ; December 23, 1863 - 1918) was a Russian general of the Infantry, statesman, Chief of Staff of the Imperial Russian Army from August 1, 1914 to August 10, 1916, and was the last Minister of War of the Russian Empire from January 3, 1917 to February 28, 1917.`

Selected supported triple:
`Mikhail Belyaev` -> `date of death` -> `01 January 1918`

Rewritten question:
None. Rewrite was never reached.

Outcome:
- `entity_grounding_failed`

What happened:
- The row contains a supported relation, so it was not rejected for relation coverage.
- The conservative entity resolver tried to ground `Mikhail Belyaev` from the triple text.
- The richer sentence form uses `Mikhail Alekseyevich Belyaev`, so the subject string in the triple is weaker than the sentence string.
- The current resolver requires a conservative exact-label match, so this row stopped before rewrite.

DuckDuckGo evidence:
- none, because search was never reached

## Case 2

Serialized triple:
`Shiels Jewellers inception 01 January 1945`

Original KELM sentence:
`Shiels Jewellers is an Australian jewellery retailer and was founded by Jack Shiels in Adelaide in 1945.`

Rewritten question:
`In which year was the Australian jewellery retailer Shiels Jewellers, founded by Jack Shiels in Adelaide, established?`

LLM keyword queries:
- `Shiels Jewellers founding year`
- `"Jack Shiels" jewellery retailer Adelaide establishment date`
- `year Shiels Jewellers started in Australia`
- `history of Shiels Jewellers foundation`

Outcome:
- `search_longtail_verifier_rejected`

Hit rates:
- `full_question`: `1.0`
- `keyword_queries`: `0.95`
- `overall`: `0.96`

Triggered rule:
- `full_question:hit_rate_exceeded`

DuckDuckGo evidence:

`full_question`
- URL: `//duckduckgo.com/l/?uddg=https%3A%2F%2Fwww.shiels.com.au%2Fpages%2Four%2Dstory&rut=07655a18d836f58c1ee8e5351b00723a06f3ca311094d1457d04b5774a515348`
  Snippet: `The Shiels Story With the goal of providing high quality, valuable and unique jewellery pieces, Shiels was founded in 1945 and has remained an Australian family business ever since. Originally owned by Jack and Jeanne Shiels, the business quickly earned a reputation for consistently making beautiful, unique and long-lasting jewellery pieces.`
- URL: `//duckduckgo.com/l/?uddg=https%3A%2F%2Fwww.retailbiz.com.au%2Flatest%2Dnews%2Fshiels%2Djewellers%2Dcelebrates%2D80%2Dyears%2Din%2Dbusiness%2F&rut=ed530e9f7d8bb3d5f3245a6388ef8a0af8dbc048d195f77378201e48408507d7`
  Snippet: `Australian jeweller Shiels Jewellers is celebrating 80 years in business with a 35-day promotion until 30 March 2025, featuring a special discounted catalogue, weekly jewellery party bag giveaways and a nostalgic video advertisement. Founded in 1945 by Jack and Jeanne Shiels at Adelaide's Central Market Arcade, the small family-run jewellery store has evolved into a national retailer with ...`

`keyword_query_1`: `Shiels Jewellers founding year`
- URL: `//duckduckgo.com/l/?uddg=https%3A%2F%2Fen.wikipedia.org%2Fwiki%2FShiels_Jewellers&rut=9c52f9edd764ff35bb0b2ae838e69db18e57482c7cbc618ceb71978e04aae695`
  Snippet: `Shiels Jewellers is an Australian jewellery retailer and was founded by Jack Shiels in Adelaide in 1945. [1][2][3][4][5] Since then, Shiels has expanded to 40 stores across South Australia, Queensland, New South Wales and Western Australia, employing over 450 people.`
- URL: `//duckduckgo.com/l/?uddg=https%3A%2F%2Fwww.shiels.com.au%2Fpages%2Four%2Dstory&rut=07655a18d836f58c1ee8e5351b00723a06f3ca311094d1457d04b5774a515348`
  Snippet: `The Shiels Story With the goal of providing high quality, valuable and unique jewellery pieces, Shiels was founded in 1945 and has remained an Australian family business ever since. Originally owned by Jack and Jeanne Shiels, the business quickly earned a reputation for consistently making beautiful, unique and long-lasting jewellery pieces.`

`keyword_query_2`: `"Jack Shiels" jewellery retailer Adelaide establishment date`
- URL: `//duckduckgo.com/l/?uddg=https%3A%2F%2Fen.wikipedia.org%2Fwiki%2FShiels_Jewellers&rut=9c52f9edd764ff35bb0b2ae838e69db18e57482c7cbc618ceb71978e04aae695`
  Snippet: `Shiels Jewellers is an Australian jewellery retailer and was founded by Jack Shiels in Adelaide in 1945. [1][2][3][4][5] Since then, Shiels has expanded to 40 stores across South Australia, Queensland, New South Wales and Western Australia, employing over 450 people. Shiels remains headquartered in Adelaide, South Australia, and currently sells bridal and diamond jewellery in a variety of ...`
- URL: `//duckduckgo.com/l/?uddg=https%3A%2F%2Feverything.explained.today%2FShiels_Jewellers%2F&rut=d390f9549e3c2cf0ad7a747458a5def886643e8e9d4caad4d2ab25804db67acd`
  Snippet: `Shiels Jewellers is an Australian jewellery retailer and was founded by Jack Shiels in Adelaide in 1945. [1][2][3][4][5] Since then, Shiels has expanded to 40 stores across South Australia, Queensland, New South Wales and Western Australia, employing over 450 people. Shiels remains headquartered in Adelaide, South Australia, and currently sells bridal and diamond jewellery in a variety of ...`

`keyword_query_3`: `year Shiels Jewellers started in Australia`
- URL: `//duckduckgo.com/l/?uddg=https%3A%2F%2Fen.wikipedia.org%2Fwiki%2FShiels_Jewellers&rut=9c52f9edd764ff35bb0b2ae838e69db18e57482c7cbc618ceb71978e04aae695`
  Snippet: `Shiels Jewellers is an Australian jewellery retailer and was founded by Jack Shiels in Adelaide in 1945. [1][2][3][4][5] Since then, Shiels has expanded to 40 stores across South Australia, Queensland, New South Wales and Western Australia, employing over 450 people.`
- URL: `//duckduckgo.com/l/?uddg=https%3A%2F%2Fwww.shiels.com.au%2Fpages%2Four%2Dstory&rut=07655a18d836f58c1ee8e5351b00723a06f3ca311094d1457d04b5774a515348`
  Snippet: `The Shiels Story With the goal of providing high quality, valuable and unique jewellery pieces, Shiels was founded in 1945 and has remained an Australian family business ever since. Originally owned by Jack and Jeanne Shiels, the business quickly earned a reputation for consistently making beautiful, unique and long-lasting jewellery pieces.`

`keyword_query_4`: `history of Shiels Jewellers foundation`
- URL: `//duckduckgo.com/l/?uddg=https%3A%2F%2Fen.wikipedia.org%2Fwiki%2FShiels_Jewellers&rut=9c52f9edd764ff35bb0b2ae838e69db18e57482c7cbc618ceb71978e04aae695`
  Snippet: `Shiels Jewellers is an Australian jewellery retailer and was founded by Jack Shiels in Adelaide in 1945. [1][2][3][4][5] Since then, Shiels has expanded to 40 stores across South Australia, Queensland, New South Wales and Western Australia, employing over 450 people.`
- URL: `//duckduckgo.com/l/?uddg=https%3A%2F%2Fwww.shiels.com.au%2Fpages%2Four%2Dstory&rut=07655a18d836f58c1ee8e5351b00723a06f3ca311094d1457d04b5774a515348`
  Snippet: `The Shiels Story With the goal of providing high quality, valuable and unique jewellery pieces, Shiels was founded in 1945 and has remained an Australian family business ever since. Originally owned by Jack and Jeanne Shiels, the business quickly earned a reputation for consistently making beautiful, unique and long-lasting jewellery pieces.`

## Case 3

Serialized triples:
`Assassin 's Creed II Roger Craig Smith character role Ezio Auditore da Firenze, Nolan North character role Desmond Miles`

Original KELM sentence:
`The framing story is set in the 21st century and follows Desmond Miles as Assassin 's Creed II relives the genetic memories of his ancestor Ezio Auditore da Firenze.`

Rewritten question:
None. Rewrite was never reached.

Outcome:
- `unsupported_relation_record`

What happened:
- The row has no relation in the current allowlist.
- `character role` is not part of the supported KELM subset, so the row stopped before grounding.

DuckDuckGo evidence:
- none, because search was never reached

## Case 4

Serialized triple:
`Cyclopites taxon rank Genus`

Original KELM sentence:
`Cyclopites is a genus of aglaspidid arthropods that lived in shallow seas in what is now Wisconsin during Late Cambrian times.`

Rewritten question:
`What taxonomic category does Cyclopites belong to, considering it is an aglaspidid arthropod that inhabited shallow seas in the area now known as Wisconsin during the Late Cambrian period?`

Outcome:
- `search_longtail_verifier_rejected`

Hit rates:
- `full_question`: `1.0`
- `keyword_queries`: `0.4`
- `overall`: `0.55`

Triggered rule:
- `keyword_query_1:answer_in_title`

What happened:
- This row passed grounding and rewrite.
- The rewritten question no longer leaked the answer string directly.
- After rerunning the row in isolation, the search verifier completed normally.
- The row was still rejected because search results exposed the answer directly in titles and snippets.

DuckDuckGo evidence:

`full_question`
- URL: `//duckduckgo.com/l/?uddg=https%3A%2F%2Fen.wikipedia.org%2Fwiki%2FCyclopites&rut=a50463dde8f3fc680508b77270bf5bfea0872fb424f018b941fc997559db1c6a`
  Snippet: `Cyclopites is a genus of aglaspidid arthropods that lived in shallow seas in what is now Wisconsin during Late Cambrian times. It is distinguished from other aglaspidids by the extreme proximity of its eyes.`
- URL: `//duckduckgo.com/l/?uddg=https%3A%2F%2Fgrokipedia.com%2Fpage%2Fcyclopites&rut=e94644dd9d3bba77187a45480e3a2dfda893399d2fc52bb27fb1870fd8b1137d`
  Snippet: `Cyclopites is an extinct genus of marine arthropods belonging to the order Aglaspidida, known from the Upper Cambrian (Furongian, Jiangshanian Stage) period approximately 497-485 million years ago. It is classified within the family Tremaglaspididae and the monophyletic clade Vicissicaudata, part of the larger subphylum Artiopoda, which encompasses various non-trilobite arthropods with ...`

`keyword_query_1`: `"Cyclopites" taxonomic classification`
- URL: `//duckduckgo.com/l/?uddg=https%3A%2F%2Fen.wikipedia.org%2Fwiki%2FCyclopites&rut=a50463dde8f3fc680508b77270bf5bfea0872fb424f018b941fc997559db1c6a`
  Snippet: `Cyclopites is a genus of aglaspidid arthropods that lived in shallow seas in what is now Wisconsin during Late Cambrian times. It is distinguished from other aglaspidids by the extreme proximity of its eyes.`
- URL: `//duckduckgo.com/l/?uddg=http%3A%2F%2Ftaxonomicon.taxonomy.nl%2FTaxonPositions.aspx%3Fid%3D1307390%26src%3D0&rut=fa525f26132327ec016c066678e5489a98675cbc07c8041d4b3ac5d7308221aa`
  Snippet: `Taxonomic positions and number of subtaxa of Genus 鈥燙yclopites Raasch, 1939`

`keyword_query_2`: `aglaspidid arthropods from Late Cambrian Wisconsin`
- URL: `//duckduckgo.com/l/?uddg=https%3A%2F%2Fwww.jstor.org%2Fstable%2F1305947&rut=d3a888478c0f604d2df0dc10c2c50ec013a0f3867a01eb75932c3c35f7c44c57`
  Snippet: `ABSTRACT-New specimens of aglaspidid arthropods, mainly from the Upper Cambrian St. Lawrence (Upper Dikelocephalus Zone), show that appendages previously assigned to the genotype Aglaspis new genus and species Flobertia kochi. Chraspedops fragilis is transferred to a new genus Tuboculops. Aglaspis dorsetensis and Aglaspis franconensis is queried.`
- URL: `//duckduckgo.com/l/?uddg=https%3A%2F%2Fwww.cambridge.org%2Fcore%2Fjournals%2Fjournal%2Dof%2Dpaleontology%2Farticle%2Fabs%2Faglaspidida%2Darthropoda%2Dfrom%2Dthe%2Dupper%2Dcambrian%2Dof%2Dwisconsin%2F8E49E625EB1777F5EE6DB1EB372994B7&rut=9925da635987b1c716247330c703eee66dc3459fd10646ed6d59fd2f25314168`
  Snippet: `Abstract New specimens of aglaspidid arthropods, mainly from the Upper Cambrian St. Lawrence Formation of Wisconsin (Upper Dikelocephalus Zone), show that appendages previously assigned to the genotype Aglaspis barrandei actually belong to a new genus and species Flobertia kochi. Chraspedops fragilis is transferred to a new genus Tuboculops.`

`keyword_query_3`: `classification of arthropods in Late Cambrian shallow seas`
- URL: `//duckduckgo.com/l/?uddg=https%3A%2F%2Fen.wikipedia.org%2Fwiki%2FList_of_Cambrian_arthropods&rut=597e1ae9e2a0c09e58a0835897b90e33f889bf8a7f0a4be4c907af4d75eabd0f`
  Snippet: `This list contains many extinct arthropod [1] genera from the Cambrian Period of the Paleozoic Era. Some trilobites, bradoriids and phosphatocopines may not be included due to the lack of literature on these clades and inaccessibility of many papers describing their genera. This list also provides references for any Wikipedia users who intend to create pages for more obscure taxa.`
- URL: `//duckduckgo.com/l/?uddg=https%3A%2F%2Fwww.palaeontologyonline.com%2F%3Fp%3D3523&rut=46a17b23a5e93392c10ebfe87d6fa8b0d5e9d8a83d704888eb3e2cef3152cc87`
  Snippet: `Agnostus pisiformis: The agnostids 鈥?an arthropod order found from the early Cambrian period to the late Ordovician, which peaked in diversity during the middle Cambrian 鈥?have long been considered a highly unusual group of trilobites.`

## Case 5

Serialized triples:
`Confessions from the David Galaxy Affair instance of Film`

Original KELM sentence:
`Confessions from the David Galaxy Affair is a 1979 comedy film starring Alan Lake and Anthony Booth.`

Rewritten question:
None. Rewrite was never reached.

Outcome:
- `unsupported_relation_record`

What happened:
- `instance of` is not in the current supported KELM subset.

DuckDuckGo evidence:
- none, because search was never reached

## Case 6

Serialized triples:
`The Planets ( 1999 TV series ) publication date 01 January 1999, narrator Samuel West`

Original KELM sentence:
`The series featured appearances from famous pioneering space scientists and explorers, and was narrated by Samuel West in the original 1999 edition, and Mark Halliley in the 2004 remastered edition.`

Selected supported triple:
`The Planets ( 1999 TV series )` -> `narrator` -> `Samuel West`

Rewritten question:
None. Rewrite was never reached.

Outcome:
- `entity_grounding_failed`

What happened:
- `narrator` is supported, so this is not a relation-coverage failure.
- The row stopped during grounding, before rewrite.
- The likely issue is that the subject form in the triple is awkwardly normalized and the sentence text does not repeat the full title, so the conservative exact-match resolver did not get enough signal.

DuckDuckGo evidence:
- none, because search was never reached

## Case 7

Serialized triples:
`Manny Diaz ( California politician ) occupation Politician, position held member of the California State Assembly, date of birth 04 July 1953`

Original KELM sentence:
`Manolo J. Diaz (born July 4, 1953 in San Francisco, California) is an American engineer and politician who served as a member of the California State Assembly from 2000 to 2004, representing the 23rd District.`

Selected supported triple:
`Manny Diaz ( California politician )` -> `date of birth` -> `04 July 1953`

Rewritten question:
None. Rewrite was never reached.

Outcome:
- `entity_grounding_failed`

What happened:
- `date of birth` is supported, so this is not a relation-coverage failure.
- The triple uses `Manny Diaz`, while the sentence uses `Manolo J. Diaz`.
- Under the current conservative resolver, that alias mismatch is enough to stop the row before rewrite.

DuckDuckGo evidence:
- none, because search was never reached

## Case 8

Serialized triples:
`Battle Magic ( novel ) genre Novel, follows Street Magic`

Original KELM sentence:
`Battle Magic is a fantasy novel by Tamora Pierce in the Emelan universe and follows Street Magic.`

Rewritten question:
None. Rewrite was never reached.

Outcome:
- `unsupported_relation_record`

What happened:
- The row does not contain a currently supported relation.
- `genre` and `follows` are not in the current KELM allowlist.

DuckDuckGo evidence:
- none, because search was never reached

## Case 9

Serialized triples:
`Ty Cobb ( attorney ) occupation Lawyer`

Original KELM sentence:
`Ty Cobb is an American attorney and former Special Counsel to the President.`

Rewritten question:
None. Rewrite was never reached.

Outcome:
- `unsupported_relation_record`

What happened:
- `occupation` is not in the current supported KELM subset.

DuckDuckGo evidence:
- none, because search was never reached

## Case 10

Serialized triple:
`Peter Kelland educated at University of Cambridge`

Original KELM sentence:
`After two years in the Marines Peter Kelland began his studies at the University of Cambridge.`

Rewritten question:
`Where did Peter Kelland begin his studies after serving two years in the Marines?`

LLM keyword queries:
- `"Peter Kelland" education after Marines`
- `Peter Kelland university studies post Marines`
- `Peter Kelland academic background following military service`
- `Peter Kelland studies after two years in Marines`

Outcome:
- `search_longtail_verifier_rejected`

Hit rates:
- `full_question`: `1.0`
- `keyword_queries`: `0.65`
- `overall`: `0.72`

Triggered rule:
- `full_question:hit_rate_exceeded`

DuckDuckGo evidence:

`full_question`
- URL: `//duckduckgo.com/l/?uddg=https%3A%2F%2Fen.wikipedia.org%2Fwiki%2FPeter_Kelland&rut=7a45ab494a5d8a986937be5bb340706532069f9d89d93f781b771c522b3df8bc`
  Snippet: `After leaving Repton, he spent two years in the Royal Marines. [1] After two years in the Marines he began his studies at the University of Cambridge. [1] He made his first-class debut for Cambridge University Cricket Club against Sussex at Fenner's in 1949.`
- URL: `//duckduckgo.com/l/?uddg=https%3A%2F%2Fmilitary%2Dhistory.fandom.com%2Fwiki%2FPeter_Kelland&rut=6a519f554c5d1ed8deec184c10f4ee985ae445ba31318f87af4a055d164a138c`
  Snippet: `After two years in the Marines he began his studies at the University of Cambridge. [1] He made his first-class debut for Cambridge University Cricket Club against Sussex at Fenner's in 1949.`

`keyword_query_1`: `"Peter Kelland" education after Marines`
- URL: `//duckduckgo.com/l/?uddg=https%3A%2F%2Fen.wikipedia.org%2Fwiki%2FPeter_Kelland&rut=7a45ab494a5d8a986937be5bb340706532069f9d89d93f781b771c522b3df8bc`
  Snippet: `After leaving Repton, he spent two years in the Royal Marines. [1] After two years in the Marines he began his studies at the University of Cambridge. [1] He made his first-class debut for Cambridge University Cricket Club against Sussex at Fenner's in 1949.`
- URL: `//duckduckgo.com/l/?uddg=https%3A%2F%2Fdbpedia.org%2Fpage%2FPeter_Kelland&rut=a27fcb18ba0ad6c17df955e7023c7f03e7f08de3a85d9e1e49458886a62aef31`
  Snippet: `Peter Alban Kelland (20 September 1926 - 24 October 2011) was an English cricketer. Kelland was a right-handed batsman who bowled right-arm fast-medium. He was born at Pinner, Middlesex, to Parents Rev Alban Joseph Kelland and Stella Prynne.`

`keyword_query_2`: `Peter Kelland university studies post Marines`
- URL: `//duckduckgo.com/l/?uddg=https%3A%2F%2Fen.wikipedia.org%2Fwiki%2FPeter_Kelland&rut=7a45ab494a5d8a986937be5bb340706532069f9d89d93f781b771c522b3df8bc`
  Snippet: `After leaving Repton, he spent two years in the Royal Marines. [1] After two years in the Marines he began his studies at the University of Cambridge. [1] He made his first-class debut for Cambridge University Cricket Club against Sussex at Fenner's in 1949.`
- URL: `//duckduckgo.com/l/?uddg=https%3A%2F%2Fmilitary%2Dhistory.fandom.com%2Fwiki%2FPeter_Kelland&rut=6a519f554c5d1ed8deec184c10f4ee985ae445ba31318f87af4a055d164a138c`
  Snippet: `After leaving Repton, he spent two years in the Royal Marines. [1] After two years in the Marines he began his studies at the University of Cambridge. [1] He made his first-class debut for Cambridge University Cricket Club against Sussex at Fenner's in 1949.`

`keyword_query_3`: `Peter Kelland academic background following military service`
- URL: `//duckduckgo.com/l/?uddg=https%3A%2F%2Fen.wikipedia.org%2Fwiki%2FPeter_Kelland&rut=7a45ab494a5d8a986937be5bb340706532069f9d89d93f781b771c522b3df8bc`
  Snippet: `Peter Alban Kelland (20 September 1926 - 24 October 2011) was an English cricketer. Kelland was a right-handed batsman who bowled right-arm fast-medium. He was born at Pinner, Middlesex, to Parents Rev Alban Joseph Kelland and Stella Prynne. Kelland was educated at Repton School during World War II, where he was Head of his House and played in the school cricket team. Alongside Donald Carr ...`
- URL: `//duckduckgo.com/l/?uddg=https%3A%2F%2Fmilitary%2Dhistory.fandom.com%2Fwiki%2FPeter_Kelland&rut=6a519f554c5d1ed8deec184c10f4ee985ae445ba31318f87af4a055d164a138c`
  Snippet: `Peter Alban Kelland (20 September 1926 - 24 October 2011) was an English cricketer. Kelland was a right-handed batsman who bowled right-arm fast-medium. He was born at Pinner, Middlesex, to Parents Rev Alban Joseph Kelland and Stella Prynne. Kelland was educated at Repton School during World War II, where he was Head of his House and played in the school cricket team. Alongside Donald Carr ...`

`keyword_query_4`: `Peter Kelland studies after two years in Marines`
- URL: `//duckduckgo.com/l/?uddg=https%3A%2F%2Fen.wikipedia.org%2Fwiki%2FPeter_Kelland&rut=7a45ab494a5d8a986937be5bb340706532069f9d89d93f781b771c522b3df8bc`
  Snippet: `After leaving Repton, he spent two years in the Royal Marines. [1] After two years in the Marines he began his studies at the University of Cambridge. [1] He made his first-class debut for Cambridge University Cricket Club against Sussex at Fenner's in 1949.`
- URL: `//duckduckgo.com/l/?uddg=https%3A%2F%2Fmilitary%2Dhistory.fandom.com%2Fwiki%2FPeter_Kelland&rut=6a519f554c5d1ed8deec184c10f4ee985ae445ba31318f87af4a055d164a138c`
  Snippet: `After two years in the Marines he began his studies at the University of Cambridge. [1] He made his first-class debut for Cambridge University Cricket Club against Sussex at Fenner's in 1949.`

## Notes

- This walkthrough uses the recorded DuckDuckGo redirect URLs exactly as they appear in the output artifacts.
- For full raw result lists, use [outputs/kelm_half_pipeline_rejected.jsonl](D:/Study/AI/My-research/Wikidata_Framework/outputs/kelm_half_pipeline_rejected.jsonl).
- Cases 1, 6, and 7 are the clearest examples that `entity_grounding_failed` is a better label than the older combined reject bucket.
- Case 4 shows that live search transport can still fail even after rewrite succeeds.
