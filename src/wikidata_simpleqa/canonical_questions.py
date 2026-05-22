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
    date_value = candidate.date_value or candidate.target_time
    year = str(date_value)[:4] if date_value else str(candidate.target_time)[:4]
    month = _month_name(date_value)
    format_args = {
        "descriptor": descriptor,
        "subject_kind": template.subject_type_label,
        "year": year,
        "time": year,
        "month": month,
        "language": "English",
    }
    format_args.update(candidate.source_metadata.get("question_format_args", {}))
    return template.canonical_question_template.format(**format_args)


def _month_name(value: str) -> str:
    """Return an English month name from an ISO-like date string when possible."""
    months = {
        "01": "January",
        "02": "February",
        "03": "March",
        "04": "April",
        "05": "May",
        "06": "June",
        "07": "July",
        "08": "August",
        "09": "September",
        "10": "October",
        "11": "November",
        "12": "December",
    }
    text = str(value)
    month = text[5:7] if len(text) >= 7 else ""
    return months.get(month, "")
