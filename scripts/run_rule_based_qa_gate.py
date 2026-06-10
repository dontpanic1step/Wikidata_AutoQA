#!/usr/bin/env python3
"""Run a rule-based answer-type gate before final LLM QA filtering."""

from __future__ import annotations

import argparse
import glob
import json
import os
import re
import socket
import sys
import tempfile
from collections import defaultdict
from datetime import datetime, timezone
from pathlib import Path
from time import sleep
from typing import Any
from urllib.error import HTTPError, URLError
from urllib.request import Request, urlopen

PROJECT_ROOT = Path(__file__).resolve().parents[1]
SRC_DIR = PROJECT_ROOT / "src"
if str(SRC_DIR) not in sys.path:
    sys.path.insert(0, str(SRC_DIR))

from wikidata_simpleqa.date_reference import normalize_gate_date_answer


COMMON_WORD_URLS = (
    "https://raw.githubusercontent.com/hermitdave/FrequencyWords/master/content/2018/en/en_full.txt",
    "https://gist.githubusercontent.com/w8y/d9de9d857a953e751cbfb83bc13eba33/raw/wiki-100k.txt",
    "https://raw.githubusercontent.com/first20hours/google-10000-english/master/google-10000-english.txt",
)
COMMON_NAME_URLS = (
    "https://raw.githubusercontent.com/dominictarr/random-name/master/first-names.txt",
    "https://raw.githubusercontent.com/arineng/arincli/master/lib/last-names.txt",
)

DEFAULT_LEXICON_DIR = Path("cache") / "rule_based_qa_gate"
DEFAULT_SIMPLEQA_VERIFIED_PATH = Path(
    r"D:\Study\AI\My-research\Hallucinated_websearch\benchmark\ok_json\simpleqa_verified.json"
)

GATED_ANSWER_TYPES = {"Date", "Person", "Place"}
BOOL_KEY = "rule_answer_type_match"
PLACE_SEED_WHITELIST = {
    "abbey",
    "airport",
    "area",
    "arena",
    "arrondissement",
    "borough",
    "building",
    "campus",
    "capital city",
    "castle",
    "cave",
    "church",
    "city",
    "city and country",
    "city and province",
    "city and state",
    "coast",
    "college",
    "country",
    "county",
    "district",
    "doab",
    "duchy",
    "dukedom",
    "field",
    "fort",
    "garden",
    "geographic entity",
    "geographic area",
    "geographic location",
    "geographic region",
    "geographic section",
    "grammar school",
    "high school",
    "hospital",
    "hotel",
    "island",
    "kibbutz",
    "kingdom",
    "lake",
    "location",
    "middle school",
    "mountain",
    "municipality",
    "observatory",
    "ocean",
    "palace",
    "parochial school",
    "peninsular plateau",
    "place",
    "plateau",
    "province",
    "prison",
    "republic",
    "river",
    "school",
    "state",
    "stadium",
    "studio",
    "street address",
    "theater",
    "theater venue",
    "theatre",
    "town",
    "track",
    "university",
    "venue",
    "village",
    "ward",
    "zoo",
}

PLACE_CATEGORY_PATTERNS = (
    r"\bwhat is the name of the (?P<cat>[a-z][a-z -]{1,60}?)\s+(?:that|where|with|in|near|of|called|located)\b",
    r"\bwhat is the name of (?P<cat>the [a-z][a-z -]{1,60}?)\s+(?:that|where|with|in|near|of|called|located)\b",
    r"\bwhat is the (?P<cat>[a-z][a-z -]{1,60}?)\s+(?:where|that|with|in|near|of|called|located)\b",
    r"\bin which (?P<cat>[a-z][a-z -]{1,60}?)\s+(?:was|were|is|are|did|does|had|has|do|will|would|can)\b",
    r"\bin what (?P<cat>[a-z][a-z -]{1,60}?)\s+(?:was|were|is|are|did|does|had|has|do|will|would|can)\b",
    r"\bat which (?P<cat>[a-z][a-z -]{1,60}?)\s+(?:was|were|is|are|did|does|had|has|do|will|would|can)\b",
    r"\bat what (?P<cat>[a-z][a-z -]{1,60}?)\s+(?:was|were|is|are|did|does|had|has|do|will|would|can)\b",
    r"\bfrom which (?P<cat>[a-z][a-z -]{1,60}?)\s+(?:did|was|were|is|are|has|had|does)\b",
    r"\bfrom what (?P<cat>[a-z][a-z -]{1,60}?)\s+(?:did|was|were|is|are|has|had|does)\b",
    r"\bwhich (?P<cat>[a-z][a-z -]{1,60}?)\s+(?:was|were|is|are|did|does|has|had|do|will|would|can|extends)\b",
    r"\bwhat (?P<cat>[a-z][a-z -]{1,60}?)\s+(?:did|was|were|is|are|has|had|does)\b",
    r"\bname the (?P<cat>[a-z][a-z -]{1,60}?)\s+(?:in|of|near|where|that)\b",
)

CATEGORY_PREFIX_WORDS = {
    "american",
    "boston",
    "canadian",
    "english",
    "former",
    "first",
    "first public",
    "indian",
    "israeli",
    "ivy league",
    "largest",
    "mexican",
    "nassau county ny",
    "nebraska",
    "new jersey",
    "norwegian",
    "nyc",
    "only",
    "original",
    "paris",
    "rhode island",
    "second largest",
    "second-largest",
    "singapore",
    "small",
    "south american",
    "specific",
    "swiss",
    "the",
    "third-tallest",
    "tokyo",
    "two",
    "u s",
    "u.s.",
    "venezuelan",
    "vermont",
}

DERIVED_CATEGORY_HEADS = {
    "art school",
    "baseball field",
    "body of water",
    "capital city",
    "catholic church",
    "grammar school",
    "high school",
    "middle school",
    "parochial school",
    "peninsular plateau",
    "street address",
    "abbey",
    "airport",
    "area",
    "arrondissement",
    "borough",
    "building",
    "campus",
    "castle",
    "cave",
    "church",
    "city",
    "coast",
    "college",
    "country",
    "county",
    "district",
    "doab",
    "field",
    "fort",
    "garden",
    "geographic area",
    "geographic entity",
    "geographic location",
    "geographic region",
    "geographic section",
    "hospital",
    "hotel",
    "island",
    "kibbutz",
    "lake",
    "location",
    "mountain",
    "municipality",
    "observatory",
    "ocean",
    "palace",
    "place",
    "plateau",
    "province",
    "prison",
    "republic",
    "river",
    "school",
    "stadium",
    "state",
    "theater",
    "theater venue",
    "studio",
    "town",
    "track",
    "university",
    "venue",
    "village",
    "ward",
    "zoo",
}

PERSON_TOKEN_RE = re.compile(r"[^\W\d_][^\W\d_'.-]*")
PERSON_TITLE_SUFFIX_RE = re.compile(r"^(?P<prefix>.+?)\s+the\s+(?P<title>[^\W\d_][^\W\d_'.-]*)$")
PERSON_ROMAN_NUMERAL_SUFFIX_RE = re.compile(r"^(?P<prefix>.+?)\s+(?P<roman>[MDCLXVI]+)$")
ROMAN_NUMERAL_RE = re.compile(r"(?=[MDCLXVI]+\Z)M{0,4}(CM|CD|D?C{0,3})(XC|XL|L?X{0,3})(IX|IV|V?I{0,3})")
PERSON_MEDIAL_NAME_PARTICLES = {
    "abd",
    "abu",
    "af",
    "al",
    "ap",
    "bin",
    "bint",
    "de",
    "der",
    "di",
    "el",
    "ibn",
    "mac",
    "mc",
    "van",
    "von",
}
PERSON_PREFIX_NAME_PARTICLES = {
    "abd",
    "abu",
    "af",
    "al",
    "ap",
    "bin",
    "bint",
    "el",
    "ibn",
    "mac",
    "mc",
}


def utc_now_iso() -> str:
    return datetime.now(timezone.utc).isoformat(timespec="seconds")


def load_jsonl(path: Path) -> list[dict[str, Any]]:
    records: list[dict[str, Any]] = []
    with path.open("r", encoding="utf-8") as handle:
        for line in handle:
            if line.strip():
                records.append(json.loads(line))
    return records


def discover_input_files(input_path: Path, pattern: str, exclude_pattern: str = "") -> list[Path]:
    if input_path.is_file():
        return [input_path]
    if input_path.is_dir():
        files = sorted(Path(p) for p in glob.glob(str(input_path / pattern)) if Path(p).is_file())
        if exclude_pattern:
            excluded = {Path(p).resolve() for p in glob.glob(str(input_path / exclude_pattern))}
            files = [path for path in files if path.resolve() not in excluded]
        return files
    raise FileNotFoundError(f"Input path does not exist: {input_path}")


def atomic_write_jsonl(path: Path, records: list[dict[str, Any]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    temp_name = ""
    try:
        with tempfile.NamedTemporaryFile(
            "w",
            encoding="utf-8",
            dir=path.parent,
            prefix=f".{path.name}.",
            suffix=".tmp",
            delete=False,
        ) as handle:
            temp_name = handle.name
            for record in records:
                handle.write(json.dumps(record, ensure_ascii=False) + "\n")
            handle.flush()
            os.fsync(handle.fileno())
        os.replace(temp_name, path)
    except Exception:
        if temp_name:
            try:
                Path(temp_name).unlink(missing_ok=True)
            except Exception:
                pass
        raise


def atomic_write_json(path: Path, payload: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    temp_name = ""
    try:
        with tempfile.NamedTemporaryFile(
            "w",
            encoding="utf-8",
            dir=path.parent,
            prefix=f".{path.name}.",
            suffix=".tmp",
            delete=False,
        ) as handle:
            temp_name = handle.name
            json.dump(payload, handle, ensure_ascii=False, indent=2)
            handle.write("\n")
            handle.flush()
            os.fsync(handle.fileno())
        os.replace(temp_name, path)
    except Exception:
        if temp_name:
            try:
                Path(temp_name).unlink(missing_ok=True)
            except Exception:
                pass
        raise


def download_text_with_fallback(
    urls: tuple[str, ...],
    *,
    timeout_seconds: float = 30.0,
    max_retries: int = 3,
    retry_backoff_seconds: float = 1.0,
) -> str:
    last_error: Exception | None = None
    for url in urls:
        for attempt in range(max_retries + 1):
            request = Request(url=url, headers={"User-Agent": "wikidata-simpleqa-rule-gate/0.1"})
            try:
                with urlopen(request, timeout=timeout_seconds) as response:
                    return response.read().decode("utf-8", errors="replace")
            except (HTTPError, URLError, TimeoutError, socket.timeout) as exc:
                last_error = exc
                if isinstance(exc, HTTPError) and exc.code not in {408, 409, 425, 429, 500, 502, 503, 504}:
                    break
                if attempt < max_retries:
                    sleep(retry_backoff_seconds * (2**attempt))
    if last_error is not None:
        raise RuntimeError(f"Failed to download lexicon: {last_error}")
    raise RuntimeError("Failed to download lexicon without an explicit error")


def parse_word_lines(text: str, *, max_words: int | None = None) -> set[str]:
    words: set[str] = set()
    for line in text.splitlines():
        stripped = line.strip()
        if not stripped:
            continue
        token = re.split(r"[\s,]+", stripped, maxsplit=1)[0].strip().lower()
        if re.fullmatch(r"[a-z][a-z'.-]*", token):
            words.add(token)
            if max_words is not None and len(words) >= max_words:
                break
    return words


def ensure_lexicon_file(
    path: Path,
    urls: tuple[str, ...],
    *,
    allow_download: bool,
    fallback_words: set[str],
    max_words: int | None = None,
    min_words: int | None = None,
) -> set[str]:
    if path.exists():
        words = parse_word_lines(path.read_text(encoding="utf-8", errors="replace"), max_words=max_words)
        if min_words is None or len(words) >= min_words or not allow_download:
            return words
    if allow_download:
        text = download_text_with_fallback(urls)
        parsed_words = parse_word_lines(text, max_words=max_words)
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text("\n".join(sorted(parsed_words)) + "\n", encoding="utf-8")
        return parsed_words
    return set(fallback_words)


def load_person_lexicons(lexicon_dir: Path, *, allow_download: bool) -> tuple[set[str], set[str]]:
    common_words = ensure_lexicon_file(
        lexicon_dir / "common_words_100k.txt",
        COMMON_WORD_URLS,
        allow_download=allow_download,
        fallback_words={"the", "and", "of", "in", "a", "for", "to", "with", "on", "by", "from"},
        max_words=100000,
        min_words=100000,
    )
    common_names: set[str] = set()
    for index, urls in enumerate((COMMON_NAME_URLS[:1], COMMON_NAME_URLS[1:]), start=1):
        common_names.update(
            ensure_lexicon_file(
                lexicon_dir / f"common_names_{index}.txt",
                urls,
                allow_download=allow_download,
                fallback_words={
                    "jack",
                    "john",
                    "mary",
                    "maria",
                    "may",
                    "robert",
                    "william",
                    "smith",
                    "brown",
                    "wilson",
                },
            )
        )
    return common_words, common_names


def answer_words(answer: Any) -> list[str]:
    tokens = [m.group(0).strip("'.-").lower() for m in PERSON_TOKEN_RE.finditer(str(answer or ""))]
    return [token for token in tokens if len(token) > 1]


def _person_name_particle_words(tokens: list[str]) -> list[str]:
    return [tokens[index] for index in sorted(_person_medial_name_particle_indexes(tokens))]


def _person_medial_name_particle_indexes(tokens: list[str]) -> set[int]:
    indexes = {
        index
        for index, token in enumerate(tokens)
        if (
            0 < index < len(tokens) - 1
            and token in PERSON_MEDIAL_NAME_PARTICLES
        )
        or (
            index == 0
            and len(tokens) > 1
            and token in PERSON_PREFIX_NAME_PARTICLES
        )
    }
    return indexes if 1 <= len(indexes) <= 2 else set()


def _person_marker_words(tokens: list[str], *, common_words: set[str], common_names: set[str]) -> list[str]:
    name_particle_indexes = _person_medial_name_particle_indexes(tokens)
    return [
        token
        for index, token in enumerate(tokens)
        if index not in name_particle_indexes
        and token in common_words
        and token not in common_names
    ]


def _valid_roman_numeral(text: str) -> bool:
    return bool(ROMAN_NUMERAL_RE.fullmatch(text))


def _capitalized_word(text: str) -> bool:
    stripped = text.strip("'.-")
    return bool(stripped) and stripped[0].isupper()


def _person_allowed_name_pattern(
    answer: Any,
    *,
    common_words: set[str],
    common_names: set[str],
) -> dict[str, Any] | None:
    text = re.sub(r"\s+", " ", str(answer or "").strip())
    title_match = PERSON_TITLE_SUFFIX_RE.fullmatch(text)
    if title_match and _capitalized_word(title_match.group("title")):
        prefix_tokens = answer_words(title_match.group("prefix"))
        prefix_markers = _person_marker_words(prefix_tokens, common_words=common_words, common_names=common_names)
        if prefix_tokens and not prefix_markers:
            return {
                "pattern": "name_prefix_the_capitalized_epithet",
                "prefix_words": prefix_tokens,
                "prefix_marker_words": prefix_markers,
                "ignored_suffix_words": ["the", title_match.group("title").lower()],
            }

    roman_match = PERSON_ROMAN_NUMERAL_SUFFIX_RE.fullmatch(text)
    if roman_match and _valid_roman_numeral(roman_match.group("roman")):
        prefix_tokens = answer_words(roman_match.group("prefix"))
        prefix_markers = _person_marker_words(prefix_tokens, common_words=common_words, common_names=common_names)
        if prefix_tokens and not prefix_markers:
            return {
                "pattern": "name_prefix_roman_numeral_suffix",
                "prefix_words": prefix_tokens,
                "prefix_marker_words": prefix_markers,
                "ignored_suffix_words": [roman_match.group("roman").lower()],
            }

    return None


def evaluate_person_gate(
    record: dict[str, Any],
    *,
    common_words: set[str],
    common_names: set[str],
    threshold: float,
) -> tuple[bool, dict[str, Any]]:
    tokens = [token for token in answer_words(record.get("answer")) if token]
    name_particles = _person_name_particle_words(tokens)
    markers = _person_marker_words(tokens, common_words=common_words, common_names=common_names)
    ratio = (len(markers) / len(tokens)) if tokens else 0.0
    allowed_name_pattern = _person_allowed_name_pattern(
        record.get("answer"),
        common_words=common_words,
        common_names=common_names,
    )
    if allowed_name_pattern is not None:
        return True, {
            "rule": "person_common_words_minus_common_names",
            "answer_words": tokens,
            "marker_words": markers,
            "name_particle_words": name_particles,
            "marker_ratio": round(ratio, 4),
            "threshold": threshold,
            "allowed_name_pattern": allowed_name_pattern,
            "reason": "Person answer matches a conservative monarch or epithet name pattern.",
        }
    matched = ratio < threshold
    return matched, {
        "rule": "person_common_words_minus_common_names",
        "answer_words": tokens,
        "marker_words": markers,
        "name_particle_words": name_particles,
        "marker_ratio": round(ratio, 4),
        "threshold": threshold,
        "reason": (
            "Person answer has too many common non-name words."
            if not matched
            else "Person answer is below the common non-name word threshold."
        ),
    }


def normalize_category(text: str) -> str:
    category = re.sub(r"[^a-z0-9 &.-]+", " ", text.lower()).strip()
    category = re.sub(r"\s+", " ", category)
    category = category.replace("u.s.", "u s")
    if category.startswith("are the names of the three stadiums"):
        return "stadium"
    changed = True
    while changed:
        changed = False
        for prefix in sorted(CATEGORY_PREFIX_WORDS, key=len, reverse=True):
            if category == prefix:
                return category
            if category.startswith(prefix + " "):
                category = category[len(prefix) + 1 :].strip()
                changed = True
                break
    if not category.startswith("body of water"):
        for separator in (" in ", " of ", " near ", " from ", " at "):
            if separator in category:
                head = category.split(separator, 1)[0].strip()
                if head:
                    category = head
                    break
    for head in sorted(DERIVED_CATEGORY_HEADS, key=len, reverse=True):
        if category == head or category.startswith(head + " ") or category.endswith(" " + head):
            category = head
            break
    if category in {"countries", "villages", "stadiums", "schools", "universities"}:
        category = {
            "countries": "country",
            "villages": "village",
            "stadiums": "stadium",
            "schools": "school",
            "universities": "university",
        }[category]
    return category


def extract_place_category(question: Any) -> str | None:
    text = str(question or "").lower()
    for pattern in PLACE_CATEGORY_PATTERNS:
        match = re.search(pattern, text)
        if not match:
            continue
        category = normalize_category(match.group("cat"))
        if category and category not in {"is", "was", "were", "are", "did", "does", "the", "name"}:
            return category
    return None


def load_simpleqa_place_categories(path: Path) -> set[str]:
    data = json.loads(path.read_text(encoding="utf-8"))
    categories: set[str] = set()
    for record in data:
        if not isinstance(record, dict) or record.get("answer_type") != "Place":
            continue
        category = extract_place_category(record.get("question"))
        if category:
            categories.add(category)
    return categories


def load_place_whitelist(simpleqa_verified_path: Path | None) -> set[str]:
    whitelist = set(PLACE_SEED_WHITELIST)
    if simpleqa_verified_path and simpleqa_verified_path.exists():
        whitelist.update(load_simpleqa_place_categories(simpleqa_verified_path))
    return whitelist


def evaluate_place_gate(
    record: dict[str, Any],
    *,
    place_whitelist: set[str],
) -> tuple[bool, dict[str, Any]]:
    category = extract_place_category(record.get("question"))
    if category is None:
        return True, {
            "rule": "place_question_category_whitelist",
            "extracted_category": None,
            "reason": "No explicit place category was extracted; passing by default.",
        }
    matched = category in place_whitelist
    if matched:
        reason = f"Extracted place category is whitelisted: {category}."
    else:
        reason = f"Extracted category is not in the place whitelist: {category}."
    return matched, {
        "rule": "place_question_category_whitelist",
        "extracted_category": category,
        "whitelist_size": len(place_whitelist),
        "reason": reason,
    }


def evaluate_date_gate(record: dict[str, Any]) -> tuple[bool, dict[str, Any]]:
    original = str(record.get("answer") or "").strip()
    normalized = normalize_gate_date_answer(original)
    matched = normalized is not None
    return matched, {
        "rule": "date_standard_or_normalizable_format",
        "original_answer": original,
        "normalized_answer": normalized,
        "reason": (
            "Date answer is standard or normalizable into the accepted date format."
            if matched
            else "Date answer is not an accepted standard or normalizable date format."
        ),
    }


def evaluate_record(
    record: dict[str, Any],
    *,
    common_words: set[str],
    common_names: set[str],
    place_whitelist: set[str],
    person_threshold: float,
) -> tuple[dict[str, Any], bool]:
    output = dict(record)
    answer_type = str(record.get("answer_type") or "")
    if answer_type == "Date":
        matched, details = evaluate_date_gate(record)
        if matched and details.get("normalized_answer"):
            output["answer"] = details["normalized_answer"]
    elif answer_type == "Person":
        matched, details = evaluate_person_gate(
            record,
            common_words=common_words,
            common_names=common_names,
            threshold=person_threshold,
        )
    elif answer_type == "Place":
        matched, details = evaluate_place_gate(record, place_whitelist=place_whitelist)
    else:
        matched = True
        details = {
            "rule": "no_rule_for_answer_type",
            "reason": f"No rule-based gate is currently applied for answer_type={answer_type!r}.",
        }

    existing_bool = output.get("bool_result") if isinstance(output.get("bool_result"), dict) else {}
    output["bool_result"] = dict(existing_bool)
    output["bool_result"][BOOL_KEY] = matched
    output["rule_based_qa_gate"] = {
        "status": "matched" if matched else "mismatched",
        "answer_type": answer_type,
        "details": details,
        "created_at": utc_now_iso(),
    }
    return output, matched


def run_gate(
    records: list[dict[str, Any]],
    *,
    common_words: set[str],
    common_names: set[str],
    place_whitelist: set[str],
    person_threshold: float = 0.5,
) -> tuple[list[dict[str, Any]], list[dict[str, Any]]]:
    matched_records: list[dict[str, Any]] = []
    mismatched_records: list[dict[str, Any]] = []
    for record in records:
        output, matched = evaluate_record(
            record,
            common_words=common_words,
            common_names=common_names,
            place_whitelist=place_whitelist,
            person_threshold=person_threshold,
        )
        if matched:
            matched_records.append(output)
        else:
            mismatched_records.append(output)
    return matched_records, mismatched_records


def answer_type_filename(prefix: str, answer_type: Any) -> str:
    text = str(answer_type or "unknown").strip().lower()
    text = re.sub(r"[^a-z0-9]+", "_", text).strip("_") or "unknown"
    return f"{text}.{prefix}.jsonl"


def write_grouped_by_answer_type(
    records: list[dict[str, Any]],
    output_dir: Path,
    *,
    prefix: str,
    overwrite: bool,
) -> list[Path]:
    output_dir.mkdir(parents=True, exist_ok=True)
    grouped: dict[str, list[dict[str, Any]]] = defaultdict(list)
    for record in records:
        grouped[answer_type_filename(prefix, record.get("answer_type"))].append(record)

    written: list[Path] = []
    for filename, group in sorted(grouped.items()):
        path = output_dir / filename
        if path.exists() and not overwrite:
            raise FileExistsError(f"Output already exists; pass --overwrite to replace: {path}")
        atomic_write_jsonl(path, group)
        written.append(path)
    return written


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Run rule-based QA answer-type gate.")
    parser.add_argument("--input-path", required=True, type=Path, help="JSONL file or directory to gate.")
    parser.add_argument("--output-path", required=True, type=Path, help="Directory for matched and mismatched JSONLs.")
    parser.add_argument("--glob", default="*accepted*.jsonl", help="Directory input glob. Default: *accepted*.jsonl")
    parser.add_argument("--exclude-glob", default="", help="Optional directory input exclude glob.")
    parser.add_argument("--simpleqa-verified-path", type=Path, default=DEFAULT_SIMPLEQA_VERIFIED_PATH)
    parser.add_argument("--lexicon-dir", type=Path, default=DEFAULT_LEXICON_DIR)
    parser.add_argument("--no-download-lexicons", action="store_true", help="Use cached/fallback lexicons only.")
    parser.add_argument("--person-common-word-threshold", type=float, default=0.5)
    parser.add_argument("--overwrite", action="store_true")
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    input_files = discover_input_files(args.input_path, args.glob, args.exclude_glob)
    if not input_files:
        raise SystemExit(f"No input JSONL files found under {args.input_path} matching {args.glob!r}")

    records: list[dict[str, Any]] = []
    for input_file in input_files:
        records.extend(load_jsonl(input_file))

    common_words, common_names = load_person_lexicons(
        args.lexicon_dir,
        allow_download=not args.no_download_lexicons,
    )
    place_whitelist = load_place_whitelist(args.simpleqa_verified_path)
    matched, mismatched = run_gate(
        records,
        common_words=common_words,
        common_names=common_names,
        place_whitelist=place_whitelist,
        person_threshold=args.person_common_word_threshold,
    )

    matched_paths = write_grouped_by_answer_type(
        matched,
        args.output_path / "matched",
        prefix="rule_gate_matched",
        overwrite=args.overwrite,
    )
    mismatched_paths = write_grouped_by_answer_type(
        mismatched,
        args.output_path / "mismatched",
        prefix="rule_gate_mismatched",
        overwrite=args.overwrite,
    )
    summary = {
        "input_files": [str(path) for path in input_files],
        "records": len(records),
        "matched": len(matched),
        "mismatched": len(mismatched),
        "gated_answer_types": sorted(GATED_ANSWER_TYPES),
        "person_common_word_threshold": args.person_common_word_threshold,
        "lexicon_dir": str(args.lexicon_dir),
        "common_word_count": len(common_words),
        "common_name_count": len(common_names),
        "place_whitelist_count": len(place_whitelist),
        "matched_outputs": [str(path) for path in matched_paths],
        "mismatched_outputs": [str(path) for path in mismatched_paths],
        "place_whitelist_output": str(args.output_path / "place_whitelist.json"),
    }
    atomic_write_jsonl(args.output_path / "rule_gate_summary.jsonl", [summary])
    atomic_write_json(args.output_path / "place_whitelist.json", sorted(place_whitelist))
    print(json.dumps(summary, indent=2, ensure_ascii=False))


if __name__ == "__main__":
    main()
