import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "src"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))

from wikidata_simpleqa.page_id_lists import (
    PageIdListEntry,
    collect_route3_page_ids_from_directory,
    page_ids_excluded_for_context,
    read_page_id_list,
    read_page_id_entries,
    restore_route3_page_id_entries_from_accepted_directory,
    write_page_id_list,
)

SCRIPT = ROOT / "scripts" / "manage_route3_page_id_list.py"


class Route3PageIdListHelperTest(unittest.TestCase):
    def test_read_page_id_list_accepts_json_jsonl_plain_and_urls(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            root = Path(tmpdir)
            json_path = root / "ids.json"
            json_path.write_text(json.dumps([101, "102", {"page_id": 103}]), encoding="utf-8")
            jsonl_path = root / "ids.jsonl"
            jsonl_path.write_text(
                "\n".join(
                    [
                        json.dumps({"source_metadata": {"page_id": 201}}),
                        json.dumps({"streaming_discovery": {"page_id": 202}}),
                        "https://en.wikipedia.org/w/index.php?pageid=203",
                    ]
                ),
                encoding="utf-8",
            )

            self.assertEqual(read_page_id_list(json_path), {101, 102, 103})
            self.assertEqual(read_page_id_list(jsonl_path), {201, 202, 203})

    def test_collect_directory_uses_route3_artifacts_without_raw_used_ids_by_default(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            root = Path(tmpdir)
            (root / "01_person_summary.json").write_text(json.dumps({"page_ids": [101, 102]}), encoding="utf-8")
            (root / "01_person_state.json").write_text(
                json.dumps(
                    {
                        "used_ids": [101, 102, 999],
                        "accepted_ids": [201],
                        "rejected_ids": [202],
                        "in_progress_ids": [203],
                        "rerun_pool": [204],
                    }
                ),
                encoding="utf-8",
            )
            (root / "01_person_accepted.jsonl").write_text(
                json.dumps({"source_metadata": {"page_id": 301}}) + "\n",
                encoding="utf-8",
            )
            (root / "recipe_page_id_exclusions.json").write_text(json.dumps([999]), encoding="utf-8")

            collection = collect_route3_page_ids_from_directory(root)

        self.assertEqual(collection.page_ids, {101, 102, 201, 202, 203, 204, 301})
        self.assertNotIn(999, collection.page_ids)

    def test_collect_directory_can_include_used_ids_when_explicit(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            root = Path(tmpdir)
            (root / "01_state.json").write_text(json.dumps({"used_ids": [999]}), encoding="utf-8")

            collection = collect_route3_page_ids_from_directory(root, include_used_ids=True)

        self.assertEqual(collection.page_ids, {999})

    def test_inherit_command_writes_sorted_union(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            root = Path(tmpdir)
            source_a = root / "a.json"
            source_b = root / "b.json"
            output = root / "out.json"
            write_page_id_list(source_a, [3, 1])
            write_page_id_list(source_b, [2, 3])

            subprocess.run(
                [
                    sys.executable,
                    str(SCRIPT),
                    "inherit",
                    "--source",
                    str(source_a),
                    "--source",
                    str(source_b),
                    "--output",
                    str(output),
                ],
                cwd=ROOT,
                check=True,
                text=True,
                capture_output=True,
            )

            self.assertEqual(json.loads(output.read_text(encoding="utf-8")), [1, 2, 3])

    def test_inherit_command_can_write_triadic_entries(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            root = Path(tmpdir)
            source = root / "source.json"
            output = root / "out.json"
            source.write_text(
                json.dumps(
                    [
                        101,
                        {"page_id": 102, "answer_type": "Person", "table_type": "infobox"},
                    ]
                ),
                encoding="utf-8",
            )

            subprocess.run(
                [
                    sys.executable,
                    str(SCRIPT),
                    "inherit",
                    "--source",
                    str(source),
                    "--output",
                    str(output),
                    "--triadic-output",
                ],
                cwd=ROOT,
                check=True,
                text=True,
                capture_output=True,
            )

            entries = read_page_id_entries(output)

        self.assertEqual(
            entries,
            {
                PageIdListEntry(page_id=101),
                PageIdListEntry(page_id=102, answer_type="Person", table_type="infobox"),
            },
        )

    def test_page_id_context_matching_uses_page_only_or_exact_triad(self) -> None:
        entries = {
            PageIdListEntry(page_id=101, answer_type="Person", table_type="infobox"),
            PageIdListEntry(page_id=102, answer_type="Person", table_type="infobox"),
            PageIdListEntry(page_id=102, answer_type="Person", table_type="wikitable"),
            PageIdListEntry(page_id=103),
            PageIdListEntry(page_id=104, answer_type="Person"),
            PageIdListEntry(page_id=105, table_type="infobox"),
        }

        self.assertEqual(
            page_ids_excluded_for_context(entries, answer_types=["Person"], table_types=["infobox"]),
            {101, 102, 103},
        )
        self.assertEqual(
            page_ids_excluded_for_context(entries, answer_types=["Place"], table_types=["infobox"]),
            {103},
        )
        self.assertEqual(
            page_ids_excluded_for_context(entries, answer_types=["Person"], table_types=["infobox", "wikitable"]),
            {101, 102, 103},
        )

    def test_restore_accepted_directory_defaults_to_page_only_entries(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            root = Path(tmpdir)
            accepted_dir = root / "accepted"
            accepted_dir.mkdir()
            (accepted_dir / "accepted.jsonl").write_text(
                "\n".join(
                    [
                        json.dumps(
                            {
                                "answer_type": "Person",
                                "source_metadata": {
                                    "page_id": 101,
                                    "selected_source_table": {"table_type": "infobox"},
                                },
                            }
                        ),
                        json.dumps(
                            {
                                "answer_type": "Place",
                                "source_metadata": {
                                    "streaming_discovery": {"page_id": 102},
                                    "selected_source_table": {"table_type": "wikitable"},
                                },
                            }
                        ),
                        json.dumps(
                            {
                                "answer_type": "Number",
                                "rejection_reason": "not_accepted",
                                "source_metadata": {
                                    "page_id": 103,
                                    "selected_source_table": {"table_type": "infobox"},
                                },
                            }
                        ),
                    ]
                ),
                encoding="utf-8",
            )

            collection = restore_route3_page_id_entries_from_accepted_directory(accepted_dir)

        self.assertEqual(
            collection.entries,
            {
                PageIdListEntry(page_id=101),
                PageIdListEntry(page_id=102),
            },
        )

    def test_restore_accepted_directory_can_build_triadic_entries(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            root = Path(tmpdir)
            accepted_dir = root / "accepted"
            accepted_dir.mkdir()
            (accepted_dir / "accepted.jsonl").write_text(
                "\n".join(
                    [
                        json.dumps(
                            {
                                "answer_type": "Person",
                                "source_metadata": {
                                    "page_id": 101,
                                    "selected_source_table": {"table_type": "infobox"},
                                },
                            }
                        ),
                        json.dumps(
                            {
                                "answer_type": "Place",
                                "source_metadata": {
                                    "streaming_discovery": {"page_id": 102},
                                    "selected_source_table": {"table_type": "wikitable"},
                                },
                            }
                        ),
                    ]
                ),
                encoding="utf-8",
            )

            collection = restore_route3_page_id_entries_from_accepted_directory(
                accepted_dir,
                triadic_entries=True,
            )

        self.assertEqual(
            collection.entries,
            {
                PageIdListEntry(page_id=101, answer_type="Person", table_type="infobox"),
                PageIdListEntry(page_id=102, answer_type="Place", table_type="wikitable"),
            },
        )

    def test_release_command_subtracts_directory_ids(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            root = Path(tmpdir)
            source = root / "source.json"
            release_dir = root / "segment"
            output = root / "released.json"
            release_dir.mkdir()
            write_page_id_list(source, [1, 2, 3, 4, 999])
            (release_dir / "segment_summary.json").write_text(json.dumps({"page_ids": [2]}), encoding="utf-8")
            (release_dir / "segment_state.json").write_text(
                json.dumps({"accepted_ids": [3], "used_ids": [999]}),
                encoding="utf-8",
            )

            completed = subprocess.run(
                [
                    sys.executable,
                    str(SCRIPT),
                    "release",
                    "--source",
                    str(source),
                    "--release-dir",
                    str(release_dir),
                    "--output",
                    str(output),
                ],
                cwd=ROOT,
                check=True,
                text=True,
                capture_output=True,
            )
            summary = json.loads(completed.stdout)

            self.assertEqual(json.loads(output.read_text(encoding="utf-8")), [1, 4, 999])
            self.assertEqual(summary["removed_count"], 2)

    def test_release_command_subtracts_only_matching_triadic_entries(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            root = Path(tmpdir)
            source = root / "source.json"
            release_dir = root / "segment"
            output = root / "released.json"
            release_dir.mkdir()
            source.write_text(
                json.dumps(
                    [
                        {"page_id": 101, "answer_type": "Person", "table_type": "infobox"},
                        {"page_id": 101, "answer_type": "Place", "table_type": "infobox"},
                        {"page_id": 101, "answer_type": "Person", "table_type": "wikitable"},
                    ]
                ),
                encoding="utf-8",
            )
            (release_dir / "accepted.jsonl").write_text(
                json.dumps(
                    {
                        "answer_type": "Person",
                        "source_metadata": {
                            "page_id": 101,
                            "selected_source_table": {"table_type": "infobox"},
                        },
                    }
                )
                + "\n",
                encoding="utf-8",
            )

            subprocess.run(
                [
                    sys.executable,
                    str(SCRIPT),
                    "release",
                    "--source",
                    str(source),
                    "--release-dir",
                    str(release_dir),
                    "--output",
                    str(output),
                ],
                cwd=ROOT,
                check=True,
                text=True,
                capture_output=True,
            )

            entries = read_page_id_entries(output)

        self.assertEqual(
            entries,
            {
                PageIdListEntry(page_id=101, answer_type="Person", table_type="wikitable"),
                PageIdListEntry(page_id=101, answer_type="Place", table_type="infobox"),
            },
        )

    def test_restore_accepted_command_writes_page_only_list_by_default(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            root = Path(tmpdir)
            accepted_dir = root / "accepted"
            output = root / "accepted_ids.json"
            accepted_dir.mkdir()
            (accepted_dir / "records.jsonl").write_text(
                json.dumps(
                    {
                        "answer_type": "Date",
                        "source_metadata": {
                            "page_id": 501,
                            "selected_source_table": {"table_type": "infobox"},
                        },
                    }
                )
                + "\n",
                encoding="utf-8",
            )

            subprocess.run(
                [
                    sys.executable,
                    str(SCRIPT),
                    "restore-accepted",
                    "--accepted-dir",
                    str(accepted_dir),
                    "--output",
                    str(output),
                ],
                cwd=ROOT,
                check=True,
                text=True,
                capture_output=True,
            )

            payload = json.loads(output.read_text(encoding="utf-8"))

        self.assertEqual(payload, [501])

    def test_restore_accepted_command_can_write_triadic_page_id_list(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            root = Path(tmpdir)
            accepted_dir = root / "accepted"
            output = root / "triadic.json"
            accepted_dir.mkdir()
            (accepted_dir / "records.jsonl").write_text(
                json.dumps(
                    {
                        "answer_type": "Date",
                        "source_metadata": {
                            "page_id": 501,
                            "selected_source_table": {"table_type": "infobox"},
                        },
                    }
                )
                + "\n",
                encoding="utf-8",
            )

            subprocess.run(
                [
                    sys.executable,
                    str(SCRIPT),
                    "restore-accepted",
                    "--accepted-dir",
                    str(accepted_dir),
                    "--output",
                    str(output),
                    "--triadic-output",
                ],
                cwd=ROOT,
                check=True,
                text=True,
                capture_output=True,
            )

            entries = read_page_id_entries(output)

        self.assertEqual(entries, {PageIdListEntry(page_id=501, answer_type="Date", table_type="infobox")})

    def test_restore_triadic_entries_prefer_actual_selected_table_type(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            root = Path(tmpdir)
            accepted_dir = root / "accepted"
            output = root / "triadic.json"
            accepted_dir.mkdir()
            (accepted_dir / "records.jsonl").write_text(
                json.dumps(
                    {
                        "answer_type": "Person",
                        "source_metadata": {
                            "page_id": 601,
                            "source_channel": "infobox",
                            "table_source_types": ["infobox"],
                            "selected_source_table": {"table_type": "wikitable"},
                        },
                    }
                )
                + "\n",
                encoding="utf-8",
            )

            subprocess.run(
                [
                    sys.executable,
                    str(SCRIPT),
                    "restore-accepted",
                    "--accepted-dir",
                    str(accepted_dir),
                    "--output",
                    str(output),
                    "--triadic-output",
                ],
                cwd=ROOT,
                check=True,
                text=True,
                capture_output=True,
            )

            entries = read_page_id_entries(output)

        self.assertEqual(entries, {PageIdListEntry(page_id=601, answer_type="Person", table_type="wikitable")})


if __name__ == "__main__":
    unittest.main()
