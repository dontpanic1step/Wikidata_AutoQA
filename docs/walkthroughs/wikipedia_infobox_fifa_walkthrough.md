# Wikipedia Infobox/Table Route Walkthrough: 2026 FIFA World Cup

Run date: 2026-05-16

## Command

The live run used the OpenRouter key from `OPENROUTER_API_KEY`; the secret is intentionally not recorded here.

```powershell
python scripts\run_wikipedia_infobox_pipeline.py --url https://en.wikipedia.org/wiki/2026_FIFA_World_Cup --record-limit 1 --target-time 2024 --cutoff-year 2025 --proxy none --enable-second-stage-grading --second-stage-grading-accuracy-threshold 1 --search-longtail-max-full-question-hit-rate 1 --search-longtail-max-keyword-hit-rate 1 --search-longtail-max-overall-hit-rate 1 --output outputs\wikipedia_infobox_fifa_accepted.jsonl --rejected-output outputs\wikipedia_infobox_fifa_rejected.jsonl --summary-output outputs\wikipedia_infobox_fifa_summary.json
```

## Result

- Accepted: 1
- Rejected: 0
- Question: Which tournament venue has the highest seating capacity for the 23rd FIFA World Cup?
- Answer: AT&T Stadium
- Answer aliases: Dallas Stadium
- Generation route: `route3_wikipedia_infobox`
- Source URL: https://en.wikipedia.org/wiki/2026_FIFA_World_Cup
- Selected source table: table 3 / List of tournament venues
- Derivation summary: Selected the venue with the maximum seating capacity from the 'List of tournament venues' table, identifying AT&T Stadium as having the highest capacity of 94,000.

## Table Selection Criteria

The route ranks tables before prompting the small model. The intended criteria are:

- Prefer article `wikitable` tables over summary infoboxes.
- Prefer tables with multiple structured rows and usable headers.
- Prefer tables with numeric, ordinal, date, rank, count, vote, total, or comparable value columns.
- Prefer row values that are not easily recoverable from non-table prose.
- Penalize placeholder or mutable tables such as future standings, match schedules, and qualification tables.
- Penalize zero-dominant numeric tables and large text-heavy tables.

## Table Ranking From This Run

| Rank | Table | Section | Caption | Score | Reasons | Prose leakage |
| --- | --- | --- | --- | ---: | --- | --- |
| 1 | 3 (wikitable) | Venues | List of tournament venues | 9.9 | article_table, multi_row, has_headers, numeric_values, comparable_headers, preferred_table_context, high_prose_leakage | 32/48 (0.6667) |
| 2 | 2 (wikitable) | Voting | Voting results | 7.65 | article_table, multi_row, has_headers, numeric_values, comparable_headers | 2/7 (0.2857) |
| 3 | 5 (wikitable) | Team base camps | List of team base camps | 5.8 | article_table, multi_row, has_headers, no_comparable_headers, low_prose_leakage | 0/144 (0.0) |
| 4 | 25 (wikitable) | Prize money | Performance-based prize money based on final position | 5.5 | article_table, multi_row, has_headers, numeric_values, no_comparable_headers | 5/11 (0.4545) |
| 5 | 6 (wikitable) | Match schedule | Schedule by round | 4.35 | article_table, multi_row, has_headers, comparable_headers, mutable_or_placeholder_context | 10/20 (0.5) |
| 6 | 24 (wikitable) | Domestic sponsors |  | 3.05 | article_table, multi_row, has_headers, no_comparable_headers | 9/18 (0.5) |
| 7 | 4 (wikitable) | Draw | Pots [ N ] | 3.0 | article_table, too_few_rows, has_headers, no_comparable_headers, low_prose_leakage | 0/0 (0.0) |
| 8 | 22 (wikitable) | Sponsorships |  | 3.0 | article_table, too_few_rows, has_headers, no_comparable_headers, low_prose_leakage | 0/0 (0.0) |

## Stage 1: DuckDuckGo Search Filtering

- Passed: True
- Triggered rule: ``
- Top K: 10
- Thresholds: `{"full_question": 1.0, "keyword_queries": 1.0, "overall": 1.0}`

### Hit Rates

| Category | Query count | Results | Answer-hit results | Title-hit results | Snippet-hit results | Answer hit rate |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| full_question | 1 | 10 | 1 | 0 | 1 | 0.1 |
| keyword_queries | 4 | 40 | 4 | 0 | 4 | 0.1 |
| answer_probe | 0 | 0 | 0 | 0 | 0 | 0.0 |
| overall | 5 | 50 | 5 | 0 | 5 | 0.1 |

### Search Queries Used After Answer Sanitization

- 2026 FIFA World Cup tournament venues capacity
- largest stadium by capacity 2026 FIFA World Cup
- 23rd FIFA World Cup venue capacities
- FIFA World Cup 2026 stadiums list

The route drops model-generated queries that contain the canonical answer or answer aliases before DuckDuckGo verification.

### URLs, Snippets, And Hits

### Query: `full_question`

- Category: `full_question`
- Query text: Which tournament venue has the highest seating capacity for the 23rd FIFA World Cup?
- Result count: 10
- Answer-hit results: 1
- Hit rate: 0.1000
- Title hits: 0
- Snippet hits: 1
- Exact question hit: False

| # | Answer hit | URL | Title | Snippet |
| ---: | --- | --- | --- | --- |
| 1 | False | //duckduckgo.com/l/?uddg=https%3A%2F%2Fwww.soccergraph.com%2F2026%2F04%2Ffifa%2Dworld%2Dcup%2D2026%2Dstadiums%2Dranked%2Dby%2Dcapcity%2Dfull%2Dlist.html&rut=7e14b910ba66c1b95343216f103e342361058d09f0970d79f0669e785c0a6c09 | FIFA World Cup 2026 Stadiums Ranked by Capacity Full List | FIFA World Cup 2026: Stadiums Ranked by Capacity The 2026 FIFA World Cup, co-hosted by the United States, Canada, and Mexico, will be the largest edition in history with 48 teams and matches spread across 16 venues. FIFA has released official stadium capacities (net seating for the tournament, which may be adjusted slightly due to configuration for soccer-specific needs, such as pitch size and ... |
| 2 | False | //duckduckgo.com/l/?uddg=https%3A%2F%2Fwww.thebiglead.com%2F2026%2Dfifa%2Dworld%2Dcup%2Dstadiums%2Dranked%2Dby%2Dmaximum%2Dcapacity%2F&rut=9a2318cf86dd35df9214fffc47e0959d8feb768a7e750dbeb90267648e8d6aa5 | 2026 FIFA World Cup stadiums ranked by maximum capacity | The 2026 FIFA World Cup will be played across 16 stadiums in the United States, Mexico, and Canada, ranked by capacity from MetLife Stadium (78,576) down to BMO Field in Toronto (44,315 ... |
| 3 | True | //duckduckgo.com/l/?uddg=https%3A%2F%2Flegionreport.com%2Fworld%2Dcup%2D2026%2Dstadiums%2F&rut=1fed5f0778aab87809b32603732223fde7705bad036f7ebef2e7710c1cad3b8f | World Cup 2026 Stadiums Ranked: Capacity And More | The 2026 FIFA World Cup runs June 11 to July 19, 2026, across 16 stadiums in three countries — the first World Cup hosted by three nations and the first with 48 teams. The United States hosts 78 of the 104 matches (every game from the quarterfinals on plays on American soil), with Canada hosting 13 and Mexico 13. AT&T Stadium in Dallas is the biggest venue at nearly 93,000 seats, while BMO ... |
| 4 | False | //duckduckgo.com/l/?uddg=https%3A%2F%2Fworldsoccertalk.com%2Fworld%2Dcup%2Fworld%2Dcup%2D2026%2Dstadiums%2Dhost%2Dcities%2Dvenues%2Dand%2Dcapacities%2F&rut=679d8e4fa968ec278a59153c33fbbcd08ae75d0a67c0cc9f060d26fe346a2e46 | World Cup 2026 stadiums: Host cities, venues, and capacities | The 2026 FIFA World Cup will feature several innovations compared to previous editions. Not only will there be a new expanded format with 48 teams, but it will also be the first World Cup hosted by three different countries. That has increased the number of venues to a total of 16. The United States are the tournament's main host nation, meaning most of the matches will be played on U.S ... |
| 5 | False | //duckduckgo.com/l/?uddg=https%3A%2F%2Fwww.fifa.com%2Fen%2Ftournaments%2Fmens%2Fworldcup%2Fcanadamexicousa2026%2Farticles%2Fstadium%2Dinformation%2Ddetails&rut=6ea1f32ad397d1ae837b9161c5d9b00dd5c8ed183508b7ccb71bf5dbcf1a1bdf | Stadium Information - Fifa | Learn more about the different FIFA World Cup 2026™ stadium names, locations and seating capacities. Here are the relevant details for the FIFA World Cup 2026™ stadiums in Canada: BC Place ... |
| 6 | False | //duckduckgo.com/l/?uddg=https%3A%2F%2Fwww.stadiumport.com%2Fworld%2Dcup%2D2026%2Dstadiums&rut=9636d52abaa0b735848233b3a9ce6a2daec5e336892110012ec1e98ca50bf2bc | World Cup 2026 Stadiums Guide: All 16 Venues & Seating | Complete guide to all 16 World Cup 2026 stadiums. Seating charts, capacity, tickets & accessibility for USA, Mexico & Canada venues. |
| 7 | False | //duckduckgo.com/l/?uddg=https%3A%2F%2Fthesoccerera.com%2Ffifa%2Dworld%2Dcup%2D2026%2Dstadiums%2Dhost%2Dcities%2F&rut=ef44d439ee0d5d50c95c7a0ff4fe5f9e9d5220c1132ea936d3adcf6a24ed2106 | FIFA World Cup 2026 Stadiums: Full List of 16 Host Cities & Capacity | Get the full list of FIFA World Cup 2026 Stadiums across the USA, Canada, and Mexico. Explore host cities, venue capacities, and final match details. Read more! |
| 8 | False | //duckduckgo.com/l/?uddg=https%3A%2F%2Foffsidetalk.com%2F2026%2Dworld%2Dcup%2Dstadiums%2F&rut=5c64fa4247a96c19d5d639af61b408635d11db2697849464225308fae4fbb831 | 2026 World Cup Stadiums: Capacity, Location & Key Facts | Explore all 16 stadiums for the 2026 World Cup. Get capacity, city locations, and what makes each venue special for the historic tournament. |
| 9 | False | //duckduckgo.com/l/?uddg=https%3A%2F%2Fsportsbrackets.net%2F2025%2F12%2F08%2F2026%2Dfifa%2Dworld%2Dcup%2Dhost%2Dcities%2Dstadiums%2Dthe%2D16%2Dvenues%2Dyou%2Dneed%2Dto%2Dknow%2F&rut=b8ec729411e2cddb98af17ce4af3c5600fff8820b32ba09cd9c30279757f0d2a | 2026 FIFA World Cup Host Cities & Stadiums: The 16 Venues You Need to ... | We have the 2026 FIFA World Cup host cities Below: Every stadium with capacity, quick facts, and must-knows for fans planning trips. (All capacities per FIFA) 2026 FIFA WOrld Cup Host Cities & Stadiums Here's the 2026 FIFA World Cup Host cities and stadiums for you. All of the stadiums, seating capacity, and more. |
| 10 | False | //duckduckgo.com/l/?uddg=https%3A%2F%2Fwww.tickpick.com%2Fblog%2F2026%2Dworld%2Dcup%2Dseating%2Dguide%2Dall%2D16%2Dvenues%2Dbest%2Dand%2Dworst%2Dseats%2F&rut=c66784e8ac204837bc7b484f7e94292f995db02e955d1a252f4d7985175f159d | 2026 World Cup Seating Guide: Complete Venue Breakdown for All 16 ... | The 2026 FIFA World Cup will make history as the largest World Cup ever, featuring 48 teams and 104 matches across 16 spectacular venues in the United States, Canada, and Mexico. Understanding stadium seating categories, pricing, and sightlines is crucial to planning your World Cup experience. This comprehensive guide breaks down seating information for every ... <a title="2026 World Cup ... |
### Query: `keyword_query_1`

- Category: `keyword_queries`
- Query text: 2026 FIFA World Cup tournament venues capacity
- Result count: 10
- Answer-hit results: 0
- Hit rate: 0.0000
- Title hits: 0
- Snippet hits: 0
- Exact question hit: False

| # | Answer hit | URL | Title | Snippet |
| ---: | --- | --- | --- | --- |
| 1 | False | //duckduckgo.com/l/?uddg=https%3A%2F%2Fworldcupwiki.com%2Fstadiums%2F&rut=b69fa0635126ecbda9800d1b68aa8529783459e723fac684b2a41bc942a4368b | 2026 FIFA World Cup Stadiums: Complete Guide to All 16 Venues | 2026 FIFA World Cup Stadiums: Complete Guide to All 16 Venues The 2026 FIFA World Cup is the largest football tournament ever staged. Three nations co-host for the first time: the United States, Mexico, and Canada. A total of 48 teams will play 104 matches across 16 stadiums from June 11 to July 19, 2026. |
| 2 | False | //duckduckgo.com/l/?uddg=https%3A%2F%2Fworldsoccertalk.com%2Fworld%2Dcup%2Fworld%2Dcup%2D2026%2Dstadiums%2Dhost%2Dcities%2Dvenues%2Dand%2Dcapacities%2F&rut=679d8e4fa968ec278a59153c33fbbcd08ae75d0a67c0cc9f060d26fe346a2e46 | World Cup 2026 stadiums: Host cities, venues, and capacities | The 2026 FIFA World Cup will feature several innovations compared to previous editions. Not only will there be a new expanded format with 48 teams, but it will also be the first World Cup hosted by three different countries. That has increased the number of venues to a total of 16. The United States are the tournament's main host nation, meaning most of the matches will be played on U.S ... |
| 3 | False | //duckduckgo.com/l/?uddg=https%3A%2F%2Fwww.fifaworldcupnews.com%2Ffifa%2Dworld%2Dcup%2D2026%2Dstadiums%2Dvenues%2Dhost%2Dcities%2F&rut=9451e511fae7123cee1082fcacf128c95c1bd5b7e6574c5a3b27a1c1566440e7 | FIFA World Cup 2026 Stadiums: Full List of 16 Venues, Capacity & Map | Planning for 2026? Check the complete FIFA World Cup 2026 stadiums list. From MetLife to SoFi, get official venue capacities, host cities, and match schedules. |
| 4 | False | //duckduckgo.com/l/?uddg=https%3A%2F%2Fwww.fifa.com%2Fen%2Ftournaments%2Fmens%2Fworldcup%2Fcanadamexicousa2026%2Farticles%2Fworld%2Dcup%2D2026%2Dstadiums%2Dfifa%2Dsoccer%2Dfootball%2Dmexico%2Dusa%2Dcanada&rut=5a589b0ff279fc0028047ff5362a32749d4367dbefcc5ad5d03c9bc0fe63163e | FIFA World Cup 2026 stadiums in Canada, Mexico and the USA | Canada, Mexico and the USA to host tournament﻿ 16 stadiums will host FIFA World Cup 2026, the most since 2002﻿ FIFA details all you need to know about the venues |
| 5 | False | //duckduckgo.com/l/?uddg=https%3A%2F%2Fwww.stadiumport.com%2Fworld%2Dcup%2D2026%2Dstadiums&rut=9636d52abaa0b735848233b3a9ce6a2daec5e336892110012ec1e98ca50bf2bc | World Cup 2026 Stadiums Guide: All 16 Venues & Seating | Complete guide to all 16 World Cup 2026 stadiums. Seating charts, capacity, tickets & accessibility for USA, Mexico & Canada venues. |
| 6 | False | //duckduckgo.com/l/?uddg=https%3A%2F%2Fworldcuppass.com%2Fstadiums%2F&rut=65c608445d186c10ab7511f0171446ac66099f724e78d19cfb5597bafe3dd5bc | 2026 FIFA World Cup Stadiums: All 16 Venues, Cities & Capacities | See all 16 FIFA World Cup 2026 stadiums with host cities, capacities, FIFA tournament names and match counts across USA, Canada and Mexico. |
| 7 | False | //duckduckgo.com/l/?uddg=https%3A%2F%2Fwww.beinsports.com%2Fen%2Dus%2Fsoccer%2Ffifa%2Dworld%2Dcup%2D2026%2Farticles%2Fall%2D2026%2Dworld%2Dcup%2Dstadiums%2Dhost%2Dcities%2Dcapacity%2Dand%2Dmatches%2D2026%2D05%2D13&rut=ad400c41a60fae3af84307ac0061a425384c62188d7db67a497b1904156c09bc | All 2026 World Cup Stadiums: Host Cities, Capacity and Matches | Discover every stadium and host city for the 2026 World Cup, including capacity, location, and key matches across North America. |
| 8 | False | //duckduckgo.com/l/?uddg=https%3A%2F%2Ffwcmania.com%2Fvenues%2F&rut=324f7ce6c7b8a6b766715d8a7997cc31cfd2b756ac39567a601e94fcd1894e78 | World Cup 2026 Venues \| Stadiums, Capacity & Host Cities | The 2026 tournament covers 16 host cities across the United States, Mexico, and Canada. The FIFA World Cup 2026 map mixes legendary football grounds with some of the most advanced billion-dollar stadiums on the planet. But picking a stadium isn't just about the building. It's about altitude, humidity, public transport, and local football culture. |
| 9 | False | //duckduckgo.com/l/?uddg=https%3A%2F%2Fwww.thebiglead.com%2F2026%2Dfifa%2Dworld%2Dcup%2Dstadiums%2Dranked%2Dby%2Dmaximum%2Dcapacity%2F&rut=9a2318cf86dd35df9214fffc47e0959d8feb768a7e750dbeb90267648e8d6aa5 | 2026 FIFA World Cup stadiums ranked by maximum capacity | The 2026 FIFA World Cup will be played across 16 stadiums in the United States, Mexico, and Canada, ranked by capacity from MetLife Stadium (78,576) down to BMO Field in Toronto (44,315 ... |
| 10 | False | //duckduckgo.com/l/?uddg=https%3A%2F%2Fthematchjournal.com%2F2026%2F04%2F01%2Fworld%2Dcup%2D2026%2Dstadiums%2F&rut=318d4da1841daaee6d4bfbe921d7f1cf14048352027d330edce479bc1b822c3d | World Cup 2026 Stadiums: Full List of Venues, Capacity, Locations and ... | The World Cup 2026 stadiums will host matches across 16 venues in the United States, Canada, and Mexico, making it the largest and most geographically diverse tournament in FIFA history. Each stadium plays a key role in shaping the tournament experience, from capacity and location to hosting major matches like the opening game and the final. World Cup 2026 Stadiums: Full List of Venues ... |
### Query: `keyword_query_2`

- Category: `keyword_queries`
- Query text: largest stadium by capacity 2026 FIFA World Cup
- Result count: 10
- Answer-hit results: 3
- Hit rate: 0.3000
- Title hits: 0
- Snippet hits: 3
- Exact question hit: False

| # | Answer hit | URL | Title | Snippet |
| ---: | --- | --- | --- | --- |
| 1 | False | //duckduckgo.com/l/?uddg=https%3A%2F%2Fwww.soccergraph.com%2F2026%2F04%2Ffifa%2Dworld%2Dcup%2D2026%2Dstadiums%2Dranked%2Dby%2Dcapcity%2Dfull%2Dlist.html&rut=7e14b910ba66c1b95343216f103e342361058d09f0970d79f0669e785c0a6c09 | FIFA World Cup 2026 Stadiums Ranked by Capacity Full List | FIFA World Cup 2026: Stadiums Ranked by Capacity The 2026 FIFA World Cup, co-hosted by the United States, Canada, and Mexico, will be the largest edition in history with 48 teams and matches spread across 16 venues. FIFA has released official stadium capacities (net seating for the tournament, which may be adjusted slightly due to configuration for soccer-specific needs, such as pitch size and ... |
| 2 | False | //duckduckgo.com/l/?uddg=https%3A%2F%2Fworldcupwiki.com%2Fstadiums%2F&rut=b69fa0635126ecbda9800d1b68aa8529783459e723fac684b2a41bc942a4368b | 2026 FIFA World Cup Stadiums: Complete Guide to All 16 Venues | The 2026 FIFA World Cup is the largest football tournament ever staged. Three nations co-host for the first time: the United States, Mexico, and Canada. A total of 48 teams will play 104 matches across 16 stadiums from June 11 to July 19, 2026. This guide covers every venue with its official FIFA tournament name, capacity, full match schedule, and renovation status. All match data is verified ... |
| 3 | True | //duckduckgo.com/l/?uddg=https%3A%2F%2Fworldsoccertalk.com%2Fworld%2Dcup%2Fworld%2Dcup%2D2026%2Dstadiums%2Dhost%2Dcities%2Dvenues%2Dand%2Dcapacities%2F&rut=679d8e4fa968ec278a59153c33fbbcd08ae75d0a67c0cc9f060d26fe346a2e46 | World Cup 2026 stadiums: Host cities, venues, and capacities | The largest stadium at the World Cup will be AT&T Stadium in Dallas, which has a capacity of 94,000 spectators. Behind it is Estadio Azteca in Mexico, which was completely renovated for the tournament and, with a capacity of 83,000, will become the first stadium to host three different World Cups after previously doing so in 1970 and 1986. |
| 4 | False | //duckduckgo.com/l/?uddg=https%3A%2F%2Fwww.thebiglead.com%2F2026%2Dfifa%2Dworld%2Dcup%2Dstadiums%2Dranked%2Dby%2Dmaximum%2Dcapacity%2F&rut=9a2318cf86dd35df9214fffc47e0959d8feb768a7e750dbeb90267648e8d6aa5 | 2026 FIFA World Cup stadiums ranked by maximum capacity | The 2026 FIFA World Cup will be played across 16 stadiums in the United States, Mexico, and Canada, ranked by capacity from MetLife Stadium (78,576) down to BMO Field in Toronto (44,315 ... |
| 5 | False | //duckduckgo.com/l/?uddg=https%3A%2F%2Fnomequieroirdeaqui.com%2Fen%2Fworld%2Dcup%2D2026%2Dstadium%2Dguide%2Dall%2Dvenues%2F&rut=8fedd4877861fed9efffb073268bb9dd4a6621f0c7cc61cea03cc0aa1d841b5b | All 16 World Cup 2026 Stadiums: Capacity, Location & Matches \| NMQIDA | Complete guide to all 16 FIFA World Cup 2026 venues across USA, Mexico, and Canada. Capacity data, match assignments, and city info. |
| 6 | False | //duckduckgo.com/l/?uddg=https%3A%2F%2Fworldcuppass.com%2Fstadiums%2F&rut=65c608445d186c10ab7511f0171446ac66099f724e78d19cfb5597bafe3dd5bc | 2026 FIFA World Cup Stadiums: All 16 Venues, Cities & Capacities | See all 16 FIFA World Cup 2026 stadiums with host cities, capacities, FIFA tournament names and match counts across USA, Canada and Mexico. |
| 7 | False | //duckduckgo.com/l/?uddg=https%3A%2F%2Fwww.fifaworldcupnews.com%2Ffifa%2Dworld%2Dcup%2D2026%2Dstadiums%2Dvenues%2Dhost%2Dcities%2F&rut=9451e511fae7123cee1082fcacf128c95c1bd5b7e6574c5a3b27a1c1566440e7 | FIFA World Cup 2026 Stadiums: Full List of 16 Venues, Capacity & Map | Planning for 2026? Check the complete FIFA World Cup 2026 stadiums list. From MetLife to SoFi, get official venue capacities, host cities, and match schedules. |
| 8 | True | //duckduckgo.com/l/?uddg=https%3A%2F%2Flegionreport.com%2Fworld%2Dcup%2D2026%2Dstadiums%2F&rut=1fed5f0778aab87809b32603732223fde7705bad036f7ebef2e7710c1cad3b8f | World Cup 2026 Stadiums Ranked: Capacity And More | The 2026 FIFA World Cup runs June 11 to July 19, 2026, across 16 stadiums in three countries — the first World Cup hosted by three nations and the first with 48 teams. The United States hosts 78 of the 104 matches (every game from the quarterfinals on plays on American soil), with Canada hosting 13 and Mexico 13. AT&T Stadium in Dallas is the biggest venue at nearly 93,000 seats, while BMO ... |
| 9 | True | //duckduckgo.com/l/?uddg=https%3A%2F%2Fwww.futbolupdate.com%2Ffifa%2Dworld%2Dcup%2D2026%2Dstadiums%2F&rut=5d11efcffb42246ae39850559841c55347e4d0e9143637e42504aec5150f4b5f | 2026 FIFA World Cup Stadiums \| USA, Mexico & Canada | The largest stadium by capacity that will be used in the 2026 FIFA World Cup is the AT&T Stadium in the Dallas area (Arlington, Texas). It has a tournament capacity of 94,000 spectators. |
| 10 | False | //duckduckgo.com/l/?uddg=https%3A%2F%2Fwww.fifa.com%2Fen%2Ftournaments%2Fmens%2Fworldcup%2Fcanadamexicousa2026%2Farticles%2Fstadium%2Dinformation%2Ddetails&rut=6ea1f32ad397d1ae837b9161c5d9b00dd5c8ed183508b7ccb71bf5dbcf1a1bdf | Stadium Information - Fifa | Learn more about the different FIFA World Cup 2026™ stadium names, locations and seating capacities. |
### Query: `keyword_query_3`

- Category: `keyword_queries`
- Query text: 23rd FIFA World Cup venue capacities
- Result count: 10
- Answer-hit results: 1
- Hit rate: 0.1000
- Title hits: 0
- Snippet hits: 1
- Exact question hit: False

| # | Answer hit | URL | Title | Snippet |
| ---: | --- | --- | --- | --- |
| 1 | False | //duckduckgo.com/l/?uddg=https%3A%2F%2Fworldcupwiki.com%2Fstadiums%2F&rut=b69fa0635126ecbda9800d1b68aa8529783459e723fac684b2a41bc942a4368b | 2026 FIFA World Cup Stadiums: Complete Guide to All 16 Venues | Guide to all 16 FIFA World Cup 2026 stadiums. Confirmed match schedules, capacity, renovation updates and tickets for USA, Mexico and Canada venues |
| 2 | False | //duckduckgo.com/l/?uddg=https%3A%2F%2Fwww.soccergraph.com%2F2026%2F04%2Ffifa%2Dworld%2Dcup%2D2026%2Dstadiums%2Dranked%2Dby%2Dcapcity%2Dfull%2Dlist.html&rut=7e14b910ba66c1b95343216f103e342361058d09f0970d79f0669e785c0a6c09 | FIFA World Cup 2026 Stadiums Ranked by Capacity Full List | FIFA World Cup 2026: Stadiums Ranked by Capacity The 2026 FIFA World Cup, co-hosted by the United States, Canada, and Mexico, will be the largest edition in history with 48 teams and matches spread across 16 venues. FIFA has released official stadium capacities (net seating for the tournament, which may be adjusted slightly due to configuration for soccer-specific needs, such as pitch size and ... |
| 3 | False | //duckduckgo.com/l/?uddg=https%3A%2F%2Fworldsoccertalk.com%2Fworld%2Dcup%2Fworld%2Dcup%2D2026%2Dstadiums%2Dhost%2Dcities%2Dvenues%2Dand%2Dcapacities%2F&rut=679d8e4fa968ec278a59153c33fbbcd08ae75d0a67c0cc9f060d26fe346a2e46 | World Cup 2026 stadiums: Host cities, venues, and capacities | The 2026 FIFA World Cup will be played across 16 different venues spread throughout the United States, Mexico and Canada. |
| 4 | False | //duckduckgo.com/l/?uddg=https%3A%2F%2Fwww.fifa.com%2Fen%2Ftournaments%2Fmens%2Fworldcup%2Fcanadamexicousa2026%2Farticles%2Fstadium%2Dinformation%2Ddetails&rut=6ea1f32ad397d1ae837b9161c5d9b00dd5c8ed183508b7ccb71bf5dbcf1a1bdf | Stadium Information - Fifa | Learn more about the different FIFA World Cup 2026™ stadium names, locations and seating capacities. |
| 5 | True | //duckduckgo.com/l/?uddg=https%3A%2F%2Flegionreport.com%2Fworld%2Dcup%2D2026%2Dstadiums%2F&rut=1fed5f0778aab87809b32603732223fde7705bad036f7ebef2e7710c1cad3b8f | World Cup 2026 Stadiums Ranked: Capacity And More | The 2026 FIFA World Cup runs June 11 to July 19, 2026, across 16 stadiums in three countries — the first World Cup hosted by three nations and the first with 48 teams. The United States hosts 78 of the 104 matches (every game from the quarterfinals on plays on American soil), with Canada hosting 13 and Mexico 13. AT&T Stadium in Dallas is the biggest venue at nearly 93,000 seats, while BMO ... |
| 6 | False | //duckduckgo.com/l/?uddg=https%3A%2F%2Fsurprisesports.com%2Ffootball%2Ffifa%2Dworld%2Dcup%2Ffifa%2Dstadium%2Dcapacity%2F&rut=00dc9dfa7187b4a9360752f8438452ac427bb69b9f2183359ca85e2ea914ded6 | FIFA 2026 Stadium Capacity: Seats, Venues, Locations - Surprise Sports | Explore FIFA World Cup 2026 stadium capacities for all 16 venues. Compare seating capacity, host cities, and key details before the tournament. |
| 7 | False | //duckduckgo.com/l/?uddg=https%3A%2F%2Ffwcmania.com%2Fvenues%2F&rut=324f7ce6c7b8a6b766715d8a7997cc31cfd2b756ac39567a601e94fcd1894e78 | World Cup 2026 Venues \| Stadiums, Capacity & Host Cities | FIFA World Cup 2026 venues — all 16 official stadiums across the USA, Mexico, and Canada. Capacity, scheduled matches, and key facts for every World Cup |
| 8 | False | //duckduckgo.com/l/?uddg=https%3A%2F%2Fwww.beinsports.com%2Fen%2Dus%2Fsoccer%2Ffifa%2Dworld%2Dcup%2D2026%2Farticles%2Fall%2D2026%2Dworld%2Dcup%2Dstadiums%2Dhost%2Dcities%2Dcapacity%2Dand%2Dmatches%2D2026%2D05%2D13&rut=ad400c41a60fae3af84307ac0061a425384c62188d7db67a497b1904156c09bc | All 2026 World Cup Stadiums: Host Cities, Capacity and Matches | Discover every stadium and host city for the 2026 World Cup, including capacity, location, and key matches across North America. |
| 9 | False | //duckduckgo.com/l/?uddg=https%3A%2F%2Fwww.thebiglead.com%2F2026%2Dfifa%2Dworld%2Dcup%2Dstadiums%2Dranked%2Dby%2Dmaximum%2Dcapacity%2F&rut=9a2318cf86dd35df9214fffc47e0959d8feb768a7e750dbeb90267648e8d6aa5 | 2026 FIFA World Cup stadiums ranked by maximum capacity | The 2026 FIFA World Cup will be played across 16 stadiums in the United States, Mexico, and Canada, ranked by capacity from MetLife Stadium (78,576) down to BMO Field in Toronto (44,315 ... |
| 10 | False | //duckduckgo.com/l/?uddg=https%3A%2F%2Fthesoccerera.com%2Ffifa%2Dworld%2Dcup%2D2026%2Dstadiums%2Dhost%2Dcities%2F&rut=ef44d439ee0d5d50c95c7a0ff4fe5f9e9d5220c1132ea936d3adcf6a24ed2106 | FIFA World Cup 2026 Stadiums: Full List of 16 Host Cities & Capacity | Get the full list of FIFA World Cup 2026 Stadiums across the USA, Canada, and Mexico. Explore host cities, venue capacities, and final match details. Read more! |
### Query: `keyword_query_4`

- Category: `keyword_queries`
- Query text: FIFA World Cup 2026 stadiums list
- Result count: 10
- Answer-hit results: 0
- Hit rate: 0.0000
- Title hits: 0
- Snippet hits: 0
- Exact question hit: False

| # | Answer hit | URL | Title | Snippet |
| ---: | --- | --- | --- | --- |
| 1 | False | //duckduckgo.com/l/?uddg=https%3A%2F%2Fwww.fifa.com%2Fen%2Ftournaments%2Fmens%2Fworldcup%2Fcanadamexicousa2026%2Farticles%2Fworld%2Dcup%2D2026%2Dstadiums%2Dfifa%2Dsoccer%2Dfootball%2Dmexico%2Dusa%2Dcanada&rut=5a589b0ff279fc0028047ff5362a32749d4367dbefcc5ad5d03c9bc0fe63163e | FIFA World Cup 2026 stadiums in Canada, Mexico and the USA | The FIFA World Cup 2026™ will take place over three countries for the very first time, with Canada, Mexico and the USA set to share hosting duties in a ground-breaking edition of sport's ... |
| 2 | False | //duckduckgo.com/l/?uddg=https%3A%2F%2Fworldcupwiki.com%2Fstadiums%2F&rut=b69fa0635126ecbda9800d1b68aa8529783459e723fac684b2a41bc942a4368b | 2026 FIFA World Cup Stadiums: Complete Guide to All 16 Venues | 2026 FIFA World Cup Stadiums: Complete Guide to All 16 Venues The 2026 FIFA World Cup is the largest football tournament ever staged. Three nations co-host for the first time: the United States, Mexico, and Canada. A total of 48 teams will play 104 matches across 16 stadiums from June 11 to July 19, 2026. |
| 3 | False | //duckduckgo.com/l/?uddg=https%3A%2F%2Ffootballblog.co.uk%2Fworld%2Dcup%2D2026%2Fstadiums%2Dhost%2Dcities%2F&rut=4b6a0b3ad9ebba31776e11f1849612c4dabe624f8d3faa8cae71ad1ad476c450 | Complete FIFA World Cup 2026 Stadiums & Host Cities Map | FIFA World Cup 2026 Host Nations As shown on the World Cup stadiums 2026 map, the tournament is being hosted across three nations: the United States, Canada, and Mexico. This is the first time in World Cup history that three countries will share hosting duties. |
| 4 | False | //duckduckgo.com/l/?uddg=https%3A%2F%2Fwww.fifaworldcupnews.com%2Ffifa%2Dworld%2Dcup%2D2026%2Dstadiums%2Dvenues%2Dhost%2Dcities%2F&rut=9451e511fae7123cee1082fcacf128c95c1bd5b7e6574c5a3b27a1c1566440e7 | FIFA World Cup 2026 Stadiums: Full List of 16 Venues, Capacity & Map | Planning for 2026? Check the complete FIFA World Cup 2026 stadiums list. From MetLife to SoFi, get official venue capacities, host cities, and match schedules. |
| 5 | False | //duckduckgo.com/l/?uddg=https%3A%2F%2Fwww.olympics.com%2Fen%2Fnews%2Ffifa%2Dworld%2Dcup%2D2026%2Dfull%2Dlist%2Dstadiums%2Dmexico%2Dcanada%2Dusa&rut=0a08831ff3bb33af342a4eb6a78f9fe0235a3763654e7f53458084378fa46c32 | FIFA World Cup 2026: Full list of stadiums for the men's event in ... | The 23rd edition of the FIFA World Cup will take place across Canada, Mexico, and the USA, including at Olympic venues. Here's the full list of the 16 stadiums hosting the world's biggest football event in 2026. |
| 6 | False | //duckduckgo.com/l/?uddg=https%3A%2F%2Fparametric%2Darchitecture.com%2F2026%2Dfifa%2Dworld%2Dcup%2Dstadiums%2D16%2Dvenues%2F&rut=bb280be6297a9996f87e5cdb9210ba4fe4eb81a6507d08563d2b899edce55234 | 2026 FIFA World Cup Stadiums: Complete List of All 16 Venues in USA ... | The 2026 FIFA World Cup will be a landmark event in football history. For the first time, the tournament will be co-hosted by three nations, the United States, Canada, and Mexico, across 16 world-class stadiums. Eleven venues in the U.S., two in Canada, and three in Mexico will stage matches from the expanded 48-team tournament, running from June 11 to July 19, 2026. Each stadium brings its ... |
| 7 | False | //duckduckgo.com/l/?uddg=https%3A%2F%2Fwww.worldcupcities.org%2Fen%2Fhost%2Dcities&rut=8ce0769f275fa506443d3aedef5507a2e96960bcebcbc1d4b0ee553e5682c8ea | List of World Cup Host Cities 2026: All 16 Cities & Stadiums Guide ... | Complete list of all 16 FIFA World Cup 2026 host cities with stadiums, capacities, and travel guides. USA (11 cities): New York, Los Angeles, Dallas, Miami, Atlanta, Seattle, San Francisco, Houston, Dallas, Kansas City, Boston. |
| 8 | False | //duckduckgo.com/l/?uddg=https%3A%2F%2Fwww.stadiumport.com%2Fworld%2Dcup%2D2026%2Dstadiums&rut=9636d52abaa0b735848233b3a9ce6a2daec5e336892110012ec1e98ca50bf2bc | World Cup 2026 Stadiums Guide: All 16 Venues & Seating | World Cup 2026 Host Stadiums The 2026 FIFA World Cup™ expands across the USA, Canada, and Mexico. Experience the architecture, atmosphere, and history of the venues defining the next era of football. |
| 9 | False | //duckduckgo.com/l/?uddg=https%3A%2F%2Ftfcstadiums.com%2Ffifa%2Dworld%2Dcup%2D2026%2Dstadium%2Dguide%2F&rut=b27264d4d0de86e4aab5f0834790a112750b99506f80f0759b6ba2e15ea0e881 | FIFA World Cup 2026 Stadium Guide \| All Venues and Cities | Complete guide to every FIFA World Cup 2026 stadium across the USA, Canada, and Mexico, including host cities, official FIFA venue names, capacities, and what to expect on matchday. |
| 10 | False | //duckduckgo.com/l/?uddg=https%3A%2F%2Fwww.sportingnews.com%2Fus%2Fsoccer%2Fnews%2Fworld%2Dcup%2D2026%2Dhost%2Dcities%2Dstadiums%2Dlist%2Dusa%2Dcanada%2Dmexico%2F64cda2ae682c2ea40099bc4d&rut=e894164113a853633c66f7c9d7d6007191a1f2b02b742d3d8cbc24ef4b8d3325 | Which cities will host World Cup 2026? List of 16 stadiums chosen by ... | The 2026 FIFA World Cup is the biggest ever edition of global soccer's flagship international tournament. An expanded format features 48 teams for the first time, up from the 32-team model that ... |

## Stage 2: Small-Model QA And Judge Results

- Enabled: True
- Model count: 2
- Correct count: 0
- Attempted count: 2
- Accuracy: 0.0
- Attempt rate: 1.0
- Accuracy threshold: 1.0
- Duration seconds: 17.5911

| Model | Small-model answer | Judge grade | Judge reason | Answer seconds | Grading seconds |
| --- | --- | --- | --- | ---: | ---: |
| openai/gpt-4.1-mini | The Lusail Iconic Stadium in Lusail, Qatar, has the highest seating capacity for the 23rd FIFA World Cup, with a capacity of around 80,000 spectators. | INCORRECT | The predicted answer 'Lusail Iconic Stadium' is incorrect; the reference and source table indicate 'AT&T Stadium' (Dallas Stadium) has the highest seating capacity of 94,000 for the 23rd FIFA World Cup. | 2.6316 | 6.6244 |
| google/gemini-3-flash-preview | The **Estadio Azteca** in Mexico City has the highest seating capacity for the 2026 FIFA World Cup, with a capacity of approximately **87,523**. | INCORRECT | The predicted answer names Estadio Azteca as the venue with the highest seating capacity, but the reference answer and source table indicate that AT&T Stadium has the highest capacity (94,000), which is greater than Estadio Azteca's 83,000. | 2.3014 | 6.0334 |

Second-stage summary:

```json
{
  "run_count": 1,
  "per_model": {
    "openai/gpt-4.1-mini": {
      "runs": 1,
      "correct": 0,
      "incorrect": 1,
      "not_attempted": 0,
      "accuracy": 0.0
    },
    "google/gemini-3-flash-preview": {
      "runs": 1,
      "correct": 0,
      "incorrect": 1,
      "not_attempted": 0,
      "accuracy": 0.0
    }
  }
}
```

## Model Response

```json
{
  "question": "Which tournament venue has the highest seating capacity for the 23rd FIFA World Cup?",
  "answer": "AT&T Stadium",
  "answer_aliases": [
    "Dallas Stadium"
  ],
  "search_queries": [
    "2026 FIFA World Cup tournament venues capacity",
    "largest stadium by capacity 2026 FIFA World Cup",
    "23rd FIFA World Cup venue capacities",
    "AT&T Stadium seating capacity",
    "FIFA World Cup 2026 stadiums list"
  ],
  "composition_type": "max",
  "source_table": 3,
  "derivation_summary": "Selected the venue with the maximum seating capacity from the 'List of tournament venues' table, identifying AT&T Stadium as having the highest capacity of 94,000.",
  "discard_reason": null
}
```

## Phase Timings

Candidate metadata timings:

```json
{
  "page_fetch_seconds": 0.0087,
  "first_paragraph_fetch_seconds": 0.0005,
  "table_parse_seconds": 0.8023,
  "llm_question_generation_seconds": 4.221,
  "total_generation_seconds": 5.1309,
  "rewrite_seconds": 0.0,
  "number_reference_margin_seconds": 0.0,
  "duckduckgo_search_seconds": 7.5583,
  "second_stage_grading_seconds": 17.5911,
  "total_processing_seconds": 25.1511,
  "candidate_processing_seconds": 25.1511
}
```

Summary aggregate timings:

```json
{
  "page_fetch_seconds": 0.0087,
  "first_paragraph_fetch_seconds": 0.0005,
  "table_parse_seconds": 0.8023,
  "llm_question_generation_seconds": 4.221,
  "total_generation_seconds": 5.1309,
  "rewrite_seconds": 0.0,
  "number_reference_margin_seconds": 0.0,
  "duckduckgo_search_seconds": 7.5583,
  "second_stage_grading_seconds": 17.5911,
  "total_processing_seconds": 25.1511,
  "candidate_processing_seconds": 25.1511
}
```

## Exact Small-Model Prompt

```text
Generate one SimpleQA-style factual question from a Wikipedia infobox or table.
Return JSON only.

Requirements:
- Use a composition operation over table rows or values: max, min, sum, count, comparison, or ordinal.
- The answer must be exactly one stable entity or value from the provided table content.
- If a table cell has a parenthetical alias, put the plain entity name in answer and the parenthetical text in answer_aliases.
- Choose from the ranked tables. Prefer rank 1 unless it cannot support a safe question.
- Do not choose an infobox when a higher-ranked article table supports a composition question.
- Prefer table facts that are not easily found in article prose outside tables.
- Use a preferred_subject_anchor instead of the page title when the page title contains a year at or after the cutoff.
- For the 2026 FIFA World Cup page, use `23rd FIFA World Cup` instead of `2026 FIFA World Cup`.
- Do not ask about current, latest, most recent, or live-status facts.
- Do not make the question text depend on events in 2025 or later.
- Do not include the answer or answer aliases in the question or search queries.
- Generate exactly five answer-blind search queries.
- If no safe composition question is possible, set discard_reason and leave the other fields empty.

Output schema:
{
  "question": string,
  "answer": string,
  "answer_aliases": string[],
  "search_queries": string[],
  "composition_type": "max|min|sum|count|comparison|ordinal|other",
  "source_table": integer,
  "derivation_summary": string,
  "discard_reason": string | null
}

Payload:
{
  "title": "2026 FIFA World Cup",
  "canonical_url": "https://en.wikipedia.org/wiki/2026_FIFA_World_Cup",
  "first_paragraph": "The 2026 FIFA World Cup will be the 23rd FIFA World Cup, the quadrennial international men's soccer championship contested by the national teams of the member associations of FIFA. The tournament will take place from June 11 to July 19, 2026. It will be jointly hosted by sixteen cities—eleven in the United States, three in Mexico, and two in Canada. The tournament will be the first FIFA World Cup to be hosted by three nations, and the first to include 48 teams, an expansion from 32.",
  "preferred_subject_anchors": [
    "23rd FIFA World Cup"
  ],
  "table_selection_criteria": [
    "Prefer tables with many structured data rows.",
    "Prefer tables with numeric, ordinal, date, rank, count, or comparable value columns.",
    "Prefer tables whose row values are mostly not repeated in non-table prose, because these are less directly answerable from the article text.",
    "Prefer specific article tables over summary infoboxes when both are available."
  ],
  "ranked_table_selection": [
    {
      "table_index": 3,
      "table_type": "wikitable",
      "caption": "List of tournament venues",
      "section_heading": "Venues",
      "score": 9.9,
      "reasons": [
        "article_table",
        "multi_row",
        "has_headers",
        "numeric_values",
        "comparable_headers",
        "preferred_table_context",
        "high_prose_leakage"
      ],
      "row_count": 16,
      "numeric_cell_count": 16,
      "comparable_header_hits": [
        "age",
        "capacity"
      ],
      "preferred_context_hits": [
        "stadium",
        "venue",
        "venues"
      ],
      "mutable_context_hits": [],
      "zero_numeric_rate": 0.0,
      "prose_leakage": {
        "checked_values": 48,
        "leaked_values": 32,
        "leakage_rate": 0.6667
      }
    },
    {
      "table_index": 2,
      "table_type": "wikitable",
      "caption": "Voting results",
      "section_heading": "Voting",
      "score": 7.65,
      "reasons": [
        "article_table",
        "multi_row",
        "has_headers",
        "numeric_values",
        "comparable_headers"
      ],
      "row_count": 7,
      "numeric_cell_count": 6,
      "comparable_header_hits": [
        "vote"
      ],
      "preferred_context_hits": [],
      "mutable_context_hits": [],
      "zero_numeric_rate": 0.0,
      "prose_leakage": {
        "checked_values": 7,
        "leaked_values": 2,
        "leakage_rate": 0.2857
      }
    },
    {
      "table_index": 5,
      "table_type": "wikitable",
      "caption": "List of team base camps",
      "section_heading": "Team base camps",
      "score": 5.8,
      "reasons": [
        "article_table",
        "multi_row",
        "has_headers",
        "no_comparable_headers",
        "low_prose_leakage"
      ],
      "row_count": 48,
      "numeric_cell_count": 0,
      "comparable_header_hits": [],
      "preferred_context_hits": [],
      "mutable_context_hits": [],
      "zero_numeric_rate": 0.0,
      "prose_leakage": {
        "checked_values": 144,
        "leaked_values": 0,
        "leakage_rate": 0.0
      }
    },
    {
      "table_index": 25,
      "table_type": "wikitable",
      "caption": "Performance-based prize money based on final position",
      "section_heading": "Prize money",
      "score": 5.5,
      "reasons": [
        "article_table",
        "multi_row",
        "has_headers",
        "numeric_values",
        "no_comparable_headers"
      ],
      "row_count": 10,
      "numeric_cell_count": 26,
      "comparable_header_hits": [],
      "preferred_context_hits": [],
      "mutable_context_hits": [],
      "zero_numeric_rate": 0.0,
      "prose_leakage": {
        "checked_values": 11,
        "leaked_values": 5,
        "leakage_rate": 0.4545
      }
    },
    {
      "table_index": 6,
      "table_type": "wikitable",
      "caption": "Schedule by round",
      "section_heading": "Match schedule",
      "score": 4.35,
      "reasons": [
        "article_table",
        "multi_row",
        "has_headers",
        "comparable_headers",
        "mutable_or_placeholder_context"
      ],
      "row_count": 9,
      "numeric_cell_count": 0,
      "comparable_header_hits": [
        "date"
      ],
      "preferred_context_hits": [],
      "mutable_context_hits": [
        "match schedule"
      ],
      "zero_numeric_rate": 0.0,
      "prose_leakage": {
        "checked_values": 20,
        "leaked_values": 10,
        "leakage_rate": 0.5
      }
    },
    {
      "table_index": 24,
      "table_type": "wikitable",
      "caption": "",
      "section_heading": "Domestic sponsors",
      "score": 3.05,
      "reasons": [
        "article_table",
        "multi_row",
        "has_headers",
        "no_comparable_headers"
      ],
      "row_count": 7,
      "numeric_cell_count": 0,
      "comparable_header_hits": [],
      "preferred_context_hits": [],
      "mutable_context_hits": [],
      "zero_numeric_rate": 0.0,
      "prose_leakage": {
        "checked_values": 18,
        "leaked_values": 9,
        "leakage_rate": 0.5
      }
    },
    {
      "table_index": 4,
      "table_type": "wikitable",
      "caption": "Pots [ N ]",
      "section_heading": "Draw",
      "score": 3.0,
      "reasons": [
        "article_table",
        "too_few_rows",
        "has_headers",
        "no_comparable_headers",
        "low_prose_leakage"
      ],
      "row_count": 1,
      "numeric_cell_count": 0,
      "comparable_header_hits": [],
      "preferred_context_hits": [],
      "mutable_context_hits": [],
      "zero_numeric_rate": 0.0,
      "prose_leakage": {
        "checked_values": 0,
        "leaked_values": 0,
        "leakage_rate": 0.0
      }
    },
    {
      "table_index": 22,
      "table_type": "wikitable",
      "caption": "",
      "section_heading": "Sponsorships",
      "score": 3.0,
      "reasons": [
        "article_table",
        "too_few_rows",
        "has_headers",
        "no_comparable_headers",
        "low_prose_leakage"
      ],
      "row_count": 1,
      "numeric_cell_count": 0,
      "comparable_header_hits": [],
      "preferred_context_hits": [],
      "mutable_context_hits": [],
      "zero_numeric_rate": 0.0,
      "prose_leakage": {
        "checked_values": 0,
        "leaked_values": 0,
        "leakage_rate": 0.0
      }
    }
  ],
  "tables": [
    {
      "table_index": 3,
      "table_type": "wikitable",
      "section_heading": "Venues",
      "caption": "List of tournament venues",
      "headers": [
        "City",
        "Stadium",
        "Capacity",
        "Image"
      ],
      "rows": [
        [
          "City",
          "Stadium",
          "Capacity",
          "Image"
        ],
        [
          "Dallas ( Arlington, Texas )",
          "AT&T Stadium ‡ (Dallas Stadium)",
          "94,000"
        ],
        [
          "Mexico City",
          "Estadio Azteca † (Mexico City Stadium)",
          "83,000"
        ],
        [
          "New York/New Jersey ( East Rutherford, New Jersey )",
          "MetLife Stadium (New York New Jersey Stadium)",
          "82,500"
        ],
        [
          "Atlanta",
          "Mercedes-Benz Stadium ‡ (Atlanta Stadium)",
          "75,000"
        ],
        [
          "Kansas City",
          "Arrowhead Stadium (Kansas City Stadium)",
          "73,000"
        ],
        [
          "Houston",
          "NRG Stadium ‡ (Houston Stadium)",
          "72,000"
        ],
        [
          "San Francisco Bay Area ( Santa Clara, California )",
          "Levi's Stadium (San Francisco Bay Area Stadium)",
          "71,000"
        ],
        [
          "Los Angeles ( Inglewood, California )",
          "SoFi Stadium (Los Angeles Stadium)",
          "70,000"
        ],
        [
          "Philadelphia",
          "Lincoln Financial Field (Philadelphia Stadium)",
          "69,000"
        ],
        [
          "Seattle",
          "Lumen Field (Seattle Stadium)",
          "69,000"
        ],
        [
          "Boston ( Foxborough, Massachusetts )",
          "Gillette Stadium (Boston Stadium)",
          "65,000"
        ],
        [
          "Miami ( Miami Gardens, Florida )",
          "Hard Rock Stadium (Miami Stadium)",
          "65,000"
        ],
        [
          "Vancouver",
          "BC Place ‡ (BC Place Vancouver)",
          "54,000"
        ],
        [
          "Monterrey ( Guadalupe )",
          "Estadio BBVA (Estadio Monterrey)",
          "53,500"
        ],
        [
          "Guadalajara ( Zapopan )",
          "Estadio Akron (Estadio Guadalajara)",
          "48,000"
        ],
        [
          "Toronto",
          "BMO Field (Toronto Stadium)",
          "45,000"
        ]
      ],
      "row_dicts": [
        {
          "City": "Dallas ( Arlington, Texas )",
          "Stadium": "AT&T Stadium ‡ (Dallas Stadium)",
          "Capacity": "94,000"
        },
        {
          "City": "Mexico City",
          "Stadium": "Estadio Azteca † (Mexico City Stadium)",
          "Capacity": "83,000"
        },
        {
          "City": "New York/New Jersey ( East Rutherford, New Jersey )",
          "Stadium": "MetLife Stadium (New York New Jersey Stadium)",
          "Capacity": "82,500"
        },
        {
          "City": "Atlanta",
          "Stadium": "Mercedes-Benz Stadium ‡ (Atlanta Stadium)",
          "Capacity": "75,000"
        },
        {
          "City": "Kansas City",
          "Stadium": "Arrowhead Stadium (Kansas City Stadium)",
          "Capacity": "73,000"
        },
        {
          "City": "Houston",
          "Stadium": "NRG Stadium ‡ (Houston Stadium)",
          "Capacity": "72,000"
        },
        {
          "City": "San Francisco Bay Area ( Santa Clara, California )",
          "Stadium": "Levi's Stadium (San Francisco Bay Area Stadium)",
          "Capacity": "71,000"
        },
        {
          "City": "Los Angeles ( Inglewood, California )",
          "Stadium": "SoFi Stadium (Los Angeles Stadium)",
          "Capacity": "70,000"
        },
        {
          "City": "Philadelphia",
          "Stadium": "Lincoln Financial Field (Philadelphia Stadium)",
          "Capacity": "69,000"
        },
        {
          "City": "Seattle",
          "Stadium": "Lumen Field (Seattle Stadium)",
          "Capacity": "69,000"
        },
        {
          "City": "Boston ( Foxborough, Massachusetts )",
          "Stadium": "Gillette Stadium (Boston Stadium)",
          "Capacity": "65,000"
        },
        {
          "City": "Miami ( Miami Gardens, Florida )",
          "Stadium": "Hard Rock Stadium (Miami Stadium)",
          "Capacity": "65,000"
        },
        {
          "City": "Vancouver",
          "Stadium": "BC Place ‡ (BC Place Vancouver)",
          "Capacity": "54,000"
        },
        {
          "City": "Monterrey ( Guadalupe )",
          "Stadium": "Estadio BBVA (Estadio Monterrey)",
          "Capacity": "53,500"
        },
        {
          "City": "Guadalajara ( Zapopan )",
          "Stadium": "Estadio Akron (Estadio Guadalajara)",
          "Capacity": "48,000"
        },
        {
          "City": "Toronto",
          "Stadium": "BMO Field (Toronto Stadium)",
          "Capacity": "45,000"
        }
      ],
      "normalized_text": "Venues\nList of tournament venues\nCity | Stadium | Capacity | Image\nDallas ( Arlington, Texas ) | AT&T Stadium ‡ (Dallas Stadium) | 94,000\nMexico City | Estadio Azteca † (Mexico City Stadium) | 83,000\nNew York/New Jersey ( East Rutherford, New Jersey ) | MetLife Stadium (New York New Jersey Stadium) | 82,500\nAtlanta | Mercedes-Benz Stadium ‡ (Atlanta Stadium) | 75,000\nKansas City | Arrowhead Stadium (Kansas City Stadium) | 73,000\nHouston | NRG Stadium ‡ (Houston Stadium) | 72,000\nSan Francisco Bay Area ( Santa Clara, California ) | Levi's Stadium (San Francisco Bay Area Stadium) | 71,000\nLos Angeles ( Inglewood, California ) | SoFi Stadium (Los Angeles Stadium) | 70,000\nPhiladelphia | Lincoln Financial Field (Philadelphia Stadium) | 69,000\nSeattle | Lumen Field (Seattle Stadium) | 69,000\nBoston ( Foxborough, Massachusetts ) | Gillette Stadium (Boston Stadium) | 65,000\nMiami ( Miami Gardens, Florida ) | Hard Rock Stadium (Miami Stadium) | 65,000\nVancouver | BC Place ‡ (BC Place Vancouver) | 54,000\nMonterrey ( Guadalupe ) | Estadio BBVA (Estadio Monterrey) | 53,500\nGuadalajara ( Zapopan ) | Estadio Akron (Estadio Guadalajara) | 48,000\nToronto | BMO Field (Toronto Stadium) | 45,000",
      "truncated": false
    },
    {
      "table_index": 2,
      "table_type": "wikitable",
      "section_heading": "Voting",
      "caption": "Voting results",
      "headers": [
        "Nation",
        "Vote"
      ],
      "rows": [
        [
          "Nation",
          "Vote"
        ],
        [
          "Round 1"
        ],
        [
          "Canada, Mexico, United States",
          "134"
        ],
        [
          "Morocco",
          "65"
        ],
        [
          "None of the bids",
          "1"
        ],
        [
          "Abstentions",
          "3"
        ],
        [
          "Total votes",
          "200"
        ],
        [
          "Required for majority",
          "101"
        ]
      ],
      "row_dicts": [
        {
          "Nation": "Canada, Mexico, United States",
          "Vote": "134"
        },
        {
          "Nation": "Morocco",
          "Vote": "65"
        },
        {
          "Nation": "None of the bids",
          "Vote": "1"
        },
        {
          "Nation": "Abstentions",
          "Vote": "3"
        },
        {
          "Nation": "Total votes",
          "Vote": "200"
        },
        {
          "Nation": "Required for majority",
          "Vote": "101"
        }
      ],
      "normalized_text": "Voting\nVoting results\nNation | Vote\nRound 1\nCanada, Mexico, United States | 134\nMorocco | 65\nNone of the bids | 1\nAbstentions | 3\nTotal votes | 200\nRequired for majority | 101",
      "truncated": false
    },
    {
      "table_index": 5,
      "table_type": "wikitable",
      "section_heading": "Team base camps",
      "caption": "List of team base camps",
      "headers": [
        "Team",
        "Hotel",
        "Training site"
      ],
      "rows": [
        [
          "Team",
          "Hotel",
          "Training site"
        ],
        [
          "Algeria [ 86 ]",
          "The Oread Lawrence, Lawrence, Kansas",
          "University of Kansas , [ 87 ] Lawrence, Kansas"
        ],
        [
          "Argentina [ 88 ]",
          "Origin Kansas City Riverfront, Kansas City, Missouri",
          "Sporting KC Training Center, Kansas City, Kansas"
        ],
        [
          "Australia [ 89 ]",
          "Claremont Hotel & Spa , Berkeley, California",
          "Oakland Roots / Soul Training Facility, Alameda, California"
        ],
        [
          "Austria [ 90 ]",
          "Bacara Resort , Goleta, California",
          "UCSB Harder Stadium , Santa Barbara, California"
        ],
        [
          "Belgium [ 91 ]",
          "Hyatt Regency Lake Washington at Seattle's Southport, Renton, Washington",
          "Seattle Sounders FC Performance Center and Clubhouse, Renton, Washington"
        ],
        [
          "Bosnia and Herzegovina [ 92 ]",
          "Asher Adams, Autograph Collection , Salt Lake City, Utah",
          "Real Salt Lake Training Center, Herriman, Utah"
        ],
        [
          "Brazil [ 93 ]",
          "The Ridge, Basking Ridge, New Jersey",
          "Columbia Park , Morristown, New Jersey"
        ],
        [
          "Canada [ 94 ]",
          "The Westin Bayshore , Vancouver, British Columbia",
          "National Soccer Development Centre , Vancouver, British Columbia"
        ],
        [
          "Cape Verde [ 95 ]",
          "Grand Hyatt Tampa Bay, Tampa, Florida",
          "Waters Sportsplex, Tampa, Florida"
        ],
        [
          "Colombia [ 96 ]",
          "Grand Fiesta Americana Country Club, Guadalajara, Jalisco",
          "Academia Atlas FC , Zapopan, Jalisco"
        ],
        [
          "Croatia [ 97 ]",
          "Hotel AKA Alexandria, Alexandria, Virginia",
          "Episcopal High School , Alexandria, Virginia"
        ],
        [
          "Curaçao [ 98 ]",
          "Boca Raton Marriott at Boca Center, Boca Raton, Florida",
          "Florida Atlantic University , Boca Raton, Florida"
        ],
        [
          "Czech Republic [ 99 ]",
          "Hilton Garden Inn Dallas-Arlington South, Arlington, Texas",
          "Mansfield Multipurpose Stadium , Mansfield, Texas"
        ],
        [
          "DR Congo [ 100 ]",
          "Omni Houston Hotel, Houston, Texas",
          "Houston Sports Park , Houston, Texas"
        ],
        [
          "Ecuador [ 101 ]",
          "Le Méridien Columbus, The Joseph, Columbus, Ohio",
          "Columbus Crew Performance Center , Columbus, Ohio"
        ],
        [
          "Egypt [ 102 ]",
          "Northern Quest Resort & Casino , Airway Heights, Washington",
          "Gonzaga University , Spokane, Washington"
        ],
        [
          "England [ 86 ]",
          "The Inn at Meadowbrook, Prairie Village, Kansas",
          "Swope Soccer Village , Kansas City, Missouri"
        ],
        [
          "France [ 103 ]",
          "Four Seasons Hotel Boston, Boston, Massachusetts",
          "Bentley University , Waltham, Massachusetts"
        ],
        [
          "Germany [ 104 ]",
          "Graylyn , Winston-Salem, North Carolina",
          "Wake Forest University , Winston-Salem, North Carolina"
        ],
        [
          "Ghana [ 105 ]",
          "Providence Biltmore , Providence, Rhode Island",
          "Bryant University , Smithfield, Rhode Island"
        ],
        [
          "Haiti [ 106 ]",
          "Sheraton Atlantic City Convention Center Hotel, Atlantic City, New Jersey",
          "Stockton University , Galloway Township, New Jersey"
        ],
        [
          "Iran [ 107 ]",
          "Westward Look Wyndham Grand Resort and Spa, Tucson, Arizona",
          "Kino Sports Complex , Tucson, Arizona"
        ],
        [
          "Iraq [ 95 ]",
          "Greenbrier Resort , White Sulphur Springs, West Virginia",
          "The Greenbrier Sports Performance Centre, White Sulphur Springs, West Virginia"
        ],
        [
          "Ivory Coast [ 108 ]",
          "Hotel Du Pont , Wilmington, Delaware",
          "Philadelphia Union Stadium , Chester, Pennsylvania"
        ],
        [
          "Japan [ 109 ]",
          "TBA, Nashville, Tennessee",
          "Nashville SC Training Center, Nashville, Tennessee"
        ],
        [
          "Jordan [ 110 ]",
          "The Nines Hotel , Portland, Oregon",
          "University of Portland , Portland, Oregon"
        ],
        [
          "Mexico [ 111 ]",
          "Centro de Alto Rendimiento on-site accommodation, Mexico City",
          "Centro de Alto Rendimiento, Mexico City"
        ],
        [
          "Morocco [ 112 ]",
          "Somerset Hills Hotel, Tapestry Collection by Hilton , Warren, New Jersey",
          "Pingry School , Basking Ridge, New Jersey"
        ],
        [
          "Netherlands [ 113 ]",
          "Cascade Hotel, Kansas City, a Tribute Portfolio Hotel, Kansas City, Missouri",
          "Kansas City Current Training Facility, Riverside, Missouri"
        ],
        [
          "New Zealand [ 114 ]",
          "Hyatt Regency La Jolla at Aventine, San Diego, California",
          "Torero Stadium , San Diego, California"
        ],
        [
          "Norway [ 115 ]",
          "Grandover Resort & Spa, A Wyndham Grand Hotel , Greensboro, North Carolina",
          "University of North Carolina at Greensboro , Greensboro, North Carolina"
        ],
        [
          "Panama [ 116 ]",
          "Nottawasaga Inn Resort & Conference Centre, New Tecumseth, Ontario",
          "Nottawasaga Training Site, New Tecumseth, Ontario"
        ],
        [
          "Paraguay [ 117 ]",
          "Signia by Hilton San Jose , San Jose, California",
          "Spartan Soccer Complex , San Jose, California"
        ],
        [
          "Portugal [ 118 ]",
          "Four Seasons Hotel Palm Beach, Palm Beach, Florida",
          "Gardens North County District Park, Palm Beach Gardens, Florida"
        ],
        [
          "Qatar [ 119 ]",
          "Courtyard by Marriott Santa Barbara Goleta, Goleta, California",
          "Westmont College , Santa Barbara, California"
        ],
        [
          "Saudi Arabia [ 120 ]",
          "Four Seasons Hotel Austin, Austin, Texas",
          "Austin FC Stadium , Austin, Texas"
        ],
        [
          "Scotland [ 121 ]",
          "Renaissance Charlotte SouthPark Hotel, Charlotte, North Carolina",
          "Charlotte FC Training Center, Charlotte, North Carolina"
        ],
        [
          "Senegal [ 122 ]",
          "The Heldrich Hotel and Conference Center, New Brunswick, New Jersey",
          "Rutgers University , Piscataway, New Jersey"
        ],
        [
          "South Africa [ 111 ]",
          "Camino Real Pachuca, Pachuca, Hidalgo",
          "Universidad Del Futbol [ es ] , San Agustín Tlaxiaca, Hidalgo"
        ]
      ],
      "row_dicts": [
        {
          "Team": "Algeria [ 86 ]",
          "Hotel": "The Oread Lawrence, Lawrence, Kansas",
          "Training site": "University of Kansas , [ 87 ] Lawrence, Kansas"
        },
        {
          "Team": "Argentina [ 88 ]",
          "Hotel": "Origin Kansas City Riverfront, Kansas City, Missouri",
          "Training site": "Sporting KC Training Center, Kansas City, Kansas"
        },
        {
          "Team": "Australia [ 89 ]",
          "Hotel": "Claremont Hotel & Spa , Berkeley, California",
          "Training site": "Oakland Roots / Soul Training Facility, Alameda, California"
        },
        {
          "Team": "Austria [ 90 ]",
          "Hotel": "Bacara Resort , Goleta, California",
          "Training site": "UCSB Harder Stadium , Santa Barbara, California"
        },
        {
          "Team": "Belgium [ 91 ]",
          "Hotel": "Hyatt Regency Lake Washington at Seattle's Southport, Renton, Washington",
          "Training site": "Seattle Sounders FC Performance Center and Clubhouse, Renton, Washington"
        },
        {
          "Team": "Bosnia and Herzegovina [ 92 ]",
          "Hotel": "Asher Adams, Autograph Collection , Salt Lake City, Utah",
          "Training site": "Real Salt Lake Training Center, Herriman, Utah"
        },
        {
          "Team": "Brazil [ 93 ]",
          "Hotel": "The Ridge, Basking Ridge, New Jersey",
          "Training site": "Columbia Park , Morristown, New Jersey"
        },
        {
          "Team": "Canada [ 94 ]",
          "Hotel": "The Westin Bayshore , Vancouver, British Columbia",
          "Training site": "National Soccer Development Centre , Vancouver, British Columbia"
        },
        {
          "Team": "Cape Verde [ 95 ]",
          "Hotel": "Grand Hyatt Tampa Bay, Tampa, Florida",
          "Training site": "Waters Sportsplex, Tampa, Florida"
        },
        {
          "Team": "Colombia [ 96 ]",
          "Hotel": "Grand Fiesta Americana Country Club, Guadalajara, Jalisco",
          "Training site": "Academia Atlas FC , Zapopan, Jalisco"
        },
        {
          "Team": "Croatia [ 97 ]",
          "Hotel": "Hotel AKA Alexandria, Alexandria, Virginia",
          "Training site": "Episcopal High School , Alexandria, Virginia"
        },
        {
          "Team": "Curaçao [ 98 ]",
          "Hotel": "Boca Raton Marriott at Boca Center, Boca Raton, Florida",
          "Training site": "Florida Atlantic University , Boca Raton, Florida"
        },
        {
          "Team": "Czech Republic [ 99 ]",
          "Hotel": "Hilton Garden Inn Dallas-Arlington South, Arlington, Texas",
          "Training site": "Mansfield Multipurpose Stadium , Mansfield, Texas"
        },
        {
          "Team": "DR Congo [ 100 ]",
          "Hotel": "Omni Houston Hotel, Houston, Texas",
          "Training site": "Houston Sports Park , Houston, Texas"
        },
        {
          "Team": "Ecuador [ 101 ]",
          "Hotel": "Le Méridien Columbus, The Joseph, Columbus, Ohio",
          "Training site": "Columbus Crew Performance Center , Columbus, Ohio"
        },
        {
          "Team": "Egypt [ 102 ]",
          "Hotel": "Northern Quest Resort & Casino , Airway Heights, Washington",
          "Training site": "Gonzaga University , Spokane, Washington"
        },
        {
          "Team": "England [ 86 ]",
          "Hotel": "The Inn at Meadowbrook, Prairie Village, Kansas",
          "Training site": "Swope Soccer Village , Kansas City, Missouri"
        },
        {
          "Team": "France [ 103 ]",
          "Hotel": "Four Seasons Hotel Boston, Boston, Massachusetts",
          "Training site": "Bentley University , Waltham, Massachusetts"
        },
        {
          "Team": "Germany [ 104 ]",
          "Hotel": "Graylyn , Winston-Salem, North Carolina",
          "Training site": "Wake Forest University , Winston-Salem, North Carolina"
        },
        {
          "Team": "Ghana [ 105 ]",
          "Hotel": "Providence Biltmore , Providence, Rhode Island",
          "Training site": "Bryant University , Smithfield, Rhode Island"
        },
        {
          "Team": "Haiti [ 106 ]",
          "Hotel": "Sheraton Atlantic City Convention Center Hotel, Atlantic City, New Jersey",
          "Training site": "Stockton University , Galloway Township, New Jersey"
        },
        {
          "Team": "Iran [ 107 ]",
          "Hotel": "Westward Look Wyndham Grand Resort and Spa, Tucson, Arizona",
          "Training site": "Kino Sports Complex , Tucson, Arizona"
        },
        {
          "Team": "Iraq [ 95 ]",
          "Hotel": "Greenbrier Resort , White Sulphur Springs, West Virginia",
          "Training site": "The Greenbrier Sports Performance Centre, White Sulphur Springs, West Virginia"
        },
        {
          "Team": "Ivory Coast [ 108 ]",
          "Hotel": "Hotel Du Pont , Wilmington, Delaware",
          "Training site": "Philadelphia Union Stadium , Chester, Pennsylvania"
        },
        {
          "Team": "Japan [ 109 ]",
          "Hotel": "TBA, Nashville, Tennessee",
          "Training site": "Nashville SC Training Center, Nashville, Tennessee"
        },
        {
          "Team": "Jordan [ 110 ]",
          "Hotel": "The Nines Hotel , Portland, Oregon",
          "Training site": "University of Portland , Portland, Oregon"
        },
        {
          "Team": "Mexico [ 111 ]",
          "Hotel": "Centro de Alto Rendimiento on-site accommodation, Mexico City",
          "Training site": "Centro de Alto Rendimiento, Mexico City"
        },
        {
          "Team": "Morocco [ 112 ]",
          "Hotel": "Somerset Hills Hotel, Tapestry Collection by Hilton , Warren, New Jersey",
          "Training site": "Pingry School , Basking Ridge, New Jersey"
        },
        {
          "Team": "Netherlands [ 113 ]",
          "Hotel": "Cascade Hotel, Kansas City, a Tribute Portfolio Hotel, Kansas City, Missouri",
          "Training site": "Kansas City Current Training Facility, Riverside, Missouri"
        },
        {
          "Team": "New Zealand [ 114 ]",
          "Hotel": "Hyatt Regency La Jolla at Aventine, San Diego, California",
          "Training site": "Torero Stadium , San Diego, California"
        },
        {
          "Team": "Norway [ 115 ]",
          "Hotel": "Grandover Resort & Spa, A Wyndham Grand Hotel , Greensboro, North Carolina",
          "Training site": "University of North Carolina at Greensboro , Greensboro, North Carolina"
        },
        {
          "Team": "Panama [ 116 ]",
          "Hotel": "Nottawasaga Inn Resort & Conference Centre, New Tecumseth, Ontario",
          "Training site": "Nottawasaga Training Site, New Tecumseth, Ontario"
        },
        {
          "Team": "Paraguay [ 117 ]",
          "Hotel": "Signia by Hilton San Jose , San Jose, California",
          "Training site": "Spartan Soccer Complex , San Jose, California"
        },
        {
          "Team": "Portugal [ 118 ]",
          "Hotel": "Four Seasons Hotel Palm Beach, Palm Beach, Florida",
          "Training site": "Gardens North County District Park, Palm Beach Gardens, Florida"
        },
        {
          "Team": "Qatar [ 119 ]",
          "Hotel": "Courtyard by Marriott Santa Barbara Goleta, Goleta, California",
          "Training site": "Westmont College , Santa Barbara, California"
        },
        {
          "Team": "Saudi Arabia [ 120 ]",
          "Hotel": "Four Seasons Hotel Austin, Austin, Texas",
          "Training site": "Austin FC Stadium , Austin, Texas"
        },
        {
          "Team": "Scotland [ 121 ]",
          "Hotel": "Renaissance Charlotte SouthPark Hotel, Charlotte, North Carolina",
          "Training site": "Charlotte FC Training Center, Charlotte, North Carolina"
        },
        {
          "Team": "Senegal [ 122 ]",
          "Hotel": "The Heldrich Hotel and Conference Center, New Brunswick, New Jersey",
          "Training site": "Rutgers University , Piscataway, New Jersey"
        },
        {
          "Team": "South Africa [ 111 ]",
          "Hotel": "Camino Real Pachuca, Pachuca, Hidalgo",
          "Training site": "Universidad Del Futbol [ es ] , San Agustín Tlaxiaca, Hidalgo"
        },
        {
          "Team": "South Korea [ 123 ]",
          "Hotel": "The Westin Guadalajara, Guadalajara, Jalisco",
          "Training site": "Chivas Verde Valle, Zapopan, Jalisco"
        }
      ],
      "normalized_text": "Team base camps\nList of team base camps\nTeam | Hotel | Training site\nAlgeria [ 86 ] | The Oread Lawrence, Lawrence, Kansas | University of Kansas , [ 87 ] Lawrence, Kansas\nArgentina [ 88 ] | Origin Kansas City Riverfront, Kansas City, Missouri | Sporting KC Training Center, Kansas City, Kansas\nAustralia [ 89 ] | Claremont Hotel & Spa , Berkeley, California | Oakland Roots / Soul Training Facility, Alameda, California\nAustria [ 90 ] | Bacara Resort , Goleta, California | UCSB Harder Stadium , Santa Barbara, California\nBelgium [ 91 ] | Hyatt Regency Lake Washington at Seattle's Southport, Renton, Washington | Seattle Sounders FC Performance Center and Clubhouse, Renton, Washington\nBosnia and Herzegovina [ 92 ] | Asher Adams, Autograph Collection , Salt Lake City, Utah | Real Salt Lake Training Center, Herriman, Utah\nBrazil [ 93 ] | The Ridge, Basking Ridge, New Jersey | Columbia Park , Morristown, New Jersey\nCanada [ 94 ] | The Westin Bayshore , Vancouver, British Columbia | National Soccer Development Centre , Vancouver, British Columbia\nCape Verde [ 95 ] | Grand Hyatt Tampa Bay, Tampa, Florida | Waters Sportsplex, Tampa, Florida\nColombia [ 96 ] | Grand Fiesta Americana Country Club, Guadalajara, Jalisco | Academia Atlas FC , Zapopan, Jalisco\nCroatia [ 97 ] | Hotel AKA Alexandria, Alexandria, Virginia | Episcopal High School , Alexandria, Virginia\nCuraçao [ 98 ] | Boca Raton Marriott at Boca Center, Boca Raton, Florida | Florida Atlantic University , Boca Raton, Florida\nCzech Republic [ 99 ] | Hilton Garden Inn Dallas-Arlington South, Arlington, Texas | Mansfield Multipurpose Stadium , Mansfield, Texas\nDR Congo [ 100 ] | Omni Houston Hotel, Houston, Texas | Houston Sports Park , Houston, Texas\nEcuador [ 101 ] | Le Méridien Columbus, The Joseph, Columbus, Ohio | Columbus Crew Performance Center , Columbus, Ohio\nEgypt [ 102 ] | Northern Quest Resort & Casino , Airway Heights, Washington | Gonzaga University , Spokane, Washington\nEngland [ 86 ] | The Inn at Meadowbrook, Prairie Village, Kansas | Swope Soccer Village , Kansas City, Missouri\nFrance [ 103 ] | Four Seasons Hotel Boston, Boston, Massachusetts | Bentley University , Waltham, Massachusetts\nGermany [ 104 ] | Graylyn , Winston-Salem, North Carolina | Wake Forest University , Winston-Salem, North Carolina\nGhana [ 105 ] | Providence Biltmore , Providence, Rhode Island | Bryant University , Smithfield, Rhode Island\nHaiti [ 106 ] | Sheraton Atlantic City Convention Center Hotel, Atlantic City, New Jersey |",
      "truncated": true
    },
    {
      "table_index": 25,
      "table_type": "wikitable",
      "section_heading": "Prize money",
      "caption": "Performance-based prize money based on final position",
      "headers": [
        "Place",
        "Teams",
        "Amount (in millions)"
      ],
      "rows": [
        [
          "Place",
          "Teams",
          "Amount (in millions)"
        ],
        [
          "Per team",
          "Total"
        ],
        [
          "Champions",
          "1",
          "$50",
          "$50"
        ],
        [
          "Runners-up",
          "1",
          "$33",
          "$33"
        ],
        [
          "Third place",
          "1",
          "$29",
          "$29"
        ],
        [
          "Fourth place",
          "1",
          "$27",
          "$27"
        ],
        [
          "5th–8th place (quarter-finals)",
          "4",
          "$19",
          "$76"
        ],
        [
          "9th–16th place (round of 16)",
          "8",
          "$15",
          "$120"
        ],
        [
          "17th–32nd place (round of 32)",
          "16",
          "$11",
          "$176"
        ],
        [
          "33rd–48th place (group stage)",
          "16",
          "$9",
          "$144"
        ],
        [
          "Total",
          "48",
          "$655"
        ]
      ],
      "row_dicts": [
        {
          "Place": "Per team",
          "Teams": "Total"
        },
        {
          "Place": "Champions",
          "Teams": "1",
          "Amount (in millions)": "$50"
        },
        {
          "Place": "Runners-up",
          "Teams": "1",
          "Amount (in millions)": "$33"
        },
        {
          "Place": "Third place",
          "Teams": "1",
          "Amount (in millions)": "$29"
        },
        {
          "Place": "Fourth place",
          "Teams": "1",
          "Amount (in millions)": "$27"
        },
        {
          "Place": "5th–8th place (quarter-finals)",
          "Teams": "4",
          "Amount (in millions)": "$19"
        },
        {
          "Place": "9th–16th place (round of 16)",
          "Teams": "8",
          "Amount (in millions)": "$15"
        },
        {
          "Place": "17th–32nd place (round of 32)",
          "Teams": "16",
          "Amount (in millions)": "$11"
        },
        {
          "Place": "33rd–48th place (group stage)",
          "Teams": "16",
          "Amount (in millions)": "$9"
        },
        {
          "Place": "Total",
          "Teams": "48",
          "Amount (in millions)": "$655"
        }
      ],
      "normalized_text": "Prize money\nPerformance-based prize money based on final position\nPlace | Teams | Amount (in millions)\nPer team | Total\nChampions | 1 | $50 | $50\nRunners-up | 1 | $33 | $33\nThird place | 1 | $29 | $29\nFourth place | 1 | $27 | $27\n5th–8th place (quarter-finals) | 4 | $19 | $76\n9th–16th place (round of 16) | 8 | $15 | $120\n17th–32nd place (round of 32) | 16 | $11 | $176\n33rd–48th place (group stage) | 16 | $9 | $144\nTotal | 48 | $655",
      "truncated": false
    },
    {
      "table_index": 6,
      "table_type": "wikitable",
      "section_heading": "Match schedule",
      "caption": "Schedule by round",
      "headers": [
        "Round",
        "Matchday",
        "Date"
      ],
      "rows": [
        [
          "Round",
          "Matchday",
          "Date"
        ],
        [
          "Group stage",
          "Matchday 1",
          "June 11–17, 2026"
        ],
        [
          "Matchday 2",
          "June 18–23, 2026"
        ],
        [
          "Matchday 3",
          "June 24–27, 2026"
        ],
        [
          "Knockout stage",
          "Round of 32",
          "June 28 – July 3, 2026"
        ],
        [
          "Round of 16",
          "July 4–7, 2026"
        ],
        [
          "Quarterfinals",
          "July 9–11, 2026"
        ],
        [
          "Semifinals",
          "July 14–15, 2026"
        ],
        [
          "Match for third place",
          "July 18, 2026"
        ],
        [
          "Final",
          "July 19, 2026"
        ]
      ],
      "row_dicts": [
        {
          "Round": "Group stage",
          "Matchday": "Matchday 1",
          "Date": "June 11–17, 2026"
        },
        {
          "Round": "Matchday 2",
          "Matchday": "June 18–23, 2026"
        },
        {
          "Round": "Matchday 3",
          "Matchday": "June 24–27, 2026"
        },
        {
          "Round": "Knockout stage",
          "Matchday": "Round of 32",
          "Date": "June 28 – July 3, 2026"
        },
        {
          "Round": "Round of 16",
          "Matchday": "July 4–7, 2026"
        },
        {
          "Round": "Quarterfinals",
          "Matchday": "July 9–11, 2026"
        },
        {
          "Round": "Semifinals",
          "Matchday": "July 14–15, 2026"
        },
        {
          "Round": "Match for third place",
          "Matchday": "July 18, 2026"
        },
        {
          "Round": "Final",
          "Matchday": "July 19, 2026"
        }
      ],
      "normalized_text": "Match schedule\nSchedule by round\nRound | Matchday | Date\nGroup stage | Matchday 1 | June 11–17, 2026\nMatchday 2 | June 18–23, 2026\nMatchday 3 | June 24–27, 2026\nKnockout stage | Round of 32 | June 28 – July 3, 2026\nRound of 16 | July 4–7, 2026\nQuarterfinals | July 9–11, 2026\nSemifinals | July 14–15, 2026\nMatch for third place | July 18, 2026\nFinal | July 19, 2026",
      "truncated": false
    },
    {
      "table_index": 24,
      "table_type": "wikitable",
      "section_heading": "Domestic sponsors",
      "caption": "",
      "headers": [
        "Atlanta",
        "Boston",
        "Dallas",
        "Guadalajara"
      ],
      "rows": [
        [
          "Atlanta",
          "Boston",
          "Dallas",
          "Guadalajara"
        ],
        [
          "Cox Enterprises [ 198 ] [ 200 ] Georgia-Pacific [ 198 ] [ 200 ] Home Depot [ 198 ] [ 200 ] NAPA Auto Parts [ 201 ] Southern Company [ 198 ] [ 200 ]",
          "Meet Boston [ 202 ] Sanofi [ 203 ] State Street [ 203 ]",
          "Arca Continental [ 204 ] Choctaw Casinos & Resorts [ 205 ] North Texas Sports Foundation [ 206 ] UT Southwestern [ 206 ]",
          "Guadalajara [ 207 ] Jalisco [ 207 ] Zapopan [ 207 ]"
        ],
        [
          "Houston",
          "Kansas City",
          "Los Angeles",
          "Monterrey"
        ],
        [
          "Aramco [ 208 ] Arca Continental [ 208 ] Houston Methodist Hospital [ 208 ] Hunton Group [ 208 ] NRG Energy [ 209 ] Quanta Services [ 208 ] Rice University [ 210 ] Visit Sugar Land [ 211 ]",
          "Black & Veatch [ 212 ] Hallmark [ 213 ] J. E. Dunn Construction [ 213 ] Populous [ 214 ] Purina [ 214 ] University of Kansas Health System [ 213 ]",
          "Amgen [ 215 ] Archer Aviation [ 215 ] Discover Los Angeles [ 216 ] Kaiser Permanente [ 215 ] Los Angeles Metro [ 217 ]",
          "TBD"
        ],
        [
          "Mexico City",
          "Miami [ 218 ]",
          "New York/New Jersey",
          "Philadelphia [ 219 ]"
        ],
        [
          "Club América [ 220 ] Uber [ 220 ]",
          "Bilzin Sumberg [ 218 ] Hard Rock Casino [ 218 ] Royal Caribbean [ 221 ] University of Miami [ 218 ]",
          "Bristol Myers Squibb [ 222 ] Hackensack Meridian Health [ 223 ] Onyx Equities [ 224 ] Paul, Weiss, Rifkind, Wharton & Garrison [ 225 ] Public Service Enterprise Group [ 226 ] Related Companies [ 227 ] Sports Illustrated [ 228 ]",
          "Cencora Comcast Independence Blue Cross PECO Energy Company Penn Medicine Philadelphia Eagles VisitPA William Penn Foundation"
        ],
        [
          "San Francisco Bay Area [ 229 ]",
          "Seattle",
          "Toronto",
          "Vancouver"
        ],
        [
          "Boston Consulting Group Electronic Arts Genentech Kaiser Permanente",
          "Puyallup Tribe of Indians [ 230 ]",
          "Humber Polytechnic [ 231 ] OLG [ 232 ] OPG [ 233 ] [ 232 ] Toronto FC [ 232 ]",
          "TBD"
        ]
      ],
      "row_dicts": [
        {
          "Atlanta": "Cox Enterprises [ 198 ] [ 200 ] Georgia-Pacific [ 198 ] [ 200 ] Home Depot [ 198 ] [ 200 ] NAPA Auto Parts [ 201 ] Southern Company [ 198 ] [ 200 ]",
          "Boston": "Meet Boston [ 202 ] Sanofi [ 203 ] State Street [ 203 ]",
          "Dallas": "Arca Continental [ 204 ] Choctaw Casinos & Resorts [ 205 ] North Texas Sports Foundation [ 206 ] UT Southwestern [ 206 ]",
          "Guadalajara": "Guadalajara [ 207 ] Jalisco [ 207 ] Zapopan [ 207 ]"
        },
        {
          "Atlanta": "Houston",
          "Boston": "Kansas City",
          "Dallas": "Los Angeles",
          "Guadalajara": "Monterrey"
        },
        {
          "Atlanta": "Aramco [ 208 ] Arca Continental [ 208 ] Houston Methodist Hospital [ 208 ] Hunton Group [ 208 ] NRG Energy [ 209 ] Quanta Services [ 208 ] Rice University [ 210 ] Visit Sugar Land [ 211 ]",
          "Boston": "Black & Veatch [ 212 ] Hallmark [ 213 ] J. E. Dunn Construction [ 213 ] Populous [ 214 ] Purina [ 214 ] University of Kansas Health System [ 213 ]",
          "Dallas": "Amgen [ 215 ] Archer Aviation [ 215 ] Discover Los Angeles [ 216 ] Kaiser Permanente [ 215 ] Los Angeles Metro [ 217 ]",
          "Guadalajara": "TBD"
        },
        {
          "Atlanta": "Mexico City",
          "Boston": "Miami [ 218 ]",
          "Dallas": "New York/New Jersey",
          "Guadalajara": "Philadelphia [ 219 ]"
        },
        {
          "Atlanta": "Club América [ 220 ] Uber [ 220 ]",
          "Boston": "Bilzin Sumberg [ 218 ] Hard Rock Casino [ 218 ] Royal Caribbean [ 221 ] University of Miami [ 218 ]",
          "Dallas": "Bristol Myers Squibb [ 222 ] Hackensack Meridian Health [ 223 ] Onyx Equities [ 224 ] Paul, Weiss, Rifkind, Wharton & Garrison [ 225 ] Public Service Enterprise Group [ 226 ] Related Companies [ 227 ] Sports Illustrated [ 228 ]",
          "Guadalajara": "Cencora Comcast Independence Blue Cross PECO Energy Company Penn Medicine Philadelphia Eagles VisitPA William Penn Foundation"
        },
        {
          "Atlanta": "San Francisco Bay Area [ 229 ]",
          "Boston": "Seattle",
          "Dallas": "Toronto",
          "Guadalajara": "Vancouver"
        },
        {
          "Atlanta": "Boston Consulting Group Electronic Arts Genentech Kaiser Permanente",
          "Boston": "Puyallup Tribe of Indians [ 230 ]",
          "Dallas": "Humber Polytechnic [ 231 ] OLG [ 232 ] OPG [ 233 ] [ 232 ] Toronto FC [ 232 ]",
          "Guadalajara": "TBD"
        }
      ],
      "normalized_text": "Domestic sponsors\nAtlanta | Boston | Dallas | Guadalajara\nCox Enterprises [ 198 ] [ 200 ] Georgia-Pacific [ 198 ] [ 200 ] Home Depot [ 198 ] [ 200 ] NAPA Auto Parts [ 201 ] Southern Company [ 198 ] [ 200 ] | Meet Boston [ 202 ] Sanofi [ 203 ] State Street [ 203 ] | Arca Continental [ 204 ] Choctaw Casinos & Resorts [ 205 ] North Texas Sports Foundation [ 206 ] UT Southwestern [ 206 ] | Guadalajara [ 207 ] Jalisco [ 207 ] Zapopan [ 207 ]\nHouston | Kansas City | Los Angeles | Monterrey\nAramco [ 208 ] Arca Continental [ 208 ] Houston Methodist Hospital [ 208 ] Hunton Group [ 208 ] NRG Energy [ 209 ] Quanta Services [ 208 ] Rice University [ 210 ] Visit Sugar Land [ 211 ] | Black & Veatch [ 212 ] Hallmark [ 213 ] J. E. Dunn Construction [ 213 ] Populous [ 214 ] Purina [ 214 ] University of Kansas Health System [ 213 ] | Amgen [ 215 ] Archer Aviation [ 215 ] Discover Los Angeles [ 216 ] Kaiser Permanente [ 215 ] Los Angeles Metro [ 217 ] | TBD\nMexico City | Miami [ 218 ] | New York/New Jersey | Philadelphia [ 219 ]\nClub América [ 220 ] Uber [ 220 ] | Bilzin Sumberg [ 218 ] Hard Rock Casino [ 218 ] Royal Caribbean [ 221 ] University of Miami [ 218 ] | Bristol Myers Squibb [ 222 ] Hackensack Meridian Health [ 223 ] Onyx Equities [ 224 ] Paul, Weiss, Rifkind, Wharton & Garrison [ 225 ] Public Service Enterprise Group [ 226 ] Related Companies [ 227 ] Sports Illustrated [ 228 ] | Cencora Comcast Independence Blue Cross PECO Energy Company Penn Medicine Philadelphia Eagles VisitPA William Penn Foundation\nSan Francisco Bay Area [ 229 ] | Seattle | Toronto | Vancouver\nBoston Consulting Group Electronic Arts Genentech Kaiser Permanente | Puyallup Tribe of Indians [ 230 ] | Humber Polytechnic [ 231 ] OLG [ 232 ] OPG [ 233 ] [ 232 ] Toronto FC [ 232 ] | TBD",
      "truncated": false
    },
    {
      "table_index": 4,
      "table_type": "wikitable",
      "section_heading": "Draw",
      "caption": "Pots [ N ]",
      "headers": [
        "Pot 1",
        "Pot 2",
        "Pot 3",
        "Pot 4"
      ],
      "rows": [
        [
          "Pot 1",
          "Pot 2",
          "Pot 3",
          "Pot 4"
        ],
        [
          "United States (co-host) (14) Mexico (co-host) (15) Canada (co-host) (27) Spain (1) Argentina (2) France (3) England (4) Brazil (5) Portugal (6) Netherlands (7) Belgium (8) Germany (9)",
          "Croatia (10) Morocco (11) Colombia (13) Uruguay (16) Switzerland (17) Japan (18) Senegal (19) Iran (20) South Korea (22) Ecuador (23) Austria (24) Australia (26)",
          "Norway (29) Panama (30) Egypt (34) Algeria (35) Scotland (36) Paraguay (39) Tunisia (40) Ivory Coast (42) Uzbekistan (50) Qatar (51) Saudi Arabia (60) South Africa (61)",
          "Jordan (66) Cape Verde (68) Ghana (72) Curaçao (82) Haiti (84) New Zealand (86) UEFA Path A winners [ O ] UEFA Path B winners [ O ] UEFA Path C winners [ O ] UEFA Path D winners [ O ] IC Path 1 winners [ O ] [ P ] IC Path 2 winners [ O ] [ Q ]"
        ]
      ],
      "row_dicts": [
        {
          "Pot 1": "United States (co-host) (14) Mexico (co-host) (15) Canada (co-host) (27) Spain (1) Argentina (2) France (3) England (4) Brazil (5) Portugal (6) Netherlands (7) Belgium (8) Germany (9)",
          "Pot 2": "Croatia (10) Morocco (11) Colombia (13) Uruguay (16) Switzerland (17) Japan (18) Senegal (19) Iran (20) South Korea (22) Ecuador (23) Austria (24) Australia (26)",
          "Pot 3": "Norway (29) Panama (30) Egypt (34) Algeria (35) Scotland (36) Paraguay (39) Tunisia (40) Ivory Coast (42) Uzbekistan (50) Qatar (51) Saudi Arabia (60) South Africa (61)",
          "Pot 4": "Jordan (66) Cape Verde (68) Ghana (72) Curaçao (82) Haiti (84) New Zealand (86) UEFA Path A winners [ O ] UEFA Path B winners [ O ] UEFA Path C winners [ O ] UEFA Path D winners [ O ] IC Path 1 winners [ O ] [ P ] IC Path 2 winners [ O ] [ Q ]"
        }
      ],
      "normalized_text": "Draw\nPots [ N ]\nPot 1 | Pot 2 | Pot 3 | Pot 4\nUnited States (co-host) (14) Mexico (co-host) (15) Canada (co-host) (27) Spain (1) Argentina (2) France (3) England (4) Brazil (5) Portugal (6) Netherlands (7) Belgium (8) Germany (9) | Croatia (10) Morocco (11) Colombia (13) Uruguay (16) Switzerland (17) Japan (18) Senegal (19) Iran (20) South Korea (22) Ecuador (23) Austria (24) Australia (26) | Norway (29) Panama (30) Egypt (34) Algeria (35) Scotland (36) Paraguay (39) Tunisia (40) Ivory Coast (42) Uzbekistan (50) Qatar (51) Saudi Arabia (60) South Africa (61) | Jordan (66) Cape Verde (68) Ghana (72) Curaçao (82) Haiti (84) New Zealand (86) UEFA Path A winners [ O ] UEFA Path B winners [ O ] UEFA Path C winners [ O ] UEFA Path D winners [ O ] IC Path 1 winners [ O ] [ P ] IC Path 2 winners [ O ] [ Q ]",
      "truncated": false
    },
    {
      "table_index": 22,
      "table_type": "wikitable",
      "section_heading": "Sponsorships",
      "caption": "",
      "headers": [
        "FIFA partners",
        "FIFA World Cup sponsors",
        "FIFA World Cup supporters"
      ],
      "rows": [
        [
          "FIFA partners",
          "FIFA World Cup sponsors",
          "FIFA World Cup supporters"
        ],
        [
          "Adidas [ 173 ] Aramco [ 174 ] Coca-Cola [ 175 ] Hyundai – Kia [ 176 ] Lenovo [ 177 ] Qatar Airways [ 178 ] Visa [ 179 ]",
          "AB InBev ( Budweiser + Others ) [ 180 ] American Airlines [ 181 ] Bank of America [ 182 ] Frito-Lay ( Lay's ) [ 183 ] Hisense [ 184 ] McDonald's [ 185 ] Mengniu Dairy [ 186 ] Unilever ( Rexona + Others ) [ 187 ] Verizon [ 188 ]",
          "ADI Predictstreet [ 189 ] DoorDash [ 190 ] Marriott Bonvoy [ 191 ] Rock-it Cargo [ 192 ] Valvoline [ 193 ]"
        ]
      ],
      "row_dicts": [
        {
          "FIFA partners": "Adidas [ 173 ] Aramco [ 174 ] Coca-Cola [ 175 ] Hyundai – Kia [ 176 ] Lenovo [ 177 ] Qatar Airways [ 178 ] Visa [ 179 ]",
          "FIFA World Cup sponsors": "AB InBev ( Budweiser + Others ) [ 180 ] American Airlines [ 181 ] Bank of America [ 182 ] Frito-Lay ( Lay's ) [ 183 ] Hisense [ 184 ] McDonald's [ 185 ] Mengniu Dairy [ 186 ] Unilever ( Rexona + Others ) [ 187 ] Verizon [ 188 ]",
          "FIFA World Cup supporters": "ADI Predictstreet [ 189 ] DoorDash [ 190 ] Marriott Bonvoy [ 191 ] Rock-it Cargo [ 192 ] Valvoline [ 193 ]"
        }
      ],
      "normalized_text": "Sponsorships\nFIFA partners | FIFA World Cup sponsors | FIFA World Cup supporters\nAdidas [ 173 ] Aramco [ 174 ] Coca-Cola [ 175 ] Hyundai – Kia [ 176 ] Lenovo [ 177 ] Qatar Airways [ 178 ] Visa [ 179 ] | AB InBev ( Budweiser + Others ) [ 180 ] American Airlines [ 181 ] Bank of America [ 182 ] Frito-Lay ( Lay's ) [ 183 ] Hisense [ 184 ] McDonald's [ 185 ] Mengniu Dairy [ 186 ] Unilever ( Rexona + Others ) [ 187 ] Verizon [ 188 ] | ADI Predictstreet [ 189 ] DoorDash [ 190 ] Marriott Bonvoy [ 191 ] Rock-it Cargo [ 192 ] Valvoline [ 193 ]",
      "truncated": false
    }
  ]
}
```
