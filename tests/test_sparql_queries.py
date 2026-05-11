"""Tests for generic SPARQL seed query builders."""

from __future__ import annotations

import unittest

from test_support import ROOT  # noqa: F401
from wikidata_simpleqa.models import DomainTemplate
from wikidata_simpleqa.sparql_queries import (
    build_candidate_query,
    build_count_candidate_query,
    build_subject_seed_query,
)


class SparqlQueryBuilderTests(unittest.TestCase):
    """Check that generic seed queries stay lightweight."""

    def test_build_candidate_query_omits_label_service(self) -> None:
        template = DomainTemplate(
            domain="film_based_on",
            topic="Arts and Media",
            answer_type="Work",
            question_family="what_work_film_based_on",
            subject_type_qid="Q11424",
            subject_type_label="film",
            date_property_pid="P577",
            target_property_pid="P144",
            target_property_label="based on",
            canonical_question_template="What work was {descriptor} based on?",
        )

        query = build_candidate_query(
            template=template,
            target_start_date="2026-01-01",
            date_upper_bound="2026-05-09",
            limit=3,
        )

        self.assertIn("SELECT ?item ?answer ?date", query)
        self.assertNotIn("?itemLabel", query)
        self.assertNotIn("?answerLabel", query)
        self.assertNotIn("SERVICE wikibase:label", query)

    def test_build_count_candidate_query_omits_label_service(self) -> None:
        template = DomainTemplate(
            domain="dataset_language_count",
            topic="Computer Science and AI",
            answer_type="Number",
            question_family="how_many_languages_dataset",
            subject_type_qid="Q1172284",
            subject_type_label="dataset",
            date_property_pid="P577",
            target_property_pid="P407",
            target_property_label="language of work or name",
            canonical_question_template="How many languages does {descriptor} use?",
            answer_format="number",
        )

        query = build_count_candidate_query(
            template=template,
            target_start_date="2026-01-01",
            date_upper_bound="2026-05-09",
            limit=3,
        )

        self.assertIn("SELECT ?item ?date (COUNT(DISTINCT ?value) AS ?answerCount)", query)
        self.assertNotIn("?itemLabel", query)
        self.assertNotIn("SERVICE wikibase:label", query)
        self.assertIn("GROUP BY ?item ?date", query)

    def test_candidate_query_can_require_english_subject_label_without_label_service(self) -> None:
        template = DomainTemplate(
            domain="monastery_country",
            topic="Philosophy and Religion",
            answer_type="Place",
            question_family="which_country_monastery_located",
            subject_type_qid="Q44613",
            subject_type_label="monastery",
            date_property_pid="P571",
            target_property_pid="P17",
            target_property_label="country",
            canonical_question_template="In which country is the monastery {descriptor} located?",
            query_tags=["require_english_subject_label"],
        )

        query = build_candidate_query(
            template=template,
            target_start_date="2026-01-01",
            date_upper_bound="2026-05-09",
            limit=3,
        )

        self.assertIn('?item rdfs:label ?itemEnLabel.', query)
        self.assertIn('FILTER(LANG(?itemEnLabel) = "en")', query)
        self.assertNotIn("SERVICE wikibase:label", query)

    def test_subject_seed_query_can_require_english_subject_label(self) -> None:
        template = DomainTemplate(
            domain="product_manufacturer",
            topic="Economy and Business",
            answer_type="Organization",
            question_family="which_company_manufactured_product",
            subject_type_qid="Q2424752",
            subject_type_label="product",
            date_property_pid="P577",
            target_property_pid="P176",
            target_property_label="manufacturer",
            canonical_question_template="Which company manufactured the product {descriptor}?",
            query_tags=["staged_seed_query", "require_english_subject_label"],
        )

        query = build_subject_seed_query(
            template=template,
            target_start_date="2026-01-01",
            date_upper_bound="2026-05-09",
            limit=3,
        )

        self.assertIn('?item rdfs:label ?itemEnLabel.', query)
        self.assertIn('FILTER(LANG(?itemEnLabel) = "en")', query)


if __name__ == "__main__":
    unittest.main()
