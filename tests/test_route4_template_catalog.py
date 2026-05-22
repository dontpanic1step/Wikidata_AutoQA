"""Tests for the reviewed Route 4 template catalog."""

from __future__ import annotations

import unittest

from test_support import ROOT  # noqa: F401
from wikidata_simpleqa.route4_template_catalog import (
    DISCARDED_ROUTE4_TEMPLATE_KEYS,
    get_route4_reviewed_single_hop_templates,
    get_route4_reviewed_template_by_key,
)
from wikidata_simpleqa.route4_two_hop import (
    CLUE_HIDDEN_OBJECT,
    CLUE_HIDDEN_SUBJECT,
    get_route4_combinable_single_hop_templates,
    get_route4_two_hop_template_catalog,
    get_route4_two_hop_template_summary,
    get_route4_uncombined_single_hop_templates,
)
from wikidata_simpleqa.canonical_questions import build_canonical_question
from wikidata_simpleqa.models import CandidateFact, DomainTemplate


class Route4TemplateCatalogTests(unittest.TestCase):
    """Check that workbook comments were applied to Route 4 templates."""

    def test_discards_reviewed_templates(self) -> None:
        template_keys = {template.template_key for template in get_route4_reviewed_single_hop_templates()}
        self.assertFalse(DISCARDED_ROUTE4_TEMPLATE_KEYS.intersection(template_keys))

    def test_country_location_comments_use_administrative_area(self) -> None:
        lighthouse = get_route4_reviewed_template_by_key("existing_lighthouse_country")
        self.assertIsNotNone(lighthouse)
        assert lighthouse is not None
        self.assertEqual(lighthouse.target_property_pid, "P131")
        self.assertIn("administrative area", lighthouse.canonical_question_template)

    def test_rephrases_reviewed_canonical_question(self) -> None:
        screenwriter = get_route4_reviewed_template_by_key("existing_film_screenwriter")
        self.assertIsNotNone(screenwriter)
        assert screenwriter is not None
        self.assertEqual(
            screenwriter.canonical_question_template,
            "Who wrote the script for the film {descriptor}?",
        )

    def test_adds_user_second_sheet_templates(self) -> None:
        template = get_route4_reviewed_template_by_key("route4_hadron_collider_beam_energy")
        self.assertIsNotNone(template)
        assert template is not None
        self.assertEqual(template.subject_type_label, "hadron collider")
        self.assertEqual(template.target_property_pid, "P13413")
        self.assertEqual(template.answer_format, "number")

    def test_number_and_value_formats_are_carried(self) -> None:
        number_template = get_route4_reviewed_template_by_key("generated_geography_administrative_places_number")
        self.assertIsNotNone(number_template)
        assert number_template is not None
        self.assertEqual(number_template.answer_format, "number")
        coordinate_template = get_route4_reviewed_template_by_key("route4_earthquake_coordinate_location")
        self.assertIsNotNone(coordinate_template)
        assert coordinate_template is not None
        self.assertEqual(coordinate_template.answer_format, "value")

    def test_year_placeholder_renders_from_candidate_date(self) -> None:
        template = get_route4_reviewed_template_by_key("generated_geography_administrative_places_number")
        self.assertIsNotNone(template)
        assert template is not None
        candidate = CandidateFact(
            subject_qid="Q1",
            subject_label="Example Municipality",
            subject_aliases=[],
            domain=template.template_key,
            topic=template.template_domain,
            answer_type=template.answer_type,
            question_family=template.question_family,
            subject_type_qids=[template.subject_type_qid],
            target_property_pid=template.target_property_pid,
            target_property_label=template.target_property_label,
            answer_qids=["VALUE:number:10"],
            answer_labels=["10"],
            answer_aliases=[],
            date_property_pid=template.date_property_pid,
            date_value="2024-05-01",
            target_time="2024",
            canonical_question="",
        )
        rendered = build_canonical_question(candidate, template)
        self.assertIn("2024", rendered)

    def test_two_hop_catalog_includes_subject_side_join(self) -> None:
        pairs = get_route4_two_hop_template_catalog()
        self.assertTrue(
            any(
                pair.answer_template_key == "existing_film_director"
                and pair.clue_template_key == "existing_film_based_on"
                and pair.clue_orientation == CLUE_HIDDEN_SUBJECT
                for pair in pairs
            )
        )

    def test_two_hop_catalog_includes_object_side_join(self) -> None:
        pairs = get_route4_two_hop_template_catalog()
        self.assertTrue(
            any(
                pair.answer_template_key == "existing_person_birth_date"
                and pair.clue_template_key == "existing_film_director"
                and pair.clue_orientation == CLUE_HIDDEN_OBJECT
                for pair in pairs
            )
        )

    def test_two_hop_catalog_allows_same_level_place_object_join(self) -> None:
        city_population = DomainTemplate(
            domain="city_population",
            topic="Geography",
            answer_type="Number",
            question_family="city_population",
            subject_type_qid="Q515",
            subject_type_label="city",
            date_property_pid="P571",
            target_property_pid="P1082",
            target_property_label="population",
            canonical_question_template="What was the population of {descriptor}?",
        )
        monument_city = DomainTemplate(
            domain="monument_city",
            topic="History",
            answer_type="Place",
            question_family="monument_city",
            subject_type_qid="Q4989906",
            subject_type_label="monument",
            date_property_pid="P571",
            target_property_pid="P131",
            target_property_label="city",
            canonical_question_template="Which city is {descriptor} in?",
        )

        pairs = get_route4_two_hop_template_catalog([city_population, monument_city])

        self.assertTrue(
            any(
                pair.answer_template_key == "city_population"
                and pair.clue_template_key == "monument_city"
                and pair.clue_orientation == CLUE_HIDDEN_OBJECT
                for pair in pairs
            )
        )

    def test_two_hop_catalog_allows_same_relation_place_object_join(self) -> None:
        city_parent_area = DomainTemplate(
            domain="city_parent_area",
            topic="Geography",
            answer_type="Place",
            question_family="city_parent_area",
            subject_type_qid="Q515",
            subject_type_label="city",
            date_property_pid="P571",
            target_property_pid="P131",
            target_property_label="located in administrative territorial entity",
            canonical_question_template="Which administrative area is {descriptor} in?",
        )
        monument_parent_area = DomainTemplate(
            domain="monument_parent_area",
            topic="History",
            answer_type="Place",
            question_family="monument_parent_area",
            subject_type_qid="Q4989906",
            subject_type_label="monument",
            date_property_pid="P571",
            target_property_pid="P131",
            target_property_label="located in administrative territorial entity",
            canonical_question_template="Which administrative area is {descriptor} in?",
        )

        pairs = get_route4_two_hop_template_catalog([city_parent_area, monument_parent_area])

        self.assertTrue(
            any(
                pair.answer_template_key == "city_parent_area"
                and pair.clue_template_key == "monument_parent_area"
                and pair.clue_orientation == CLUE_HIDDEN_OBJECT
                and pair.join_basis == "same_place_relation:P131"
                for pair in pairs
            )
        )

    def test_two_hop_catalog_allows_p131_join_without_subject_place_level(self) -> None:
        university_parent_area = DomainTemplate(
            domain="university_parent_area",
            topic="Education",
            answer_type="Place",
            question_family="university_parent_area",
            subject_type_qid="Q3918",
            subject_type_label="university",
            date_property_pid="P571",
            target_property_pid="P131",
            target_property_label="located in administrative territorial entity",
            canonical_question_template="Which administrative area is {descriptor} in?",
        )
        lighthouse_parent_area = DomainTemplate(
            domain="lighthouse_parent_area",
            topic="Architecture and Transportation",
            answer_type="Place",
            question_family="lighthouse_parent_area",
            subject_type_qid="Q39715",
            subject_type_label="lighthouse",
            date_property_pid="P571",
            target_property_pid="P131",
            target_property_label="located in administrative territorial entity",
            canonical_question_template="Which administrative area is {descriptor} in?",
        )

        pairs = get_route4_two_hop_template_catalog([university_parent_area, lighthouse_parent_area])

        self.assertTrue(
            any(
                pair.answer_template_key == "university_parent_area"
                and pair.clue_template_key == "lighthouse_parent_area"
                and pair.clue_orientation == CLUE_HIDDEN_OBJECT
                and pair.join_basis == "same_place_relation:P131"
                for pair in pairs
            )
        )

    def test_two_hop_catalog_allows_same_country_relation_object_join(self) -> None:
        country_member_country = DomainTemplate(
            domain="country_member_country",
            topic="Society and Culture",
            answer_type="Place",
            question_family="country_member_country",
            subject_type_qid="Q6256",
            subject_type_label="country",
            date_property_pid="P580",
            target_property_pid="P17",
            target_property_label="country",
            canonical_question_template="Which country is {descriptor} associated with?",
        )
        newspaper_country = DomainTemplate(
            domain="newspaper_country",
            topic="Language and Literature",
            answer_type="Place",
            question_family="newspaper_country",
            subject_type_qid="Q11032",
            subject_type_label="newspaper",
            date_property_pid="P571",
            target_property_pid="P17",
            target_property_label="country",
            canonical_question_template="Which country is {descriptor} from?",
        )

        pairs = get_route4_two_hop_template_catalog([country_member_country, newspaper_country])

        self.assertTrue(
            any(
                pair.answer_template_key == "country_member_country"
                and pair.clue_template_key == "newspaper_country"
                and pair.clue_orientation == CLUE_HIDDEN_OBJECT
                and pair.join_basis == "same_place_relation:P17"
                for pair in pairs
            )
        )

    def test_two_hop_catalog_rejects_mismatched_place_level_object_join(self) -> None:
        city_population = DomainTemplate(
            domain="city_population",
            topic="Geography",
            answer_type="Number",
            question_family="city_population",
            subject_type_qid="Q515",
            subject_type_label="city",
            date_property_pid="P571",
            target_property_pid="P1082",
            target_property_label="population",
            canonical_question_template="What was the population of {descriptor}?",
        )
        monument_country = DomainTemplate(
            domain="monument_country",
            topic="History",
            answer_type="Place",
            question_family="monument_country",
            subject_type_qid="Q4989906",
            subject_type_label="monument",
            date_property_pid="P571",
            target_property_pid="P17",
            target_property_label="country",
            canonical_question_template="Which country is {descriptor} in?",
        )

        pairs = get_route4_two_hop_template_catalog([city_population, monument_country])

        self.assertFalse(
            any(
                pair.answer_template_key == "city_population"
                and pair.clue_template_key == "monument_country"
                and pair.clue_orientation == CLUE_HIDDEN_OBJECT
                for pair in pairs
            )
        )

    def test_two_hop_catalog_does_not_broaden_generic_place_clues(self) -> None:
        pairs = get_route4_two_hop_template_catalog()
        self.assertFalse(
            any(
                pair.answer_template_key == "generated_education_universities_number"
                and pair.clue_template_key == "generated_history_historic_events_place"
                and pair.clue_orientation == CLUE_HIDDEN_OBJECT
                for pair in pairs
            )
        )

    def test_two_hop_catalog_does_not_treat_guidelines_as_organizations(self) -> None:
        pairs = get_route4_two_hop_template_catalog()
        self.assertFalse(
            any(
                pair.answer_template_key == "existing_clinical_guideline_publisher"
                and pair.clue_template_key == "existing_math_award_presenter"
                and pair.clue_orientation == CLUE_HIDDEN_OBJECT
                for pair in pairs
            )
        )

    def test_two_hop_catalog_skips_same_property_pairs(self) -> None:
        pairs = get_route4_two_hop_template_catalog()
        self.assertTrue(pairs)
        self.assertTrue(
            all(
                pair.answer_property_pid != pair.clue_property_pid
                or pair.answer_property_pid in {"P17", "P131"}
                for pair in pairs
            )
        )
        self.assertEqual(len({pair.template_key for pair in pairs}), len(pairs))

    def test_two_hop_catalog_does_not_use_literal_answer_as_bridge_entity(self) -> None:
        pairs = get_route4_two_hop_template_catalog()
        literal_answer_keys = {
            template.template_key
            for template in get_route4_reviewed_single_hop_templates()
            if template.answer_type in {"Date", "Number"} or template.answer_format in {"date", "number", "value"}
        }
        self.assertTrue(literal_answer_keys)
        self.assertFalse(
            any(
                pair.clue_orientation == CLUE_HIDDEN_OBJECT
                and pair.clue_template_key in literal_answer_keys
                for pair in pairs
            )
        )

    def test_two_hop_catalog_partitions_combinable_and_uncombined_templates(self) -> None:
        reviewed = get_route4_reviewed_single_hop_templates()
        combinable_keys = {template.template_key for template in get_route4_combinable_single_hop_templates(reviewed)}
        uncombined_keys = {template.template_key for template in get_route4_uncombined_single_hop_templates(reviewed)}
        reviewed_keys = {template.template_key for template in reviewed}
        self.assertFalse(combinable_keys.intersection(uncombined_keys))
        self.assertEqual(combinable_keys.union(uncombined_keys), reviewed_keys)
        self.assertIn("existing_product_release_date", uncombined_keys)

    def test_two_hop_catalog_summary_lists_remaining_one_hop_templates(self) -> None:
        summary = get_route4_two_hop_template_summary()
        self.assertEqual(summary["single_hop_templates"], 354)
        self.assertGreater(summary["two_hop_templates"], 0)
        self.assertEqual(summary["uncombined_single_hop_templates"], 25)
        self.assertIn("generated_economy_and_business_products_date", summary["uncombined_template_keys"])


if __name__ == "__main__":
    unittest.main()
