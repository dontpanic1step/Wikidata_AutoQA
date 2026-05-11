"""Tests for the template catalog."""

from __future__ import annotations

import unittest

from test_support import ROOT  # noqa: F401
from wikidata_simpleqa.domain_templates import (
    get_active_templates,
    get_blueprint_templates,
    get_date_answer_pilot_templates,
    get_multi_hop_pilot_templates,
    get_stage5b_templates,
    get_template_by_domain,
)


class DomainTemplateTests(unittest.TestCase):
    """Check catalog diversity and metadata."""

    def test_catalog_spans_multiple_topics(self) -> None:
        templates = get_active_templates()
        topics = {template.topic for template in templates}
        self.assertGreaterEqual(len(topics), 6)

    def test_catalog_spans_multiple_question_families(self) -> None:
        templates = get_active_templates()
        families = {template.question_family for template in templates}
        self.assertGreaterEqual(len(families), 8)

    def test_catalog_includes_non_who_templates(self) -> None:
        templates = get_active_templates()
        templates_with_non_who = [
            template
            for template in templates
            if not template.canonical_question_template.lower().startswith("who ")
        ]
        self.assertTrue(templates_with_non_who)

    def test_active_catalog_excludes_multi_hop_templates_by_default(self) -> None:
        templates = get_active_templates()
        domains = {template.domain for template in templates}
        self.assertNotIn("ordinal_tournament_winner", domains)

    def test_multi_hop_pilot_catalog_includes_ordinal_tournament_winner(self) -> None:
        templates = get_multi_hop_pilot_templates()
        domains = {template.domain for template in templates}
        self.assertIn("ordinal_tournament_winner", domains)
        self.assertIn("film_source_work_author", domains)

    def test_date_answer_pilot_catalog_includes_three_templates(self) -> None:
        templates = get_date_answer_pilot_templates()
        domains = {template.domain for template in templates}
        self.assertEqual(
            domains,
            {"benchmark_release_date", "product_release_date", "terminal_opening_date"},
        )

    def test_stage5b_catalog_combines_active_multi_hop_and_date_templates(self) -> None:
        templates = get_stage5b_templates()
        domains = {template.domain for template in templates}
        self.assertIn("film_director", domains)
        self.assertIn("ordinal_tournament_winner", domains)
        self.assertIn("benchmark_release_date", domains)

    def test_active_catalog_templates_are_marked_proven_in_runs(self) -> None:
        templates = get_active_templates()
        self.assertTrue(all(template.evidence_status == "proven_in_runs" for template in templates))

    def test_person_first_degree_template_is_now_marked_proven(self) -> None:
        template = next(
            template
            for template in get_multi_hop_pilot_templates()
            if template.domain == "person_first_degree_university"
        )
        self.assertEqual(template.evidence_status, "proven_in_runs")
        self.assertIn("stage5b_pilot", template.evidence_runs)

    def test_blueprint_catalog_has_about_one_hundred_templates(self) -> None:
        templates = get_blueprint_templates()
        self.assertGreaterEqual(len(templates), 100)

    def test_blueprint_catalog_covers_user_topic_list(self) -> None:
        templates = get_blueprint_templates()
        topics = {template.topic for template in templates}
        expected_topics = {
            "People",
            "Geography",
            "Politics and Law",
            "Economy and Business",
            "Society and Culture",
            "Philosophy and Religion",
            "Language and Literature",
            "Arts and Media",
            "Sports and Recreation",
            "Education",
            "Mathematics",
            "Physical Sciences",
            "Life Sciences",
            "Medicine and Health",
            "Earth, Environment, and Space",
            "Computer Science and AI",
            "Engineering and Technology",
            "Architecture and Transportation",
            "Food, Agriculture, and Daily Life",
        }
        self.assertTrue(expected_topics.issubset(topics))

    def test_blueprint_catalog_includes_date_answer_templates(self) -> None:
        templates = get_blueprint_templates()
        date_templates = [template for template in templates if template.answer_format == "date"]
        self.assertTrue(date_templates)

    def test_catalog_includes_twenty_time_related_templates(self) -> None:
        templates = get_stage5b_templates() + get_blueprint_templates()
        time_related_templates = [template for template in templates if template.temporal_mode != "atemporal"]
        self.assertGreaterEqual(len(time_related_templates), 19)

    def test_blueprint_catalog_includes_twenty_number_templates(self) -> None:
        templates = get_blueprint_templates()
        number_templates = [
            template
            for template in templates
            if template.answer_type == "Number" or template.answer_format == "number"
        ]
        self.assertGreaterEqual(len(number_templates), 20)

    def test_removed_subset_author_count_templates_are_absent(self) -> None:
        templates = get_blueprint_templates()
        domains = {template.domain for template in templates}
        self.assertIn("paper_author_count", domains)
        self.assertNotIn("math_article_author_count", domains)
        self.assertNotIn("biology_article_author_count", domains)
        self.assertIsNone(get_template_by_domain("math_article_author_count"))
        self.assertIsNone(get_template_by_domain("biology_article_author_count"))

    def test_retired_policy_mismatch_templates_are_absent(self) -> None:
        templates = get_blueprint_templates()
        domains = {template.domain for template in templates}
        self.assertNotIn("marriage_spouse", domains)
        self.assertNotIn("company_industry", domains)
        self.assertIsNone(get_template_by_domain("marriage_spouse"))
        self.assertIsNone(get_template_by_domain("company_industry"))

    def test_blueprint_catalog_includes_composed_fact_templates(self) -> None:
        templates = get_blueprint_templates()
        composed_templates = [
            template for template in templates if template.composition_style == "fact_join"
        ]
        self.assertTrue(composed_templates)

    def test_blueprint_catalog_includes_ordinal_templates(self) -> None:
        templates = get_blueprint_templates()
        ordinal_templates = [
            template
            for template in templates
            if "{ordinal}" in template.canonical_question_template
        ]
        self.assertTrue(ordinal_templates)

    def test_blueprint_catalog_still_includes_open_ordinal_and_stat_templates(self) -> None:
        templates = get_blueprint_templates()
        domains = {template.domain for template in templates}
        self.assertIn("ordinal_spouse", domains)
        self.assertIn("footballer_goals_in_ordinal_tournament", domains)
        self.assertIn("ordinal_tournament_host_country", domains)
        self.assertIn("ordinal_country_president", domains)
        self.assertIn("ordinal_country_prime_minister", domains)
        self.assertIn("ordinal_religious_leader", domains)
        self.assertIn("ordinal_university_chancellor", domains)


if __name__ == "__main__":
    unittest.main()
