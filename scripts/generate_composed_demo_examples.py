"""Generate compositional multi-hop demo examples from known Wikidata QIDs."""

from __future__ import annotations

import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "src"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))

from wikidata_simpleqa.ambiguity import resolve_subject_ambiguity
from wikidata_simpleqa.canonical_questions import build_canonical_question
from wikidata_simpleqa.composed_harvester import (
    build_first_degree_candidate_from_person_qid,
    build_wedding_age_gap_candidate_from_person_qid,
)
from wikidata_simpleqa.config import Settings
from wikidata_simpleqa.domain_templates import get_template_by_domain
from wikidata_simpleqa.io import write_jsonl
from wikidata_simpleqa.models import AmbiguityResolution
from wikidata_simpleqa.validators import (
    has_forbidden_temporal_text,
    has_year,
    question_leaks_answer,
)
from wikidata_simpleqa.wikidata_client import WikidataClient


def _finalize(candidate, template):
    resolution = AmbiguityResolution(
        status="resolved_by_non_temporal_descriptor",
        descriptor=candidate.source_metadata.get("question_format_args", {}).get(
            "descriptor", candidate.subject_label
        ),
    )
    candidate.ambiguity_status = resolution.status
    candidate.canonical_question = build_canonical_question(candidate, template, resolution)
    candidate.validation_flags["no_year"] = not has_year(candidate.canonical_question)
    candidate.validation_flags["no_temporal_expression"] = not has_forbidden_temporal_text(
        candidate.canonical_question
    )
    candidate.validation_flags["answer_not_leaked"] = not question_leaks_answer(
        candidate.canonical_question, candidate.answer_labels
    )
    return candidate


def main() -> int:
    client = WikidataClient(
        user_agent="wikidata-simpleqa-generator/0.1",
        proxy=None,
        timeout_seconds=60,
    )

    wedding_template = get_template_by_domain("wedding_age_gap")
    degree_template = get_template_by_domain("person_first_degree_university")
    if wedding_template is None or degree_template is None:
        raise ValueError("Required templates are missing.")

    wedding_settings = Settings(target_time="2007-08-03", pilot_total=1)
    degree_settings = Settings(target_time="1999-12-27", pilot_total=1)

    wedding_candidate = build_wedding_age_gap_candidate_from_person_qid(
        client=client,
        settings=wedding_settings,
        template=wedding_template,
        person_qid="Q165911",
    )
    degree_candidate = build_first_degree_candidate_from_person_qid(
        client=client,
        settings=degree_settings,
        template=degree_template,
        person_qid="Q111698612",
    )

    accepted = []
    if wedding_candidate is not None:
        accepted.append(_finalize(wedding_candidate, wedding_template).to_output_record("composed_demo_000001"))
    if degree_candidate is not None:
        accepted.append(_finalize(degree_candidate, degree_template).to_output_record("composed_demo_000002"))

    output_path = ROOT / "outputs" / "composed_demo_examples.jsonl"
    write_jsonl(output_path, accepted)
    print(json.dumps({"accepted": len(accepted), "output_path": str(output_path)}, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
