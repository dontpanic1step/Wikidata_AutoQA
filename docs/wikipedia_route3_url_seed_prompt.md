# Route 3 Wikipedia Dump Discovery Prompt

Use this prompt with a strong model when revising the Route 3 dump-discovery subdomain plan. The production seed file should come from `scripts/generate_wikipedia_table_urls.py`, preferably backed by raw pages-articles JSONL produced by `scripts/extract_wikipedia_raw_pages.py` so table and infobox markup is preserved. The URL generator may fall back to title dumps or bounded MediaWiki search for sparse subdomains, but it must open bounded candidates and grade parsed table quality before selecting URLs. Do not hand-pick final Wikipedia URLs as the default path.

```text
You are preparing a diverse dump-discovery plan for a Wikipedia table-based SimpleQA generator.

Goal:
- Produce subdomain matching rules likely to surface Wikipedia pages with stable, structured infoboxes or article tables from raw dump pages, title dumps, or bounded search fallback.
- The downstream generator will create one single fact or table reasoning QA per URL.
- Prefer pages where table rows contain facts that are not trivially repeated in article prose.
- Prefer settled historical or reference pages, not live/current status pages.

Output format:
- Return TSV rows with exactly three columns:
  domain<TAB>subdomain<TAB>required title terms<TAB>bonus title terms<TAB>excluded title terms
- Do not include final URLs; URLs must be discovered from the dump and table-scored by code.
- Do not include markdown tables or commentary in the final TSV block.

Domain plan:
- Use the exact Domain Axis from `docs/template_catalog_review.md`, then add History:
  Architecture and Transportation; Arts and Media; Computer Science and AI; Earth, Environment, and Space; Economy and Business; Education; Engineering and Technology; Food, Agriculture, and Daily Life; Geography; Language and Literature; Life Sciences; Mathematics; Medicine and Health; People; Philosophy and Religion; Physical Sciences; Politics and Law; Society and Culture; Sports and Recreation; History.
- For each domain, produce exactly two subdomains.
- For each subdomain, produce title-matching terms broad enough to find multiple dump candidates.
- Avoid near-duplicate page families. For example, do not fill the set with many annual music chart pages or many editions of the same award.
- In a 40-URL pilot, use 20 domains times 2 subdomains.

Good source patterns:
- List pages with sortable tables.
- Award pages with nominee/winner or count tables.
- Historical election result pages.
- Sports event pages with result, medal, venue, or record tables.
- Architecture, transport, geography, science, and economy list pages with numeric columns.

Bad source patterns:
- Current rankings, live standings, ongoing elections, or pages dominated by current status.
- Pages where the only useful time or number is in the title rather than table cells.
- Tables whose rows are mostly prose notes rather than structured values.
- Page families already represented by another URL in the same batch unless the table structure and domain are substantially different.

False-grounding guardrails:
- Treat table facts as local, bounded facts, not global claims.
- Do not seed pages that invite questions like "In which year did Song X enter the chart?" when the year is only the page title or one local chart slice.
- Prefer pages where a single fact question or table reasoning question can preserve the table scope, metric, unit, and section.

For each title-rule before finalizing:
- Check that the terms can match more than one plausible title/page in a dump slice or all-titles dump.
- Keep terms broad enough that the code, not the prompt, chooses the final page by table score.
- Exclude live/current terms and years at or after the configured cutoff.
```
