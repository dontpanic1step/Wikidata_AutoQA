"""Tests for the expanded statusless single-hop template catalog."""

from __future__ import annotations

from collections import Counter
import unittest

from test_support import ROOT  # noqa: F401
from wikidata_simpleqa.single_hop_template_catalog import (
    ALLOWED_SINGLE_HOP_ANSWER_TYPES,
    SINGLE_HOP_EXPANSION_DOMAINS,
    get_single_hop_subdomain_plan,
    get_single_hop_template_catalog,
)


class SingleHopTemplateCatalogTests(unittest.TestCase):
    """Check balance and route-neutral metadata for the expanded catalog."""

    def test_catalog_has_four_hundred_templates(self) -> None:
        self.assertEqual(len(get_single_hop_template_catalog()), 400)

    def test_catalog_is_balanced_by_domain(self) -> None:
        counts = Counter(template.domain for template in get_single_hop_template_catalog())
        self.assertEqual(set(counts), set(SINGLE_HOP_EXPANSION_DOMAINS))
        self.assertTrue(all(count == 20 for count in counts.values()))

    def test_catalog_is_balanced_by_answer_type(self) -> None:
        counts = Counter(template.answer_type for template in get_single_hop_template_catalog())
        self.assertEqual(set(counts), set(ALLOWED_SINGLE_HOP_ANSWER_TYPES))
        self.assertTrue(all(count == 80 for count in counts.values()))

    def test_catalog_includes_history_domain(self) -> None:
        domains = {template.domain for template in get_single_hop_template_catalog()}
        self.assertIn("History", domains)

    def test_every_template_has_qids_pids_and_search_query(self) -> None:
        for template in get_single_hop_template_catalog():
            self.assertRegex(template.subject_type_qid, r"^Q\d+$", template.template_key)
            self.assertRegex(template.date_property_pid, r"^P\d+$", template.template_key)
            self.assertRegex(template.target_property_pid, r"^P\d+$", template.template_key)
            self.assertIn(f"wd:{template.subject_type_qid}", template.candidate_search_query)
            self.assertIn(f"wdt:{template.date_property_pid}", template.candidate_search_query)
            self.assertIn(f"wdt:{template.target_property_pid}", template.candidate_search_query)
            self.assertIn("LIMIT {limit}", template.candidate_search_query)

    def test_existing_templates_are_statusless_and_answer_types_are_normalized(self) -> None:
        existing = [
            template
            for template in get_single_hop_template_catalog()
            if template.origin == "existing_single_hop_non_ordinal_non_count"
        ]
        self.assertTrue(existing)
        self.assertTrue(all(template.legacy_template_key for template in existing))
        self.assertTrue(all(template.answer_type in ALLOWED_SINGLE_HOP_ANSWER_TYPES for template in existing))

    def test_catalog_excludes_ordinal_and_count_templates(self) -> None:
        for template in get_single_hop_template_catalog():
            question = template.canonical_question_template.casefold()
            self.assertNotIn("{ordinal}", question)
            self.assertNotIn("how many", question)
            self.assertNotIn("most ", question)
            self.assertNotIn("highest", question)

    def test_subdomain_plan_has_five_to_ten_subdomains_per_domain(self) -> None:
        plan = get_single_hop_subdomain_plan()
        self.assertEqual(set(plan), set(SINGLE_HOP_EXPANSION_DOMAINS))
        self.assertTrue(all(5 <= len(subdomains) <= 10 for subdomains in plan.values()))


if __name__ == "__main__":
    unittest.main()
