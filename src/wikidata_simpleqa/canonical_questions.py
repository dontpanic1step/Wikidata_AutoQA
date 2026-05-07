"""Canonical question builders."""

from __future__ import annotations

from .models import AmbiguityResolution, CandidateFact, DomainTemplate


def build_canonical_question(
    candidate: CandidateFact,
    template: DomainTemplate,
    resolution: AmbiguityResolution | None = None,
) -> str:
    """Render a canonical question for the Stage 1 slice."""
    descriptor = resolution.descriptor if resolution is not None else candidate.subject_label
    format_args = {"descriptor": descriptor, "subject_kind": template.subject_type_label}
    format_args.update(candidate.source_metadata.get("question_format_args", {}))
    return template.canonical_question_template.format(**format_args)
