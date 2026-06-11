"""Discover diverse Wikipedia table URL seeds from Wikimedia dumps and search."""

from __future__ import annotations

import argparse
import gzip
import json
import re
import sys
from dataclasses import asdict, dataclass
from html import unescape
from pathlib import Path
from time import perf_counter
from typing import Any, Iterable
from urllib.error import HTTPError, URLError
from urllib.parse import quote
from urllib.request import Request, urlopen

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

DEFAULT_TITLE_DUMP_URL = "https://dumps.wikimedia.org/enwiki/latest/enwiki-latest-all-titles-in-ns0.gz"
ENABLE_NUMERIC_PAGE_GRADING_POINTS = False


@dataclass(frozen=True, slots=True)
class SubdomainSpec:
    """One broad domain/subdomain discovery rule over Wikipedia titles."""

    domain: str
    subdomain: str
    required_terms: tuple[str, ...]
    bonus_terms: tuple[str, ...] = ()
    excluded_terms: tuple[str, ...] = ()


@dataclass(slots=True)
class TitleCandidate:
    """One title selected from the dump before table scoring."""

    domain: str
    subdomain: str
    title: str
    title_score: float
    title_reasons: list[str]


@dataclass(slots=True)
class DumpPage:
    """One parsed article page from a local Wikimedia XML dump slice."""

    title: str
    text: str


@dataclass(slots=True)
class UrlCandidate:
    """One URL seed with opening and table-quality evidence."""

    domain: str
    subdomain: str
    title: str
    url: str
    title_score: float
    best_table_score: float
    combined_score: float
    best_table_caption: str
    best_table_section: str
    reasons: list[str]
    discovered_by: str
    open_status: str
    error_message: str = ""


SUBDOMAIN_PLAN: tuple[SubdomainSpec, ...] = (
    SubdomainSpec("Architecture and Transportation", "railway stations", ("railway", "station"), ("metro", "list"), ("power", "generating", "current")),
    SubdomainSpec("Architecture and Transportation", "airports", ("airport",), ("traffic", "list", "passenger"), ("current",)),
    SubdomainSpec("Arts and Media", "film awards", ("film", "award"), ("festival", "ceremony"), ("2025", "2026")),
    SubdomainSpec("Arts and Media", "music charts", ("music", "award"), ("song", "album", "chart", "billboard"), ("2025", "2026")),
    SubdomainSpec("Computer Science and AI", "programming languages", ("programming", "language"), ("comparison", "list"), ()),
    SubdomainSpec("Computer Science and AI", "computing benchmarks", ("computer",), ("benchmark", "machine", "ranking"), ("2025", "2026")),
    SubdomainSpec("Earth, Environment, and Space", "observatories", ("observatory",), ("astronomical", "list"), ()),
    SubdomainSpec("Earth, Environment, and Space", "impact structures", ("impact", "structure"), ("crater", "list"), ("economic", "economies", "market")),
    SubdomainSpec("Economy and Business", "companies", ("company",), ("revenue", "list", "largest"), ("2025", "2026")),
    SubdomainSpec("Economy and Business", "banks", ("bank",), ("assets", "list", "largest"), ("2025", "2026")),
    SubdomainSpec("Education", "universities", ("universit*",), ("list", "ranking", "college"), ("2025", "2026")),
    SubdomainSpec("Education", "schools", ("school",), ("list", "district", "secondary"), ("2025", "2026", "album", "song", "film")),
    SubdomainSpec("Engineering and Technology", "bridges", ("bridge",), ("span", "list", "longest"), ()),
    SubdomainSpec("Engineering and Technology", "dams", ("dam",), ("list", "largest", "hydroelectric"), ()),
    SubdomainSpec(
        "Food, Agriculture, and Daily Life",
        "crop production",
        ("production",),
        ("crop", "cereal", "wheat", "rice", "agriculture"),
        ("2025", "2026", "productions", "film", "television", "album", "company"),
    ),
    SubdomainSpec("Food, Agriculture, and Daily Life", "wine regions", ("wine",), ("production", "regions", "list"), ("2025", "2026")),
    SubdomainSpec("Geography", "lakes", ("lake",), ("list", "area", "depth"), ("bridge", "school", "church", "facility", "airport", "constituency", "district")),
    SubdomainSpec("Geography", "islands", ("island",), ("list", "area", "population"), ("league", "party", "tour", "championship")),
    SubdomainSpec("Language and Literature", "literary awards", ("book", "award"), ("literary", "novel"), ("2025", "2026")),
    SubdomainSpec("Language and Literature", "books", ("book",), ("list", "award", "novel"), ("2025", "2026")),
    SubdomainSpec("Life Sciences", "birds", ("bird",), ("list", "population", "species"), ()),
    SubdomainSpec("Life Sciences", "mammals", ("mammal",), ("list", "largest", "species"), ()),
    SubdomainSpec("Mathematics", "polyhedra", ("polyhed*",), ("list", "uniform", "regular"), ()),
    SubdomainSpec("Mathematics", "mathematical constants", ("constant",), ("mathematical", "list"), ()),
    SubdomainSpec("Medicine and Health", "hospitals", ("hospital",), ("list", "beds", "opened"), ()),
    SubdomainSpec("Medicine and Health", "epidemics", ("epidemic",), ("pandemic", "list", "outbreak"), ("2025", "2026")),
    SubdomainSpec("People", "laureates", ("laureate",), ("nobel", "list", "award"), ()),
    SubdomainSpec("People", "award records", ("award", "record"), ("academy", "list"), ("football", "sports")),
    SubdomainSpec("Philosophy and Religion", "popes", ("pope",), ("list", "papacy"), ()),
    SubdomainSpec("Philosophy and Religion", "religion demographics", ("religion",), ("demographics", "adherents", "census"), ("2025", "2026")),
    SubdomainSpec("Physical Sciences", "chemical elements", ("chemical", "element"), ("list", "density"), ()),
    SubdomainSpec("Physical Sciences", "stars", ("star",), ("nearest", "list", "distance", "astronomical"), ("season", "music", "show")),
    SubdomainSpec("Politics and Law", "elections", ("election",), ("results", "ward", "general"), ("2025", "2026")),
    SubdomainSpec("Politics and Law", "court cases", ("case",), ("court", "reports", "supreme"), ()),
    SubdomainSpec("Society and Culture", "museums", ("museum",), ("list", "county", "state"), ()),
    SubdomainSpec("Society and Culture", "public art", ("public", "art"), ("list", "sculpture"), ()),
    SubdomainSpec("Sports and Recreation", "championship results", ("championship",), ("athletics", "results", "medal"), ("2025", "2026")),
    SubdomainSpec("Sports and Recreation", "stadiums", ("stadium",), ("capacity", "list", "venue"), ("2025", "2026")),
    SubdomainSpec("History", "battles", ("battle",), ("casualties", "list", "siege"), ("manga", "album", "song", "film")),
    SubdomainSpec("History", "empires", ("empire",), ("largest", "list", "area"), ()),
)


def parse_args() -> argparse.Namespace:
    """Parse CLI arguments."""
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--target-count", type=int, default=40)
    parser.add_argument("--domain-limit", type=int, default=0, help="Limit broad domains before subdomain expansion; 0 means all.")
    parser.add_argument("--subdomains-per-domain", type=int, default=2)
    parser.add_argument("--urls-per-subdomain", type=int, default=1)
    parser.add_argument(
        "--best-subdomain-per-domain",
        action="store_true",
        help="Score the selected subdomains, then keep only the best one per broad domain.",
    )
    parser.add_argument("--timeout-seconds", type=float, default=20.0)
    parser.add_argument("--proxy", type=str, default="none")
    parser.add_argument("--min-table-score", type=float, default=0.0)
    parser.add_argument("--dump-url", type=str, default=DEFAULT_TITLE_DUMP_URL)
    parser.add_argument("--dump-title-path", type=Path, default=ROOT / "cache" / "wikipedia_dumps" / "enwiki-latest-all-titles-in-ns0.gz")
    parser.add_argument("--page-dump-dir", type=Path, default=None, help="Directory containing pages-articles XML .bz2 slices or recovered blocks.")
    parser.add_argument("--page-dump-file", action="append", type=Path, default=[], help="One pages-articles XML .bz2 slice. Can be repeated.")
    parser.add_argument("--page-jsonl-file", action="append", type=Path, default=[], help="Raw extracted page JSONL with title/text fields. Can be repeated.")
    parser.add_argument(
        "--source-mode",
        choices=("auto", "page-dump", "title-dump"),
        default="auto",
        help="Use local page dumps when provided; otherwise fall back to title-dump discovery.",
    )
    parser.add_argument("--no-download", action="store_true", help="Require --dump-title-path to already exist.")
    parser.add_argument("--download-retries", type=int, default=3)
    parser.add_argument("--title-candidates-per-subdomain", type=int, default=80)
    parser.add_argument("--score-candidates-per-subdomain", type=int, default=8)
    parser.add_argument(
        "--search-fallback-results",
        type=int,
        default=0,
        help="MediaWiki search results to add for each incomplete subdomain; 0 disables search fallback.",
    )
    parser.add_argument(
        "--search-fallback-queries-per-subdomain",
        type=int,
        default=2,
        help="Bounded number of MediaWiki search queries per incomplete subdomain.",
    )
    parser.add_argument("--cutoff-year", type=int, default=2025)
    parser.add_argument("--output", type=Path, default=ROOT / "config" / "wikipedia_table_urls.txt")
    parser.add_argument(
        "--summary-output",
        type=Path,
        default=ROOT / "outputs" / "wikipedia_table_url_generation_summary.json",
    )
    return parser.parse_args()


def main() -> int:
    """Discover, score, and write a domain/subdomain-labeled URL seed file."""
    args = parse_args()
    started = perf_counter()
    proxy = _optional_proxy(args.proxy)
    settings = Settings(target_time="2024", timeout_seconds=args.timeout_seconds, proxy=proxy)
    install_proxy(proxy)
    specs = selected_specs(
        SUBDOMAIN_PLAN,
        domain_limit=args.domain_limit,
        subdomains_per_domain=args.subdomains_per_domain,
    )
    page_dump_paths = page_dump_files(args.page_dump_file, args.page_dump_dir)
    page_jsonl_paths = [path for path in args.page_jsonl_file if path.exists()]
    source_mode = args.source_mode
    if source_mode == "auto":
        source_mode = "page-dump" if page_dump_paths or page_jsonl_paths else "title-dump"
    dump_path: Path | None = None
    page_dump_stats: dict[str, Any] = {}
    if source_mode == "page-dump":
        if not page_dump_paths and not page_jsonl_paths:
            raise ValueError("Provide --page-dump-file, --page-dump-dir, or --page-jsonl-file when --source-mode page-dump is used.")
        title_candidates, page_dump_stats = collect_page_dump_candidates(
            page_dump_paths,
            page_jsonl_paths=page_jsonl_paths,
            specs=specs,
            per_subdomain=args.title_candidates_per_subdomain,
            cutoff_year=args.cutoff_year,
        )
    else:
        dump_path = ensure_title_dump(
            dump_url=args.dump_url,
            dump_path=args.dump_title_path,
            user_agent=settings.user_agent,
            timeout_seconds=args.timeout_seconds,
            download=not args.no_download,
            retries=args.download_retries,
        )
        title_candidates = collect_title_candidates(
            dump_path,
            specs=specs,
            per_subdomain=args.title_candidates_per_subdomain,
            cutoff_year=args.cutoff_year,
        )
    search_fallback_stats: dict[str, Any] = {}
    if args.search_fallback_results > 0:
        search_fallback_stats = add_search_fallback_candidates(
            title_candidates,
            specs=specs,
            per_subdomain=args.title_candidates_per_subdomain,
            min_needed=max(args.score_candidates_per_subdomain, args.urls_per_subdomain),
            user_agent=settings.user_agent,
            timeout_seconds=args.timeout_seconds,
            fallback_results=args.search_fallback_results,
            queries_per_subdomain=args.search_fallback_queries_per_subdomain,
            cutoff_year=args.cutoff_year,
        )
    wikipedia_client = WikipediaClient(
        user_agent=settings.user_agent,
        proxy=proxy,
        timeout_seconds=args.timeout_seconds,
        cache_dir=settings.cache_dir,
    )
    if args.best_subdomain_per_domain:
        selected, failures = select_best_subdomain_urls(
            specs,
            title_candidates,
            wikipedia_client=wikipedia_client,
            min_table_score=args.min_table_score,
            score_candidates_per_subdomain=args.score_candidates_per_subdomain,
            urls_per_subdomain=args.urls_per_subdomain,
            target_count=args.target_count,
        )
    else:
        selected, failures = select_urls_in_spec_order(
            specs,
            title_candidates,
            wikipedia_client=wikipedia_client,
            min_table_score=args.min_table_score,
            score_candidates_per_subdomain=args.score_candidates_per_subdomain,
            urls_per_subdomain=args.urls_per_subdomain,
            target_count=args.target_count,
        )

    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(
        "# domain\tsubdomain\turl\n"
        + "\n".join(f"{row.domain}\t{row.subdomain}\t{row.url}" for row in selected)
        + "\n",
        encoding="utf-8",
    )
    summary = {
        "target_count": args.target_count,
        "domain_limit": args.domain_limit,
        "subdomains_per_domain": args.subdomains_per_domain,
        "urls_per_subdomain": args.urls_per_subdomain,
        "best_subdomain_per_domain": args.best_subdomain_per_domain,
        "dump_url": args.dump_url,
        "source_mode": source_mode,
        "dump_title_path": str(dump_path) if dump_path is not None else "",
        "page_dump_files": [str(path) for path in page_dump_paths],
        "page_jsonl_files": [str(path) for path in page_jsonl_paths],
        "page_dump_stats": page_dump_stats,
        "search_fallback_stats": search_fallback_stats,
        "selected_count": len(selected),
        "failed_count": len(failures),
        "output": str(args.output),
        "duration_seconds": round(perf_counter() - started, 4),
        "candidates": [asdict(candidate) for candidate in selected],
        "failed_subdomains": failures,
        "title_candidate_counts": {
            f"{domain} / {subdomain}": len(candidates)
            for (domain, subdomain), candidates in title_candidates.items()
        },
        "wikipedia_events": wikipedia_client.request_events.copy(),
    }
    args.summary_output.parent.mkdir(parents=True, exist_ok=True)
    args.summary_output.write_text(json.dumps(summary, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    _print_json(summary)
    return 0


def select_urls_in_spec_order(
    specs: list[SubdomainSpec],
    title_candidates: dict[tuple[str, str], list[TitleCandidate]],
    *,
    wikipedia_client: WikipediaClient,
    min_table_score: float,
    score_candidates_per_subdomain: int,
    urls_per_subdomain: int,
    target_count: int,
) -> tuple[list[UrlCandidate], list[dict[str, Any]]]:
    """Score subdomains in plan order and keep top URLs from each one."""
    selected: list[UrlCandidate] = []
    failures: list[dict[str, Any]] = []
    seen_urls: set[str] = set()
    for spec in specs:
        if len(selected) >= target_count:
            break
        candidates = title_candidates.get((spec.domain, spec.subdomain), [])
        scored = score_subdomain_candidates(
            candidates[:score_candidates_per_subdomain],
            wikipedia_client=wikipedia_client,
            min_table_score=min_table_score,
            seen_urls=seen_urls,
        )
        if not scored:
            failures.append(_failed_subdomain_row(spec, candidates, score_candidates_per_subdomain))
            continue
        added = 0
        for row in scored:
            if len(selected) >= target_count or added >= urls_per_subdomain:
                break
            selected.append(row)
            seen_urls.add(row.url)
            added += 1
    return selected, failures


def select_best_subdomain_urls(
    specs: list[SubdomainSpec],
    title_candidates: dict[tuple[str, str], list[TitleCandidate]],
    *,
    wikipedia_client: WikipediaClient,
    min_table_score: float,
    score_candidates_per_subdomain: int,
    urls_per_subdomain: int,
    target_count: int,
) -> tuple[list[UrlCandidate], list[dict[str, Any]]]:
    """Choose one scored subdomain per broad domain and keep its top URLs."""
    scored_by_key: dict[tuple[str, str], list[UrlCandidate]] = {}
    failures: list[dict[str, Any]] = []
    domain_order: list[str] = []
    specs_by_domain: dict[str, list[SubdomainSpec]] = {}
    for spec in specs:
        if spec.domain not in specs_by_domain:
            domain_order.append(spec.domain)
            specs_by_domain[spec.domain] = []
        specs_by_domain[spec.domain].append(spec)
        candidates = title_candidates.get((spec.domain, spec.subdomain), [])
        scored = score_subdomain_candidates(
            candidates[:score_candidates_per_subdomain],
            wikipedia_client=wikipedia_client,
            min_table_score=min_table_score,
            seen_urls=set(),
        )
        scored_by_key[(spec.domain, spec.subdomain)] = scored
        if not scored:
            failures.append(_failed_subdomain_row(spec, candidates, score_candidates_per_subdomain))

    selected: list[UrlCandidate] = []
    seen_urls: set[str] = set()
    for domain in domain_order:
        if len(selected) >= target_count:
            break
        domain_specs = specs_by_domain[domain]
        best_spec = max(
            domain_specs,
            key=lambda spec: _subdomain_selection_score(
                scored_by_key.get((spec.domain, spec.subdomain), []),
                urls_per_subdomain=urls_per_subdomain,
            ),
        )
        scored = scored_by_key.get((best_spec.domain, best_spec.subdomain), [])
        if not scored:
            continue
        added = 0
        for row in scored:
            if row.url in seen_urls:
                continue
            if len(selected) >= target_count or added >= urls_per_subdomain:
                break
            selected.append(row)
            seen_urls.add(row.url)
            added += 1
    return selected, failures


def _subdomain_selection_score(scored: list[UrlCandidate], *, urls_per_subdomain: int) -> tuple[int, float, float]:
    """Rank subdomains by completeness and aggregate table quality."""
    top = scored[:urls_per_subdomain]
    complete = 1 if len(top) >= urls_per_subdomain else 0
    combined = sum(row.combined_score for row in top)
    table_score = sum(row.best_table_score for row in top)
    return complete, combined, table_score


def _failed_subdomain_row(
    spec: SubdomainSpec,
    candidates: list[TitleCandidate],
    score_candidates_per_subdomain: int,
) -> dict[str, Any]:
    """Return a compact failed-subdomain audit row."""
    return {
        "domain": spec.domain,
        "subdomain": spec.subdomain,
        "reason": "no_dump_or_search_title_candidate_with_tables",
        "candidate_titles": [candidate.title for candidate in candidates[:score_candidates_per_subdomain]],
    }


def ensure_title_dump(
    *,
    dump_url: str,
    dump_path: Path,
    user_agent: str,
    timeout_seconds: float,
    download: bool,
    retries: int = 3,
) -> Path:
    """Return a local Wikimedia title dump, downloading it when requested."""
    if dump_path.exists() and dump_path.stat().st_size > 0:
        return dump_path
    if not download:
        raise FileNotFoundError(f"Missing title dump: {dump_path}")
    dump_path.parent.mkdir(parents=True, exist_ok=True)
    part_path = dump_path.with_suffix(dump_path.suffix + ".part")
    last_error: Exception | None = None
    for _attempt in range(max(1, retries)):
        try:
            resume_at = part_path.stat().st_size if part_path.exists() else 0
            headers = {"User-Agent": user_agent}
            if resume_at:
                headers["Range"] = f"bytes={resume_at}-"
            request = Request(dump_url, headers=headers)
            mode = "ab" if resume_at else "wb"
            with urlopen(request, timeout=timeout_seconds) as response:
                if resume_at and getattr(response, "status", 200) == 200:
                    mode = "wb"
                with part_path.open(mode) as handle:
                    while True:
                        chunk = response.read(1024 * 1024)
                        if not chunk:
                            break
                        handle.write(chunk)
            part_path.replace(dump_path)
            return dump_path
        except (HTTPError, TimeoutError, URLError, OSError) as exc:
            last_error = exc
            continue
    if last_error is not None:
        raise last_error
    part_path.replace(dump_path)
    return dump_path


def selected_specs(
    specs: tuple[SubdomainSpec, ...],
    *,
    domain_limit: int,
    subdomains_per_domain: int,
) -> list[SubdomainSpec]:
    """Select specs in catalog domain order."""
    selected: list[SubdomainSpec] = []
    domain_counts: dict[str, int] = {}
    domain_seen: list[str] = []
    for spec in specs:
        if spec.domain not in domain_counts:
            if domain_limit and len(domain_seen) >= domain_limit:
                continue
            domain_seen.append(spec.domain)
            domain_counts[spec.domain] = 0
        if domain_counts[spec.domain] >= subdomains_per_domain:
            continue
        selected.append(spec)
        domain_counts[spec.domain] += 1
    return selected


def collect_title_candidates(
    dump_path: Path,
    *,
    specs: list[SubdomainSpec],
    per_subdomain: int,
    cutoff_year: int,
) -> dict[tuple[str, str], list[TitleCandidate]]:
    """Collect high-scoring title candidates from a gzipped all-titles dump."""
    buckets: dict[tuple[str, str], list[TitleCandidate]] = {(spec.domain, spec.subdomain): [] for spec in specs}
    spec_index = build_spec_index(specs)
    for title in iter_title_dump(dump_path):
        if not is_article_title_candidate(title, cutoff_year=cutoff_year):
            continue
        normalized = normalize_title_text(title)
        tokens = normalized.split()
        for spec in matching_specs(normalized, tokens, spec_index):
            score, reasons = score_title_for_spec(title, spec, cutoff_year=cutoff_year)
            if score <= 0:
                continue
            key = (spec.domain, spec.subdomain)
            _push_top_candidate(
                buckets[key],
                TitleCandidate(spec.domain, spec.subdomain, title, score, reasons),
                limit=per_subdomain,
            )
    for key, candidates in buckets.items():
        candidates.sort(key=lambda candidate: (-candidate.title_score, candidate.title))
    return buckets


def page_dump_files(cli_paths: list[Path], dump_dir: Path | None) -> list[Path]:
    """Return local page-dump files in deterministic order."""
    paths = [path for path in cli_paths if path.exists()]
    if dump_dir is not None and dump_dir.exists():
        paths.extend(sorted(dump_dir.glob("*.bz2")))
    seen: set[Path] = set()
    deduped: list[Path] = []
    for path in paths:
        resolved = path.resolve()
        if resolved in seen:
            continue
        seen.add(resolved)
        deduped.append(path)
    return deduped


def collect_page_dump_candidates(
    dump_paths: list[Path],
    *,
    page_jsonl_paths: list[Path] | None = None,
    specs: list[SubdomainSpec],
    per_subdomain: int,
    cutoff_year: int,
) -> tuple[dict[tuple[str, str], list[TitleCandidate]], dict[str, Any]]:
    """Collect high-scoring candidates from local pages-articles dump slices."""
    buckets: dict[tuple[str, str], list[TitleCandidate]] = {(spec.domain, spec.subdomain): [] for spec in specs}
    spec_index = build_spec_index(specs)
    stats = {
        "files_seen": 0,
        "jsonl_files_seen": 0,
        "files_with_errors": [],
        "pages_seen": 0,
        "article_pages_seen": 0,
        "table_like_pages_seen": 0,
    }
    for dump_path in dump_paths:
        stats["files_seen"] += 1
        try:
            pages = iter_page_dump(dump_path)
            for page in pages:
                stats["pages_seen"] += 1
                if not is_article_title_candidate(page.title, cutoff_year=cutoff_year):
                    continue
                stats["article_pages_seen"] += 1
                page_score, page_reasons = score_page_text(page.text)
                if page_score <= 0:
                    continue
                stats["table_like_pages_seen"] += 1
                normalized = normalize_title_text(page.title)
                tokens = normalized.split()
                for spec in matching_specs(normalized, tokens, spec_index):
                    title_score, title_reasons = score_title_for_spec(page.title, spec, cutoff_year=cutoff_year)
                    if title_score <= 0:
                        continue
                    key = (spec.domain, spec.subdomain)
                    _push_top_candidate(
                        buckets[key],
                        TitleCandidate(
                            spec.domain,
                            spec.subdomain,
                            page.title,
                            round(title_score + page_score, 4),
                            [*title_reasons, *page_reasons],
                        ),
                        limit=per_subdomain,
                    )
        except (OSError, EOFError, UnicodeError) as exc:
            stats["files_with_errors"].append({"path": str(dump_path), "error": str(exc)})
    for jsonl_path in page_jsonl_paths or []:
        stats["jsonl_files_seen"] += 1
        try:
            for page in iter_page_jsonl(jsonl_path):
                stats["pages_seen"] += 1
                if not is_article_title_candidate(page.title, cutoff_year=cutoff_year):
                    continue
                stats["article_pages_seen"] += 1
                page_score, page_reasons = score_page_text(page.text)
                if page_score <= 0:
                    continue
                stats["table_like_pages_seen"] += 1
                normalized = normalize_title_text(page.title)
                tokens = normalized.split()
                for spec in matching_specs(normalized, tokens, spec_index):
                    title_score, title_reasons = score_title_for_spec(page.title, spec, cutoff_year=cutoff_year)
                    if title_score <= 0:
                        continue
                    key = (spec.domain, spec.subdomain)
                    _push_top_candidate(
                        buckets[key],
                        TitleCandidate(
                            spec.domain,
                            spec.subdomain,
                            page.title,
                            round(title_score + page_score, 4),
                            [*title_reasons, *page_reasons],
                        ),
                        limit=per_subdomain,
                    )
        except (OSError, UnicodeError, json.JSONDecodeError) as exc:
            stats["files_with_errors"].append({"path": str(jsonl_path), "error": str(exc)})
    for candidates in buckets.values():
        candidates.sort(key=lambda candidate: (-candidate.title_score, candidate.title))
    return buckets, stats


def add_search_fallback_candidates(
    buckets: dict[tuple[str, str], list[TitleCandidate]],
    *,
    specs: list[SubdomainSpec],
    per_subdomain: int,
    min_needed: int,
    user_agent: str,
    timeout_seconds: float,
    fallback_results: int,
    queries_per_subdomain: int,
    cutoff_year: int,
) -> dict[str, Any]:
    """Add MediaWiki search titles for subdomains with too few dump candidates."""
    stats: dict[str, Any] = {
        "enabled": True,
        "fallback_results": fallback_results,
        "queries_per_subdomain": queries_per_subdomain,
        "subdomains_considered": 0,
        "search_queries": 0,
        "titles_added": 0,
        "errors": [],
    }
    seen_titles = {
        normalize_title_text(candidate.title)
        for candidates in buckets.values()
        for candidate in candidates
    }
    for spec in specs:
        key = (spec.domain, spec.subdomain)
        if len(buckets.get(key, [])) >= min_needed:
            continue
        stats["subdomains_considered"] += 1
        for query in fallback_queries_for_spec(spec)[: max(1, queries_per_subdomain)]:
            stats["search_queries"] += 1
            try:
                titles = search_wikipedia_titles(
                    query,
                    user_agent=user_agent,
                    timeout_seconds=timeout_seconds,
                    limit=fallback_results,
                )
            except (HTTPError, TimeoutError, URLError, OSError, json.JSONDecodeError) as exc:
                stats["errors"].append({"domain": spec.domain, "subdomain": spec.subdomain, "query": query, "error": str(exc)})
                continue
            for title in titles:
                normalized_title = normalize_title_text(title)
                if normalized_title in seen_titles:
                    continue
                if not is_article_title_candidate(title, cutoff_year=cutoff_year):
                    continue
                score, reasons = score_title_for_spec(title, spec, cutoff_year=cutoff_year)
                if score <= 0:
                    continue
                seen_titles.add(normalized_title)
                _push_top_candidate(
                    buckets[key],
                    TitleCandidate(
                        spec.domain,
                        spec.subdomain,
                        title,
                        round(score + 0.5, 4),
                        [*reasons, "mediawiki_search_fallback"],
                    ),
                    limit=per_subdomain,
                )
                stats["titles_added"] += 1
    for candidates in buckets.values():
        candidates.sort(key=lambda candidate: (-candidate.title_score, candidate.title))
    return stats


def fallback_queries_for_spec(spec: SubdomainSpec) -> list[str]:
    """Return concise, reusable MediaWiki search queries for one subdomain."""
    required = " ".join(term.rstrip("*") for term in spec.required_terms)
    bonus = " ".join(term.rstrip("*") for term in spec.bonus_terms[:3])
    return [
        f'"list of" "{spec.subdomain}"',
        f"{spec.subdomain} {bonus}".strip(),
        f"{required} {bonus}".strip(),
    ]


def search_wikipedia_titles(
    query: str,
    *,
    user_agent: str,
    timeout_seconds: float,
    limit: int,
) -> list[str]:
    """Search English Wikipedia article titles through the MediaWiki API."""
    from urllib.parse import urlencode

    params = urlencode(
        {
            "action": "query",
            "list": "search",
            "srsearch": query,
            "srlimit": max(1, min(50, int(limit))),
            "format": "json",
            "formatversion": "2",
        }
    )
    request = Request(
        f"https://en.wikipedia.org/w/api.php?{params}",
        headers={"User-Agent": user_agent},
    )
    with urlopen(request, timeout=timeout_seconds) as response:
        payload = json.loads(response.read().decode("utf-8"))
    rows = payload.get("query", {}).get("search", [])
    if not isinstance(rows, list):
        return []
    return [
        str(row.get("title", "")).replace("_", " ").strip()
        for row in rows
        if isinstance(row, dict) and str(row.get("title", "")).strip()
    ]


def iter_page_dump(dump_path: Path) -> Iterable[DumpPage]:
    """Yield complete pages from a Wikimedia pages-articles XML bz2 slice or recovered block."""
    inside = False
    parts: list[str] = []
    with bz2_open_text(dump_path) as handle:
        for line in handle:
            if "<page>" in line:
                inside = True
                parts = [line[line.find("<page>") :]]
                if "</page>" in line:
                    page = page_from_xml("".join(parts))
                    if page is not None:
                        yield page
                    inside = False
                    parts = []
                continue
            if not inside:
                continue
            parts.append(line)
            if "</page>" in line:
                page = page_from_xml("".join(parts))
                if page is not None:
                    yield page
                inside = False
                parts = []


def iter_page_jsonl(path: Path) -> Iterable[DumpPage]:
    """Yield raw page records from JSONL created by the local slice extractor."""
    with path.open("r", encoding="utf-8", errors="replace") as handle:
        for line in handle:
            if not line.strip():
                continue
            payload = json.loads(line)
            title = str(payload.get("title", "")).strip()
            text = str(payload.get("text", ""))
            if title and text:
                yield DumpPage(title=title, text=text)


def bz2_open_text(path: Path):
    """Open one bz2 path as text."""
    import bz2

    return bz2.open(path, "rt", encoding="utf-8", errors="replace")


def page_from_xml(page_xml: str) -> DumpPage | None:
    """Extract title and wikitext from one XML page block."""
    title_match = re.search(r"<title>(.*?)</title>", page_xml, flags=re.DOTALL)
    ns_match = re.search(r"<ns>(.*?)</ns>", page_xml, flags=re.DOTALL)
    if not title_match or not ns_match or ns_match.group(1).strip() != "0":
        return None
    if "<redirect " in page_xml:
        return None
    text_match = re.search(r"<text\b[^>]*>(.*?)</text>", page_xml, flags=re.DOTALL)
    if not text_match:
        return None
    title = unescape(title_match.group(1).strip()).replace("_", " ")
    text = unescape(text_match.group(1))
    return DumpPage(title=title, text=text)


def score_page_text(text: str) -> tuple[float, list[str]]:
    """Score page wikitext for likely structured table value."""
    lowered = text.lower()
    table_count = text.count("{|")
    infobox_count = lowered.count("{{infobox")
    if table_count <= 0 and infobox_count <= 0:
        return 0.0, []
    score = 0.0
    reasons: list[str] = []
    if table_count:
        score += min(4.0, table_count * 0.8)
        reasons.append(f"wikitext_tables:{table_count}")
    if "wikitable" in lowered:
        score += 2.0
        reasons.append("wikitable_marker")
    if "sortable" in lowered:
        score += 1.0
        reasons.append("sortable_marker")
    if infobox_count:
        score += min(1.5, infobox_count * 0.5)
        reasons.append(f"infobox_marker:{infobox_count}")
    if ENABLE_NUMERIC_PAGE_GRADING_POINTS and re.search(r"\|\s*(?:capacity|population|area|height|length|votes?|rank|date|year|total|score)\s*=", lowered):
        score += 1.0
        reasons.append("comparable_infobox_field")
    if ENABLE_NUMERIC_PAGE_GRADING_POINTS and re.search(r"!\s*(?:capacity|population|area|height|length|votes?|rank|date|year|total|score)", lowered):
        score += 1.5
        reasons.append("comparable_table_header")
    if len(text) > 250_000:
        score -= 1.5
        reasons.append("large_page_penalty")
    return max(0.0, score), reasons


def iter_title_dump(dump_path: Path) -> Iterable[str]:
    """Yield article titles from a gzipped Wikimedia all-titles dump."""
    with gzip.open(dump_path, "rt", encoding="utf-8", errors="replace") as handle:
        for line in handle:
            title = line.strip()
            if title:
                yield title.replace("_", " ")


def is_article_title_candidate(title: str, *, cutoff_year: int) -> bool:
    """Return whether a title is worth scoring as a table source candidate."""
    normalized = normalize_title_text(title)
    if not normalized or len(normalized) < 4:
        return False
    if ":" in title:
        return False
    if any(token in normalized for token in ("disambiguation", "outline of", "index of", "template", "category")):
        return False
    if _text_has_cutoff_year(title, cutoff_year):
        return False
    return True


def score_title_for_spec(title: str, spec: SubdomainSpec, *, cutoff_year: int) -> tuple[float, list[str]]:
    """Score one dump title for one subdomain."""
    normalized = normalize_title_text(title)
    tokens = normalized.split()
    if any(term_matches(normalized, tokens, term) for term in spec.excluded_terms):
        return 0.0, []
    if not all(term_matches(normalized, tokens, term) for term in spec.required_terms):
        return 0.0, []
    score = 1.0
    reasons = ["required_terms"]
    for term in spec.bonus_terms:
        if term_matches(normalized, tokens, term):
            score += 1.0
            reasons.append(f"bonus:{term}")
    if normalized.startswith("list of "):
        score += 2.5
        reasons.append("list_title")
    if re.search(r"\b(?:in|of)\s+[a-z][a-z]+", normalized):
        score += 1.5
        reasons.append("scoped_title")
    if re.search(r"\b(1[6-9]\d{2}|20[0-1]\d|202[0-4])\b", normalized):
        score += 1.0
        reasons.append("historical_year")
    token_count = len(normalized.split())
    if 5 <= token_count <= 12:
        score += 1.0
        reasons.append("specific_length")
    if "(" in title and ")" in title:
        score += 0.5
        reasons.append("disambiguated_title")
    if any(phrase in normalized for phrase in ("list of countries by", "list of largest", "world record")):
        score -= 2.0
        reasons.append("short_tail_penalty")
    if _text_has_cutoff_year(title, cutoff_year):
        return 0.0, []
    return score, reasons


def score_subdomain_candidates(
    candidates: list[TitleCandidate],
    *,
    wikipedia_client: WikipediaClient,
    min_table_score: float,
    seen_urls: set[str],
) -> list[UrlCandidate]:
    """Score dump-derived titles by parsed Wikipedia table quality."""
    scored: list[UrlCandidate] = []
    for candidate in candidates:
        try:
            url_candidate = score_url_candidate(
                candidate,
                wikipedia_client=wikipedia_client,
            )
        except (HTTPError, TimeoutError, URLError, OSError, ValueError, json.JSONDecodeError):
            continue
        if url_candidate is None:
            continue
        if url_candidate.url in seen_urls:
            continue
        if url_candidate.best_table_score < min_table_score:
            continue
        scored.append(url_candidate)
    scored.sort(key=lambda row: (-row.combined_score, row.title))
    return scored


def score_url_candidate(
    candidate: TitleCandidate,
    *,
    wikipedia_client: WikipediaClient,
) -> UrlCandidate | None:
    """Score one title by extracting and ranking its tables."""
    parse_payload = wikipedia_client.fetch_parse(candidate.title)
    parse_body = parse_payload.get("parse", {}) if isinstance(parse_payload, dict) else {}
    title = str(parse_body.get("title", candidate.title)).strip()
    html = str(parse_body.get("text", "")).strip()
    if not title or not html:
        return None
    tables = extract_wikipedia_tables(html, page_title=title)
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
    table_score = float(best.get("score", 0.0) or 0.0)
    combined_score = round(table_score + candidate.title_score * 0.35, 4)
    url = "https://en.wikipedia.org/wiki/" + quote(title.replace(" ", "_"), safe=":_(),")
    return UrlCandidate(
        domain=candidate.domain,
        subdomain=candidate.subdomain,
        title=title,
        url=url,
        title_score=candidate.title_score,
        best_table_score=table_score,
        combined_score=combined_score,
        best_table_caption=str(best.get("caption", "") or ""),
        best_table_section=str(best.get("section_heading", "") or ""),
        reasons=[*candidate.title_reasons, *[str(reason) for reason in best.get("reasons", [])]],
        discovered_by="wikipedia_dump_or_search_scored",
        open_status="opened",
    )


def _push_top_candidate(candidates: list[TitleCandidate], candidate: TitleCandidate, *, limit: int) -> None:
    """Keep only the highest-scoring candidates in a small in-memory bucket."""
    candidates.append(candidate)
    if len(candidates) <= limit:
        return
    candidates.sort(key=lambda row: (-row.title_score, row.title))
    del candidates[limit:]


def build_spec_index(specs: list[SubdomainSpec]) -> dict[str, list[SubdomainSpec]]:
    """Build a token index for efficient subdomain rule matching."""
    index: dict[str, list[SubdomainSpec]] = {}
    for spec in specs:
        for token in spec.required_terms:
            key = spec_index_key(token)
            if key:
                index.setdefault(key, []).append(spec)
    return index


def spec_index_key(term: str) -> str:
    """Return the normalized index key for a required term."""
    cleaned = term.lower().strip()
    if not cleaned:
        return ""
    if " " in cleaned:
        return cleaned.split()[0].rstrip("*")
    return cleaned.rstrip("*")


def matching_specs(
    normalized: str,
    tokens: list[str],
    spec_index: dict[str, list[SubdomainSpec]],
) -> list[SubdomainSpec]:
    """Return subdomain specs whose indexed required token could match this title."""
    candidates: dict[tuple[str, str], SubdomainSpec] = {}
    for token in tokens:
        for key, specs in spec_index.items():
            if token == key or token.startswith(key):
                for spec in specs:
                    candidates[(spec.domain, spec.subdomain)] = spec
    return [
        spec
        for spec in candidates.values()
        if all(term_matches(normalized, tokens, term) for term in spec.required_terms)
    ]


def normalize_title_text(title: str) -> str:
    """Normalize a title for simple dump matching."""
    return re.sub(r"[^a-z0-9]+", " ", title.lower()).strip()


def term_matches(normalized: str, tokens: list[str], term: str) -> bool:
    """Return whether a normalized title matches one term or phrase."""
    cleaned = term.lower().strip()
    if not cleaned:
        return False
    if " " in cleaned:
        return cleaned in normalized
    if cleaned.endswith("*"):
        prefix = cleaned[:-1]
        return any(token.startswith(prefix) for token in tokens)
    plural = cleaned + "s"
    es_plural = cleaned + "es"
    return any(token in {cleaned, plural, es_plural} for token in tokens)


def _print_json(payload: dict[str, Any]) -> None:
    """Print JSON robustly on Windows consoles with legacy encodings."""
    text = json.dumps(payload, indent=2, ensure_ascii=False) + "\n"
    try:
        print(text, end="")
    except UnicodeEncodeError:
        sys.stdout.buffer.write(text.encode("utf-8", errors="replace"))


def _text_has_cutoff_year(text: str, cutoff_year: int) -> bool:
    """Return whether text contains a year at or after the cutoff."""
    for match in re.finditer(r"\b(1[5-9]\d{2}|20\d{2}|21\d{2})\b", text):
        try:
            if int(match.group(0)) >= cutoff_year:
                return True
        except ValueError:
            continue
    return False


def _optional_proxy(value: str) -> str | None:
    """Normalize CLI proxy values."""
    if value.strip().lower() in {"", "none", "direct", "off"}:
        return None
    return value


if __name__ == "__main__":
    raise SystemExit(main())
