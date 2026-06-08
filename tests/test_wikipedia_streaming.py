"""Tests for Route 3 random Wikipedia page-id streaming."""

from __future__ import annotations

import random
import tempfile
import unittest
from pathlib import Path

from test_support import ROOT  # noqa: F401
from wikidata_simpleqa.final_selection import select_final_records
from wikidata_simpleqa.wikipedia_streaming import PageIdStreamState, build_curid_url, build_pageid_url, page_id_from_url


class WikipediaStreamingTests(unittest.TestCase):
    """Check stream cache, rerun pool behavior, and final selection."""

    def test_build_curid_url_round_trips_page_id(self) -> None:
        url = build_curid_url(12345)
        self.assertEqual(url, "https://en.wikipedia.org/w/index.php?curid=12345")
        self.assertEqual(page_id_from_url(url), 12345)
        pageid_url = build_pageid_url(12345)
        self.assertEqual(pageid_url, "https://en.wikipedia.org/w/index.php?pageid=12345")
        self.assertEqual(page_id_from_url(pageid_url), 12345)

    def test_stream_state_reserves_unique_ids_and_persists(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            path = Path(tmpdir) / "state.json"
            state = PageIdStreamState.load(path)
            reserved = state.reserve_ids(
                count=5,
                lower_bound=1,
                upper_bound=20,
                rng=random.Random(7),
            )
            reloaded = PageIdStreamState.load(path)
        self.assertEqual(len(reserved), 5)
        self.assertEqual(len(set(reserved)), 5)
        self.assertTrue(set(reserved).issubset(reloaded.used_ids))
        self.assertEqual(set(reserved), reloaded.in_progress_ids)

    def test_stale_in_progress_ids_move_to_rerun_pool_first(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            path = Path(tmpdir) / "state.json"
            state = PageIdStreamState.load(path)
            first_reserved = state.reserve_ids(
                count=2,
                lower_bound=10,
                upper_bound=20,
                rng=random.Random(1),
            )
            reloaded = PageIdStreamState.load(path)
            recovered = reloaded.recover_stale_in_progress()
            second_reserved = reloaded.reserve_ids(
                count=2,
                lower_bound=10,
                upper_bound=20,
                rng=random.Random(2),
            )
        self.assertEqual(recovered, sorted(first_reserved))
        self.assertEqual(second_reserved, sorted(first_reserved))

    def test_mark_rerun_reuses_unresolved_id_without_fresh_duplicate(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            path = Path(tmpdir) / "state.json"
            state = PageIdStreamState.load(path)
            page_id = state.reserve_ids(
                count=1,
                lower_bound=100,
                upper_bound=100,
                rng=random.Random(3),
            )[0]
            state.mark_rerun(page_id, reason="pipeline_exception:RuntimeError")
            reserved_again = state.reserve_ids(
                count=1,
                lower_bound=100,
                upper_bound=100,
                rng=random.Random(4),
            )
        self.assertEqual(reserved_again, [100])

    def test_mark_rerun_persists_error_details_in_state_and_event(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            path = Path(tmpdir) / "state.json"
            state = PageIdStreamState.load(path)
            state.mark_rerun(
                100,
                reason="search_longtail_verifier_error",
                error_type="URLError",
                error_message="timed out while searching",
            )
            reloaded = PageIdStreamState.load(path)

        self.assertEqual(
            reloaded.rerun_error_details[100],
            {
                "error_type": "URLError",
                "error_message": "timed out while searching",
            },
        )
        self.assertEqual(reloaded.events[-1]["event"], "rerun")
        self.assertEqual(reloaded.events[-1]["error_type"], "URLError")
        self.assertEqual(reloaded.events[-1]["error_message"], "timed out while searching")

    def test_endpoint_sync_marks_decided_ids_and_removes_rerun_entries(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            path = Path(tmpdir) / "state.json"
            state = PageIdStreamState.load(path)
            state.mark_rerun(10, reason="transient")
            state.in_progress_ids.add(11)
            stats = state.sync_decided_ids(accepted_ids=[10], rejected_ids=[11], reason="endpoint_resume")
            reloaded = PageIdStreamState.load(path)

        self.assertEqual(stats, {"accepted_ids_synced": 1, "rejected_ids_synced": 1})
        self.assertIn(10, reloaded.accepted_ids)
        self.assertIn(11, reloaded.rejected_ids)
        self.assertNotIn(10, reloaded.rerun_pool)
        self.assertNotIn(11, reloaded.in_progress_ids)
        self.assertIn(10, reloaded.used_ids)
        self.assertIn(11, reloaded.used_ids)

    def test_table_search_candidates_reserve_only_unused_page_ids(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            path = Path(tmpdir) / "state.json"
            state = PageIdStreamState.load(path)
            selected = state.reserve_candidate_ids(
                [10, 11, 10, 12],
                count=3,
                source="table_search:insource",
            )
            state.mark_rejected(11, reason="wikipedia_infobox_no_tables")
            state.advance_table_search_offset('insource:"wikitable"', 50)
            reloaded = PageIdStreamState.load(path)
            second_selected = reloaded.reserve_candidate_ids(
                [10, 11, 13],
                count=2,
                source="table_search:insource",
            )
        self.assertEqual(selected, [10, 11, 12])
        self.assertEqual(second_selected, [13])
        self.assertEqual(reloaded.table_search_offset('insource:"wikitable"'), 50)

    def test_table_search_reservation_normalizes_string_page_ids(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            path = Path(tmpdir) / "state.json"
            state = PageIdStreamState.load(path)
            first_selected = state.reserve_candidate_ids(
                ["1069583"],
                count=1,
                source="table_search:offset=500",
            )
            second_selected = state.reserve_candidate_ids(
                [1069583, "1069583", "1069584"],
                count=2,
                source="table_search:offset=550",
            )

        self.assertEqual(first_selected, [1069583])
        self.assertEqual(second_selected, [1069584])

    def test_final_selection_dedupes_similar_questions_and_rebalances_domains(self) -> None:
        records = [
            {
                "question": "Which bridge in Example A has the longest span?",
                "domain": "Architecture",
                "subject_entity": {"url": "https://example.test/a"},
            },
            {
                "question": "Which bridge in Example A has the longest span?",
                "domain": "Architecture",
                "subject_entity": {"url": "https://example.test/a"},
            },
            {
                "question": "Which song on Chart B ranked first?",
                "domain": "Arts",
                "subject_entity": {"url": "https://example.test/b"},
            },
            {
                "question": "Which team in Table C scored the most points?",
                "domain": "Sports",
                "subject_entity": {"url": "https://example.test/c"},
            },
        ]
        selected, summary = select_final_records(
            records,
            target_count=3,
            similarity_threshold=0.9,
            domain_key="domain",
        )
        self.assertEqual(len(selected), 3)
        self.assertEqual(summary["deduped_count"], 3)
        self.assertEqual(summary["deduplication"]["removed_count"], 1)
        self.assertEqual(set(summary["domain_counts"]), {"Architecture", "Arts", "Sports"})


if __name__ == "__main__":
    unittest.main()
