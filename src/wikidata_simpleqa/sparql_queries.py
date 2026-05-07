"""SPARQL query builders for candidate harvesting."""

from __future__ import annotations

from .models import DomainTemplate


def build_candidate_query(
    template: DomainTemplate,
    target_start_date: str,
    date_upper_bound: str,
    limit: int,
) -> str:
    """Build a raw candidate query for local uniqueness filtering."""
    instance_path = f"wdt:P31 wd:{template.subject_type_qid}" if template.exact_instance_only else f"wdt:P31/wdt:P279* wd:{template.subject_type_qid}"
    return f"""
SELECT ?item ?itemLabel ?answer ?answerLabel ?date WHERE {{
  ?item {instance_path};
        wdt:{template.date_property_pid} ?date;
        wdt:{template.target_property_pid} ?answer.

  FILTER(?date >= "{target_start_date}T00:00:00Z"^^xsd:dateTime)
  FILTER(?date <= "{date_upper_bound}T23:59:59Z"^^xsd:dateTime)

  SERVICE wikibase:label {{
    bd:serviceParam wikibase:language "en".
  }}
}}
LIMIT {max(limit * 5, limit)}
""".strip()
