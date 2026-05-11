"""SPARQL query builders for candidate harvesting."""

from __future__ import annotations

from .models import DomainTemplate


def _subject_label_constraints(template: DomainTemplate) -> str:
    """Return optional English-subject-label constraints for one template."""
    if "require_english_subject_label" not in template.query_tags:
        return ""
    return """
  ?item rdfs:label ?itemEnLabel.
  FILTER(LANG(?itemEnLabel) = "en")
""".rstrip()


def _answer_label_constraints(template: DomainTemplate) -> str:
    """Return optional English-answer-label constraints for one template."""
    if "require_english_answer_label" not in template.query_tags:
        return ""
    return """
  ?answer rdfs:label ?answerEnLabel.
  FILTER(LANG(?answerEnLabel) = "en")
""".rstrip()


def build_candidate_query(
    template: DomainTemplate,
    target_start_date: str,
    date_upper_bound: str,
    limit: int,
) -> str:
    """Build a raw candidate query for local uniqueness filtering."""
    instance_path = f"wdt:P31 wd:{template.subject_type_qid}" if template.exact_instance_only else f"wdt:P31/wdt:P279* wd:{template.subject_type_qid}"
    return f"""
SELECT ?item ?answer ?date WHERE {{
  ?item {instance_path};
        wdt:{template.date_property_pid} ?date;
        wdt:{template.target_property_pid} ?answer.

  FILTER(?date >= "{target_start_date}T00:00:00Z"^^xsd:dateTime)
  FILTER(?date <= "{date_upper_bound}T23:59:59Z"^^xsd:dateTime)
}}
LIMIT {max(limit * 5, limit)}
""".strip()


def build_subject_seed_query(
    template: DomainTemplate,
    target_start_date: str,
    date_upper_bound: str,
    limit: int,
) -> str:
    """Build a cheaper subject-seed query for broad classes."""
    return f"""
SELECT DISTINCT ?item ?date WHERE {{
  ?item wdt:{template.date_property_pid} ?date;
        wdt:{template.target_property_pid} ?seedValue.

  FILTER(?date >= "{target_start_date}T00:00:00Z"^^xsd:dateTime)
  FILTER(?date <= "{date_upper_bound}T23:59:59Z"^^xsd:dateTime)
}}
LIMIT {max(limit * 10, limit)}
""".strip()


def build_count_candidate_query(
    template: DomainTemplate,
    target_start_date: str,
    date_upper_bound: str,
    limit: int,
) -> str:
    """Build a grouped query for deterministic count-style templates."""
    instance_path = (
        f"wdt:P31 wd:{template.subject_type_qid}"
        if template.exact_instance_only
        else f"wdt:P31/wdt:P279* wd:{template.subject_type_qid}"
    )
    return f"""
SELECT ?item ?date (COUNT(DISTINCT ?value) AS ?answerCount) WHERE {{
  ?item {instance_path};
        wdt:{template.date_property_pid} ?date;
        wdt:{template.target_property_pid} ?value.

  FILTER(?date >= "{target_start_date}T00:00:00Z"^^xsd:dateTime)
  FILTER(?date <= "{date_upper_bound}T23:59:59Z"^^xsd:dateTime)
}}
GROUP BY ?item ?date
LIMIT {max(limit * 5, limit)}
""".strip()
