"""Maintain Route 3 Wikipedia page-ID exclusion/helper lists."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "src"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))

from wikidata_simpleqa.page_id_lists import (
    PageIdListEntry,
    collect_route3_page_ids_from_directory,
    read_page_id_entries,
    restore_route3_page_id_entries_from_accepted_directory,
    write_page_id_entries,
    write_page_id_list,
)


def parse_args() -> argparse.Namespace:
    """Parse CLI arguments."""
    parser = argparse.ArgumentParser(description=__doc__)
    subparsers = parser.add_subparsers(dest="command", required=True)

    inherit = subparsers.add_parser("inherit", help="Copy or merge existing page-ID lists into a new list.")
    inherit.add_argument("--source", type=Path, action="append", required=True, help="Existing page-ID list file.")
    inherit.add_argument("--output", type=Path, required=True, help="Output page-ID list file.")
    inherit.add_argument(
        "--merge-existing-output",
        action="store_true",
        help="Union source IDs with the current output file if it already exists.",
    )
    inherit.add_argument("--dry-run", action="store_true", help="Print the summary without writing output.")
    inherit.add_argument(
        "--triadic-output",
        action="store_true",
        help="Write the inherited list in page_id/answer_type/table_type object format.",
    )

    release = subparsers.add_parser("release", help="Subtract page IDs represented by run folders from a list.")
    release.add_argument("--source", type=Path, required=True, help="Existing page-ID list file to subtract from.")
    release.add_argument("--release-dir", type=Path, action="append", required=True, help="Run artifact directory.")
    release.add_argument(
        "--release-source",
        type=Path,
        action="append",
        default=[],
        help="Optional extra page-ID list files to subtract.",
    )
    release.add_argument("--output", type=Path, help="Output page-ID list file. Required unless --in-place is set.")
    release.add_argument("--in-place", action="store_true", help="Overwrite --source with the released list.")
    release.add_argument(
        "--include-used-ids",
        action="store_true",
        help="Also subtract state used_ids. Off by default to avoid releasing inherited exclusions.",
    )
    release.add_argument("--dry-run", action="store_true", help="Print the summary without writing output.")

    restore = subparsers.add_parser(
        "restore-accepted",
        help="Restore a page-ID list from accepted JSONL records under a folder.",
    )
    restore.add_argument("--accepted-dir", type=Path, required=True, help="Folder containing accepted JSONL files.")
    restore.add_argument("--output", type=Path, required=True, help="Output page-ID list file.")
    restore.add_argument(
        "--triadic-output",
        action="store_true",
        help="Write accepted records as page_id/answer_type/table_type objects instead of page-only IDs.",
    )
    restore.add_argument("--dry-run", action="store_true", help="Print the summary without writing output.")
    return parser.parse_args()


def main() -> int:
    """Run the requested page-ID list operation."""
    args = parse_args()
    if args.command == "inherit":
        summary = _run_inherit(args)
    elif args.command == "release":
        summary = _run_release(args)
    elif args.command == "restore-accepted":
        summary = _run_restore_accepted(args)
    else:
        raise ValueError(f"Unsupported command: {args.command}")
    print(json.dumps(summary, indent=2, ensure_ascii=False))
    return 0


def _run_inherit(args: argparse.Namespace) -> dict:
    source_ids: set[int] = set()
    source_entries = set()
    source_counts: dict[str, int] = {}
    for path in args.source:
        entries = read_page_id_entries(path)
        ids = {entry.page_id for entry in entries}
        source_entries.update(entries)
        source_ids.update(ids)
        source_counts[str(path)] = len(ids)
    existing_output_entries = read_page_id_entries(args.output) if args.merge_existing_output else set()
    existing_output_ids = {entry.page_id for entry in existing_output_entries}
    output_ids = source_ids | existing_output_ids
    output_entries = source_entries | existing_output_entries
    if not args.dry_run:
        if args.triadic_output:
            write_page_id_entries(args.output, output_entries)
        else:
            write_page_id_list(args.output, output_ids)
    return {
        "command": "inherit",
        "sources": [str(path) for path in args.source],
        "source_counts": source_counts,
        "merge_existing_output": bool(args.merge_existing_output),
        "triadic_output": bool(args.triadic_output),
        "existing_output_count": len(existing_output_ids),
        "output": str(args.output),
        "output_count": len(output_entries if args.triadic_output else output_ids),
        "dry_run": bool(args.dry_run),
    }


def _run_release(args: argparse.Namespace) -> dict:
    output = _release_output_path(args)
    source_entries = read_page_id_entries(args.source, include_used_ids=args.include_used_ids)
    source_ids = {entry.page_id for entry in source_entries}
    release_ids: set[int] = set()
    release_entries = set()
    directory_summaries: list[dict] = []
    for directory in args.release_dir:
        collection = collect_route3_page_ids_from_directory(directory, include_used_ids=args.include_used_ids)
        release_ids.update(collection.page_ids)
        release_entries.update(collection.entries)
        directory_summaries.append(
            {
                "directory": str(directory),
                "page_id_count": len(collection.page_ids),
                "entry_count": len(collection.entries),
                "files_read": collection.files_read,
                "skipped_file_count": len(collection.skipped_files),
                "errors": collection.errors,
            }
        )
    release_source_counts: dict[str, int] = {}
    for path in args.release_source:
        entries = read_page_id_entries(path, include_used_ids=args.include_used_ids)
        ids = {entry.page_id for entry in entries}
        release_ids.update(ids)
        release_entries.update(entries)
        release_source_counts[str(path)] = len(ids)
    output_entries = {
        entry
        for entry in source_entries
        if not _entry_is_released(entry, release_entries=release_entries, release_ids=release_ids)
    }
    removed_entries = source_entries - output_entries
    removed_ids = source_ids & release_ids
    output_ids = {entry.page_id for entry in output_entries}
    if not args.dry_run:
        if any(entry.answer_type or entry.table_type for entry in source_entries):
            write_page_id_entries(output, output_entries)
        else:
            write_page_id_list(output, output_ids)
    return {
        "command": "release",
        "source": str(args.source),
        "source_count": len(source_ids),
        "source_entry_count": len(source_entries),
        "release_dirs": directory_summaries,
        "release_sources": [str(path) for path in args.release_source],
        "release_source_counts": release_source_counts,
        "include_used_ids": bool(args.include_used_ids),
        "release_id_count": len(release_ids),
        "release_entry_count": len(release_entries),
        "removed_count": len(removed_ids),
        "removed_entry_count": len(removed_entries),
        "output": str(output),
        "output_count": len(output_ids),
        "output_entry_count": len(output_entries),
        "dry_run": bool(args.dry_run),
    }


def _run_restore_accepted(args: argparse.Namespace) -> dict:
    collection = restore_route3_page_id_entries_from_accepted_directory(
        args.accepted_dir,
        triadic_entries=bool(args.triadic_output),
    )
    if not args.dry_run:
        if args.triadic_output:
            write_page_id_entries(args.output, collection.entries)
        else:
            write_page_id_list(args.output, collection.page_ids)
    return {
        "command": "restore-accepted",
        "accepted_dir": str(args.accepted_dir),
        "output": str(args.output),
        "triadic_output": bool(args.triadic_output),
        "page_id_count": len(collection.page_ids),
        "entry_count": len(collection.entries),
        "files_read": collection.files_read,
        "errors": collection.errors,
        "dry_run": bool(args.dry_run),
    }


def _entry_is_released(
    entry: PageIdListEntry,
    *,
    release_entries: set[PageIdListEntry],
    release_ids: set[int],
) -> bool:
    if entry.page_id not in release_ids and not any(release.page_id == entry.page_id for release in release_entries):
        return False
    page_entries = [release for release in release_entries if release.page_id == entry.page_id]
    if not page_entries:
        return entry.page_id in release_ids
    for release in page_entries:
        if not release.answer_type and not release.table_type:
            return True
        if (
            release.answer_type
            and release.table_type
            and entry.answer_type == release.answer_type
            and entry.table_type == release.table_type
        ):
            return True
    return False


def _release_output_path(args: argparse.Namespace) -> Path:
    if args.in_place:
        if args.output is not None and args.output != args.source:
            raise ValueError("--output cannot differ from --source when --in-place is set.")
        return args.source
    if args.output is None:
        raise ValueError("release requires --output unless --in-place is set.")
    return args.output


if __name__ == "__main__":
    raise SystemExit(main())
