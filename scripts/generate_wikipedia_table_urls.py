"""Discover diverse Wikipedia URLs that are likely to contain valuable tables."""

from __future__ import annotations

import argparse
import json
import sys
from dataclasses import asdict, dataclass
from pathlib import Path
from time import perf_counter
from typing import Any
from urllib.parse import quote, urlencode
from urllib.request import Request, urlopen
from urllib.error import HTTPError, URLError

ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "src"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))

from wikidata_simpleqa.config import Settings
from wikidata_simpleqa.network import install_proxy
from wikidata_simpleqa.wikipedia_client import WikipediaClient
from wikidata_simpleqa.wikipedia_infobox_generator import (
    extract_non_table_prose,
    extract_wikipedia_tables,
    rank_wikipedia_tables,
)


DOMAIN_QUERIES: tuple[tuple[str, tuple[str, ...]], ...] = (
    ("Sports", ("championship venues capacity table", "tournament results wikitable")),
    ("Architecture and Transportation", ("railway station ridership table", "airport passenger traffic table")),
    ("Film and Television", ("film festival awards table", "television season ratings table")),
    ("Music", ("album chart positions table", "music awards nominees table")),
    ("Science and Technology", ("space mission instruments table", "minor planet discovery table")),
    ("Geography", ("island area population table", "mountain elevation table")),
    ("Politics and Government", ("election results table constituencies", "referendum results table")),
    ("Business and Economics", ("company fleet table", "economic rankings table")),
    ("Education", ("university rankings table", "college athletics results table")),
    ("Culture and Awards", ("literary awards nominees table", "architecture awards table")),
)

FALLBACK_URLS: tuple[tuple[str, str], ...] = (
    ("Film and Television", "https://en.wikipedia.org/wiki/23rd_Independent_Spirit_Awards"),
    ("Music", "https://en.wikipedia.org/wiki/List_of_UK_top-ten_singles_in_1978"),
    ("Music", "https://en.wikipedia.org/wiki/List_of_UK_top-ten_singles_in_1979"),
    ("Music", "https://en.wikipedia.org/wiki/List_of_UK_top-ten_singles_in_1981"),
    ("Music", "https://en.wikipedia.org/wiki/List_of_UK_top-ten_singles_in_1982"),
    ("Music", "https://en.wikipedia.org/wiki/List_of_UK_top-ten_singles_in_1983"),
    ("Music", "https://en.wikipedia.org/wiki/List_of_Billboard_Hot_100_top-ten_singles_in_1980"),
    ("Music", "https://en.wikipedia.org/wiki/List_of_Billboard_Hot_100_top-ten_singles_in_1982"),
    ("Music", "https://en.wikipedia.org/wiki/List_of_Billboard_Hot_100_top-ten_singles_in_1983"),
    ("Music", "https://en.wikipedia.org/wiki/List_of_Billboard_Hot_100_top-ten_singles_in_1984"),
    ("Music", "https://en.wikipedia.org/wiki/List_of_Billboard_Hot_100_top-ten_singles_in_1981"),
    ("Music", "https://en.wikipedia.org/wiki/List_of_UK_top-ten_singles_in_1980"),
    ("Music", "https://en.wikipedia.org/wiki/List_of_UK_top-ten_singles_in_1984"),
    ("Music", "https://en.wikipedia.org/wiki/List_of_Billboard_Hot_100_top-ten_singles_in_1983"),
    ("Music", "https://en.wikipedia.org/wiki/List_of_Billboard_Hot_100_top-ten_singles_in_1984"),
    ("Film and Television", "https://en.wikipedia.org/wiki/22nd_Independent_Spirit_Awards"),
    ("Film and Television", "https://en.wikipedia.org/wiki/24th_Independent_Spirit_Awards"),
    ("Culture and Awards", "https://en.wikipedia.org/wiki/42nd_Nebula_Awards"),
    ("Culture and Awards", "https://en.wikipedia.org/wiki/43rd_Nebula_Awards"),
    ("Sports", "https://en.wikipedia.org/wiki/2014_World_Junior_Championships_in_Athletics"),
    ("Architecture and Transportation", "https://en.wikipedia.org/wiki/List_of_tallest_buildings_in_Fort_Wayne"),
    ("Science and Technology", "https://en.wikipedia.org/wiki/List_of_impact_craters_in_Europe"),
    ("Geography", "https://en.wikipedia.org/wiki/List_of_National_Natural_Landmarks_in_Alabama"),
    ("Politics and Government", "https://en.wikipedia.org/wiki/2019_Chicago_aldermanic_election"),
    ("Business and Economics", "https://en.wikipedia.org/wiki/List_of_largest_banks_in_Southeast_Asia"),
    ("Education", "https://en.wikipedia.org/wiki/List_of_colleges_and_universities_in_Maine"),
    ("Culture and Awards", "https://en.wikipedia.org/wiki/List_of_public_art_in_Indianapolis"),
    ("Sports", "https://en.wikipedia.org/wiki/2011_World_Weightlifting_Championships"),
    ("Architecture and Transportation", "https://en.wikipedia.org/wiki/List_of_bridges_on_the_National_Register_of_Historic_Places_in_Pennsylvania"),
    ("Science and Technology", "https://en.wikipedia.org/wiki/List_of_observatories"),
    ("Geography", "https://en.wikipedia.org/wiki/List_of_lakes_of_Minnesota"),
    ("Culture and Awards", "https://en.wikipedia.org/wiki/List_of_museums_in_Kentucky"),
)


@dataclass(slots=True)
class UrlCandidate:
    """One discovered URL candidate with table-quality evidence."""

    domain: str
    title: str
    url: str
    best_table_score: float
    best_table_caption: str
    best_table_section: str
    reasons: list[str]
    discovered_by: str


def parse_args() -> argparse.Namespace:
    """Parse CLI arguments."""
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--target-count", type=int, default=10)
    parser.add_argument("--search-limit-per-query", type=int, default=6)
    parser.add_argument("--timeout-seconds", type=float, default=20.0)
    parser.add_argument("--proxy", type=str, default="socks5://127.0.0.1:7897")
    parser.add_argument("--output", type=Path, default=ROOT / "config" / "wikipedia_table_urls.txt")
    parser.add_argument(
        "--summary-output",
        type=Path,
        default=ROOT / "outputs" / "wikipedia_table_url_generation_summary.json",
    )
    return parser.parse_args()


def main() -> int:
    """Discover table-heavy URLs and write a domain-labeled URL file."""
    args = parse_args()
    started = perf_counter()
    proxy = _optional_proxy(args.proxy)
    settings = Settings(target_time="2024", timeout_seconds=args.timeout_seconds, proxy=proxy)
    install_proxy(proxy)
    wikipedia_client = WikipediaClient(
        user_agent=settings.user_agent,
        proxy=proxy,
        timeout_seconds=args.timeout_seconds,
        cache_dir=settings.cache_dir,
    )
    selected: list[UrlCandidate] = []
    seen_urls: set[str] = set()
    for domain, queries in DOMAIN_QUERIES:
        if len(selected) >= args.target_count:
            break
        best = _best_candidate_for_domain(
            domain=domain,
            queries=queries,
            search_limit=args.search_limit_per_query,
            wikipedia_client=wikipedia_client,
            user_agent=settings.user_agent,
            timeout_seconds=args.timeout_seconds,
            seen_urls=seen_urls,
        )
        if best is not None:
            selected.append(best)
            seen_urls.add(best.url)

    for domain, url in FALLBACK_URLS:
        if len(selected) >= args.target_count:
            break
        if url in seen_urls:
            continue
        try:
            candidate = _score_url(
                domain=domain,
                title_or_url=url,
                wikipedia_client=wikipedia_client,
                discovered_by="fallback_seed",
            )
        except (HTTPError, TimeoutError, URLError, OSError):
            candidate = None
        if candidate is not None:
            selected.append(candidate)
            seen_urls.add(candidate.url)

    for domain, url in FALLBACK_URLS:
        if len(selected) >= args.target_count:
            break
        if url in seen_urls:
            continue
        title = url.rsplit("/", 1)[-1].replace("_", " ")
        selected.append(
            UrlCandidate(
                domain=domain,
                title=title,
                url=url,
                best_table_score=0.0,
                best_table_caption="",
                best_table_section="",
                reasons=["unscored_fallback_after_network_limit"],
                discovered_by="fallback_seed_unscored",
            )
        )
        seen_urls.add(url)

    selected = selected[: args.target_count]
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(
        "# domain\turl\n"
        + "\n".join(f"{candidate.domain}\t{candidate.url}" for candidate in selected)
        + "\n",
        encoding="utf-8",
    )
    summary = {
        "target_count": args.target_count,
        "selected_count": len(selected),
        "output": str(args.output),
        "duration_seconds": round(perf_counter() - started, 4),
        "candidates": [asdict(candidate) for candidate in selected],
        "wikipedia_events": wikipedia_client.request_events.copy(),
    }
    args.summary_output.parent.mkdir(parents=True, exist_ok=True)
    args.summary_output.write_text(json.dumps(summary, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    print(json.dumps(summary, indent=2, ensure_ascii=False))
    return 0


def _best_candidate_for_domain(
    *,
    domain: str,
    queries: tuple[str, ...],
    search_limit: int,
    wikipedia_client: WikipediaClient,
    user_agent: str,
    timeout_seconds: float,
    seen_urls: set[str],
) -> UrlCandidate | None:
    """Return the highest-scoring candidate found for one domain."""
    candidates: list[UrlCandidate] = []
    for query in queries:
        for title in _search_wikipedia_titles(query, search_limit, user_agent, timeout_seconds):
            url = "https://en.wikipedia.org/wiki/" + quote(title.replace(" ", "_"), safe=":_()")
            if url in seen_urls:
                continue
            try:
                scored = _score_url(
                    domain=domain,
                    title_or_url=title,
                    wikipedia_client=wikipedia_client,
                    discovered_by=f"mediawiki_search:{query}",
                )
            except (HTTPError, TimeoutError, URLError, OSError):
                scored = None
            if scored is not None:
                candidates.append(scored)
    if not candidates:
        return None
    return max(candidates, key=lambda item: item.best_table_score)


def _search_wikipedia_titles(query: str, limit: int, user_agent: str, timeout_seconds: float) -> list[str]:
    """Search English Wikipedia and return result titles."""
    if limit <= 0:
        return []
    api_url = "https://en.wikipedia.org/w/api.php?" + urlencode(
        {
            "action": "query",
            "list": "search",
            "srsearch": query,
            "srlimit": str(limit),
            "format": "json",
            "formatversion": "2",
        }
    )
    request = Request(api_url, headers={"Accept": "application/json", "User-Agent": user_agent})
    try:
        with urlopen(request, timeout=timeout_seconds) as response:
            payload = json.loads(response.read().decode("utf-8"))
    except (HTTPError, TimeoutError, URLError, OSError):
        return []
    rows = payload.get("query", {}).get("search", []) if isinstance(payload, dict) else []
    return [str(row.get("title", "")).strip() for row in rows if str(row.get("title", "")).strip()]


def _score_url(
    *,
    domain: str,
    title_or_url: str,
    wikipedia_client: WikipediaClient,
    discovered_by: str,
) -> UrlCandidate | None:
    """Score one URL by extracting and ranking its tables."""
    parse_payload = wikipedia_client.fetch_parse(title_or_url)
    parse_body = parse_payload.get("parse", {}) if isinstance(parse_payload, dict) else {}
    title = str(parse_body.get("title", title_or_url)).strip()
    html = str(parse_body.get("text", "")).strip()
    if not title or not html:
        return None
    tables = extract_wikipedia_tables(html)
    if not tables:
        return None
    first_paragraph = ""
    summary = wikipedia_client.fetch_summary(title)
    if isinstance(summary, dict):
        first_paragraph = str(summary.get("extract", "")).strip()
    ranked = rank_wikipedia_tables(
        tables,
        first_paragraph=first_paragraph,
        prose_text=extract_non_table_prose(html),
    )
    if not ranked:
        return None
    best = ranked[0]
    score = float(best.get("score", 0.0) or 0.0)
    if score < 4.0:
        return None
    url = "https://en.wikipedia.org/wiki/" + quote(title.replace(" ", "_"), safe=":_()")
    return UrlCandidate(
        domain=domain,
        title=title,
        url=url,
        best_table_score=score,
        best_table_caption=str(best.get("caption", "") or ""),
        best_table_section=str(best.get("section_heading", "") or ""),
        reasons=[str(reason) for reason in best.get("reasons", [])],
        discovered_by=discovered_by,
    )


def _optional_proxy(value: str) -> str | None:
    """Normalize CLI proxy values."""
    if value.strip().lower() in {"", "none", "direct", "off"}:
        return None
    return value


if __name__ == "__main__":
    raise SystemExit(main())
