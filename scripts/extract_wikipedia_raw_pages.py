"""Extract raw Wikipedia page wikitext from XML dump slices while preserving tables."""

from __future__ import annotations

import argparse
import bz2
import json
import re
import shutil
import subprocess
import sys
from dataclasses import asdict, dataclass
from html import unescape
from pathlib import Path
from time import perf_counter
from typing import Iterable

ROOT = Path(__file__).resolve().parents[1]


@dataclass(slots=True)
class RawPage:
    """One raw namespace-0 page from a Wikipedia dump."""

    title: str
    page_id: str
    text: str


def parse_args() -> argparse.Namespace:
    """Parse CLI arguments."""
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--input", action="append", type=Path, default=[], help="Input pages-articles .bz2 slice. Can be repeated.")
    parser.add_argument("--input-dir", type=Path, default=None, help="Directory containing .bz2 slices.")
    parser.add_argument("--output", type=Path, default=ROOT / "cache" / "wikipedia_1percent_dumps" / "raw_pages.jsonl")
    parser.add_argument("--summary-output", type=Path, default=ROOT / "outputs" / "wikipedia_raw_page_extraction_summary.json")
    parser.add_argument("--recover-corrupt", action=argparse.BooleanOptionalAction, default=True)
    parser.add_argument("--recovery-dir", type=Path, default=ROOT / "tmp" / "wiki_recover_raw")
    parser.add_argument("--keep-recovered-blocks", action="store_true")
    return parser.parse_args()


def main() -> int:
    """Extract raw page JSONL and summary metadata."""
    args = parse_args()
    started = perf_counter()
    input_paths = collect_inputs(args.input, args.input_dir)
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.summary_output.parent.mkdir(parents=True, exist_ok=True)
    args.recovery_dir.mkdir(parents=True, exist_ok=True)
    stats = {
        "input_files": [str(path) for path in input_paths],
        "files_seen": 0,
        "files_recovered": 0,
        "files_failed": [],
        "pages_written": 0,
        "table_like_pages_written": 0,
        "output": str(args.output),
    }
    with args.output.open("w", encoding="utf-8") as output:
        for path in input_paths:
            stats["files_seen"] += 1
            for source_path in readable_sources(path, recover=args.recover_corrupt, recovery_dir=args.recovery_dir, stats=stats):
                try:
                    for page in iter_pages(source_path):
                        if not page.text.strip():
                            continue
                        payload = {
                            "title": page.title,
                            "page_id": page.page_id,
                            "text": page.text,
                            "has_wikitable_markup": "{|" in page.text,
                            "has_infobox_markup": "{{Infobox" in page.text or "{{infobox" in page.text,
                        }
                        output.write(json.dumps(payload, ensure_ascii=False) + "\n")
                        stats["pages_written"] += 1
                        if payload["has_wikitable_markup"] or payload["has_infobox_markup"]:
                            stats["table_like_pages_written"] += 1
                except (OSError, EOFError, UnicodeError) as exc:
                    stats["files_failed"].append({"path": str(source_path), "error": str(exc)})
    if not args.keep_recovered_blocks and args.recovery_dir.exists():
        for path in args.recovery_dir.glob("rec*.bz2"):
            path.unlink(missing_ok=True)
    stats["duration_seconds"] = round(perf_counter() - started, 4)
    args.summary_output.write_text(json.dumps(stats, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    print_json(stats)
    return 0


def collect_inputs(cli_paths: list[Path], input_dir: Path | None) -> list[Path]:
    """Return input files in deterministic order."""
    paths = [path for path in cli_paths if path.exists()]
    if input_dir is not None and input_dir.exists():
        paths.extend(sorted(input_dir.glob("*.bz2")))
    seen: set[Path] = set()
    result: list[Path] = []
    for path in paths:
        resolved = path.resolve()
        if resolved in seen:
            continue
        seen.add(resolved)
        result.append(path)
    return result


def readable_sources(path: Path, *, recover: bool, recovery_dir: Path, stats: dict) -> Iterable[Path]:
    """Yield readable bz2 sources, recovering corrupt bzip blocks when needed."""
    if is_bzip_readable(path):
        yield path
        return
    if not recover:
        stats["files_failed"].append({"path": str(path), "error": "bzip2_integrity_check_failed"})
        return
    recovered = recover_bzip_blocks(path, recovery_dir=recovery_dir)
    if not recovered:
        stats["files_failed"].append({"path": str(path), "error": "bzip2recover_produced_no_readable_blocks"})
        return
    stats["files_recovered"] += 1
    yield from recovered


def is_bzip_readable(path: Path) -> bool:
    """Return whether Python can stream at least one chunk from a bzip2 file."""
    try:
        with bz2.open(path, "rb") as handle:
            handle.read(1024)
        return True
    except OSError:
        return False


def recover_bzip_blocks(path: Path, *, recovery_dir: Path) -> list[Path]:
    """Run bzip2recover in a workspace directory and return readable recovered blocks."""
    recovery_dir.mkdir(parents=True, exist_ok=True)
    local_copy = recovery_dir / path.name
    shutil.copy2(path, local_copy)
    for old_block in recovery_dir.glob(f"rec*{path.name}"):
        old_block.unlink(missing_ok=True)
    subprocess.run(
        ["bzip2recover", local_copy.name],
        cwd=recovery_dir,
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL,
        check=False,
    )
    blocks = sorted(recovery_dir.glob(f"rec*{path.name}"))
    return [block for block in blocks if is_bzip_readable(block)]


def iter_pages(path: Path) -> Iterable[RawPage]:
    """Yield complete raw pages from one bzip2 XML source."""
    inside = False
    parts: list[str] = []
    with bz2.open(path, "rt", encoding="utf-8", errors="replace") as handle:
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


def page_from_xml(page_xml: str) -> RawPage | None:
    """Extract a namespace-0 non-redirect page preserving raw wikitext."""
    title_match = re.search(r"<title>(.*?)</title>", page_xml, flags=re.DOTALL)
    ns_match = re.search(r"<ns>(.*?)</ns>", page_xml, flags=re.DOTALL)
    id_match = re.search(r"<id>(.*?)</id>", page_xml, flags=re.DOTALL)
    if not title_match or not ns_match or ns_match.group(1).strip() != "0":
        return None
    if "<redirect " in page_xml:
        return None
    text_match = re.search(r"<text\b[^>]*>(.*?)</text>", page_xml, flags=re.DOTALL)
    if not text_match:
        return None
    return RawPage(
        title=unescape(title_match.group(1).strip()).replace("_", " "),
        page_id=unescape(id_match.group(1).strip()) if id_match else "",
        text=unescape(text_match.group(1)),
    )


def print_json(payload: dict) -> None:
    """Print JSON robustly on Windows consoles."""
    text = json.dumps(payload, indent=2, ensure_ascii=False) + "\n"
    try:
        print(text, end="")
    except UnicodeEncodeError:
        sys.stdout.buffer.write(text.encode("utf-8", errors="replace"))


if __name__ == "__main__":
    raise SystemExit(main())
