"""Tests for Route 1 QID-first multi-hop support."""

from __future__ import annotations

import tempfile
from pathlib import Path
import unittest

from test_support import ROOT  # noqa: F401
from wikidata_simpleqa.route1_multihop import (
    ROUTE1_MULTIHOP_JOIN_TEMPLATE_KEYS,
    Route1QidSeedState,
    Route1QidSeedUnit,
    get_route1_multihop_join_templates,
)


class Route1MultihopTests(unittest.TestCase):
    """Check template selection and QID seed-state behavior."""

    def test_default_templates_are_join_only_and_exclude_ordinal_families(self) -> None:
        templates = get_route1_multihop_join_templates()
        template_keys = {template.template_key for template in templates}

        self.assertEqual(template_keys, set(ROUTE1_MULTIHOP_JOIN_TEMPLATE_KEYS))
        self.assertTrue(all(template.reasoning_style == "multi_hop_join" for template in templates))
        self.assertNotIn("ordinal_tournament_winner", template_keys)
        self.assertNotIn("footballer_goals_in_ordinal_tournament", template_keys)
        self.assertTrue(all(template.answer_type != "Number" for template in templates))

    def test_state_reserves_recovers_and_syncs_seed_keys(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            path = Path(tmpdir) / "state.json"
            state = Route1QidSeedState.load(path)
            seed = Route1QidSeedUnit(
                template_key="film_source_work_author",
                subject_qid="Q1",
                date_anchor="2020-01-01",
                bridge_qids=("Q2",),
                answer_qids=("Q3",),
            )

            reserved = state.reserve_seed_units([seed], count=1)

            self.assertEqual([unit.state_key for unit in reserved], [seed.state_key])
            self.assertIn(seed.state_key, state.in_progress_keys)
            recovered = state.recover_stale_in_progress()
            self.assertEqual(recovered, [seed.state_key])
            self.assertEqual(state.rerun_pool, [seed.state_key])

            reserved_again = state.reserve_seed_units([seed], count=1)

            self.assertEqual([unit.state_key for unit in reserved_again], [seed.state_key])
            state.mark_accepted(seed.state_key)
            self.assertIn(seed.state_key, state.accepted_keys)
            self.assertNotIn(seed.state_key, state.rerun_pool)

            synced = state.sync_decided_keys(
                accepted_keys=[seed.state_key],
                rejected_keys=["film_source_work_author|Q9|2020-01-01|-|-"],
            )
            self.assertEqual(synced["accepted_keys_synced"], 1)
            self.assertEqual(synced["rejected_keys_synced"], 1)

    def test_state_does_not_reserve_used_fresh_seed_twice(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            state = Route1QidSeedState.load(Path(tmpdir) / "state.json")
            seed = Route1QidSeedUnit(
                template_key="terminal_operator_country",
                subject_qid="Q10",
            )

            self.assertEqual(len(state.reserve_seed_units([seed], count=1)), 1)
            state.mark_rejected(seed.state_key, reason="validator_rejected")

            self.assertEqual(state.reserve_seed_units([seed], count=1), [])


if __name__ == "__main__":
    unittest.main()
