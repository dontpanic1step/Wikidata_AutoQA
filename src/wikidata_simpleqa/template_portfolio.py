"""Build salvage-board and portfolio views for template-program management."""

from __future__ import annotations

import json
from collections import Counter
from pathlib import Path
from typing import Any

from .domain_templates import get_all_templates
from .models import DomainTemplate

DEFAULT_PROMOTION_THRESHOLDS = {
    "pass_rate": 0.6,
    "candidate_yield_rate": 0.4,
    "semantic_repro_rate": 1.0,
}

HIGH_SALVAGE_REASONS = {
    "canonical_question_failed_validation",
    "subject_topic_mismatch",
    "duplicate_subject_resource",
    "no_english_label",
    "no_answer_label",
}

LOW_SALVAGE_REASONS = {
    "subject_label_contains_year",
    "same_label_competitor_requires_temporal_disambiguation",
}

QUERY_HEAVY_PROBLEM_KINDS = {
    "staged_seed_strategy_used",
    "windowed_subject_seed_queries_used",
    "direct_candidate_query_failed",
    "time_windowed_tournament_seed_failed",
    "time_windowed_acquisition_seed_failed",
    "windowed_subject_seed_query_failed",
    "chunked_office_holder_lookup_failed",
    "chunked_office_history_lookup_failed",
}

REWRITE_TYPE_TO_STAGE = {
    "query_simplification": "query_rewrite",
    "topic_scope_adjustment": "template_definition_rewrite",
    "subject_type_adjustment": "template_definition_rewrite",
    "canonical_question_rewrite": "canonical_question_rewrite",
    "family_split": "family_scope_rewrite",
    "family_merge": "family_scope_rewrite",
    "replacement_variant": "replacement_rewrite",
}


def default_salvage_registry_path(root: Path) -> Path:
    """Return the machine-readable template salvage registry path."""
    return root / "config" / "template_salvage_registry.json"


def load_salvage_registry(path: Path) -> dict[str, Any]:
    """Load salvage registry JSON, or return an empty default structure."""
    if not path.exists():
        return {
            "version": 1,
            "promotion_thresholds": DEFAULT_PROMOTION_THRESHOLDS.copy(),
            "templates": {},
        }
    payload = json.loads(path.read_text(encoding="utf-8"))
    templates = payload.get("templates", {})
    if not isinstance(templates, dict):
        templates = {}
    thresholds = payload.get("promotion_thresholds", {})
    if not isinstance(thresholds, dict):
        thresholds = {}
    merged_thresholds = DEFAULT_PROMOTION_THRESHOLDS.copy()
    for key, value in thresholds.items():
        try:
            merged_thresholds[str(key)] = float(value)
        except (TypeError, ValueError):
            continue
    return {
        "version": int(payload.get("version", 1) or 1),
        "promotion_thresholds": merged_thresholds,
        "templates": templates,
    }


def build_salvage_board(
    *,
    status_index: dict[str, Any],
    registry: dict[str, Any] | None = None,
) -> dict[str, Any]:
    """Build a non-proven template salvage board from the status index."""
    registry = registry or {
        "promotion_thresholds": DEFAULT_PROMOTION_THRESHOLDS.copy(),
        "templates": {},
    }
    registry_templates = registry.get("templates", {})
    if not isinstance(registry_templates, dict):
        registry_templates = {}
    thresholds = registry.get("promotion_thresholds", DEFAULT_PROMOTION_THRESHOLDS)
    if not isinstance(thresholds, dict):
        thresholds = DEFAULT_PROMOTION_THRESHOLDS.copy()

    template_map = {template.template_key: template for template in get_all_templates()}
    rows = status_index.get("templates", [])
    if not isinstance(rows, list):
        rows = []

    proven_rows = [row for row in rows if row.get("best_known_semantic_status") == "proven"]
    scarcity_context = _build_diversity_context(proven_rows, template_map)

    board_rows: list[dict[str, Any]] = []
    counts = Counter()
    for row in rows:
        template_key = str(row.get("template_key", "") or row.get("domain", "")).strip()
        if not template_key:
            continue
        if row.get("best_known_semantic_status") == "proven":
            continue
        template = template_map.get(template_key)
        if template is None:
            continue
        registry_entry = registry_templates.get(template_key, {})
        if not isinstance(registry_entry, dict):
            registry_entry = {}
        board_row = _build_board_row(
            row=row,
            template=template,
            registry_entry=registry_entry,
            thresholds=thresholds,
            scarcity_context=scarcity_context,
        )
        board_rows.append(board_row)
        counts[f"salvage_potential:{board_row['salvage_potential']}"] += 1
        counts[f"workstream:{board_row['workstream']}"] += 1
        counts[f"salvage_stage:{board_row['salvage_stage']}"] += 1
        if board_row["promotion_gate"]["eligible_now"]:
            counts["promotion_candidates"] += 1
        if board_row["promotion_gate"]["near_ready"]:
            counts["near_promotion_candidates"] += 1
        if board_row["retireable"]:
            counts["retireable"] += 1

    sort_key = lambda item: (
        _salvage_priority_rank(item["salvage_potential"]),
        _workstream_priority_rank(item["workstream"]),
        -float(item["promotion_gate"].get("gap_score", 0.0)),
        item["template_key"],
    )
    board_rows.sort(key=sort_key)

    return {
        "status_mode": status_index.get("status_mode", "latest_live_status"),
        "promotion_thresholds": thresholds,
        "counts": dict(sorted(counts.items())),
        "templates": board_rows,
    }


def render_salvage_board_markdown(board: dict[str, Any]) -> str:
    """Render a readable Markdown salvage board."""
    rows = board.get("templates", [])
    counts = board.get("counts", {})
    lines = [
        "# Template Salvage Board",
        "",
        "## Counts",
        "",
    ]
    for key, value in sorted(counts.items()):
        lines.append(f"- `{key}`: `{value}`")
    lines.extend(
        [
            "",
            "## Templates",
            "",
            "| Template Key | Domain | Potential | Workstream | Stage | Promotion | Diversity | Next Rewrite |",
            "|---|---|---|---|---|---|---|---|",
        ]
    )
    for row in rows:
        promotion = "ready" if row["promotion_gate"]["eligible_now"] else "not_ready"
        lines.append(
            "| {template_key} | {domain} | {salvage_potential} | {workstream} | {salvage_stage} | {promotion} | {diversity_contribution} | {last_rewrite_type} |".format(
                template_key=row["template_key"],
                domain=row["domain"],
                salvage_potential=row["salvage_potential"],
                workstream=row["workstream"],
                salvage_stage=row["salvage_stage"],
                promotion=promotion,
                diversity_contribution=row["diversity_contribution"]["level"],
                last_rewrite_type=row["last_rewrite_type"] or "planned",
            )
        )
    return "\n".join(lines) + "\n"


def build_portfolio_report(board: dict[str, Any], status_index: dict[str, Any]) -> dict[str, Any]:
    """Summarize program-level template portfolio progress."""
    status_counts = status_index.get("counts", {})
    if not isinstance(status_counts, dict):
        status_counts = {}
    board_rows = board.get("templates", [])
    if not isinstance(board_rows, list):
        board_rows = []

    topic_counts = Counter()
    question_family_counts = Counter()
    workstream_counts = Counter()
    promotion_ready = 0
    near_promotion_ready = 0
    rewrite_attempted = 0
    successful_rewrite = 0
    replacement_needed = 0
    for row in board_rows:
        topic_counts[str(row.get("topic", "")).strip()] += 1
        question_family_counts[str(row.get("question_family", "")).strip()] += 1
        workstream_counts[str(row.get("workstream", "")).strip()] += 1
        if row.get("promotion_gate", {}).get("eligible_now"):
            promotion_ready += 1
        if row.get("promotion_gate", {}).get("near_ready"):
            near_promotion_ready += 1
        attempts = int(row.get("salvage_attempt_count", 0) or 0)
        if attempts > 0:
            rewrite_attempted += 1
        outcome = str(row.get("rewrite_outcome", "")).strip().lower()
        if outcome.startswith("improved"):
            successful_rewrite += 1
        if row.get("salvage_stage") == "replacement_rewrite":
            replacement_needed += 1

    rewrite_success_rate = (
        round(successful_rewrite / rewrite_attempted, 4)
        if rewrite_attempted
        else 0.0
    )
    return {
        "headline": {
            "total_templates": len(status_index.get("templates", [])),
            "proven_templates": int(status_counts.get("proven", 0) or 0),
            "non_proven_templates": len(board_rows),
            "promotion_ready_templates": promotion_ready,
            "near_promotion_templates": near_promotion_ready,
            "salvage_in_progress": sum(1 for row in board_rows if row.get("salvage_stage") != "retire"),
            "replacement_needed": replacement_needed,
            "rewrite_success_rate": rewrite_success_rate,
        },
        "status_counts": status_counts,
        "workstream_counts": dict(sorted(workstream_counts.items())),
        "topic_counts": dict(sorted(topic_counts.items())),
        "question_family_counts": dict(sorted(question_family_counts.items())),
        "top_candidates": board_rows[:15],
    }


def render_portfolio_report_markdown(report: dict[str, Any]) -> str:
    """Render a readable Markdown portfolio report."""
    headline = report.get("headline", {})
    workstream_counts = report.get("workstream_counts", {})
    topic_counts = report.get("topic_counts", {})
    top_candidates = report.get("top_candidates", [])
    lines = [
        "# Template Portfolio Report",
        "",
        "## Headline",
        "",
    ]
    for key, value in headline.items():
        lines.append(f"- `{key}`: `{value}`")
    lines.extend(["", "## Workstreams", ""])
    if workstream_counts:
        for key, value in workstream_counts.items():
            lines.append(f"- `{key}`: `{value}`")
    else:
        lines.append("- None")
    lines.extend(["", "## Topic Coverage", ""])
    if topic_counts:
        for key, value in topic_counts.items():
            lines.append(f"- `{key}`: `{value}`")
    else:
        lines.append("- None")
    lines.extend(
        [
            "",
            "## Top Candidates",
            "",
            "| Template Key | Domain | Potential | Workstream | Promotion | Hypothesis |",
            "|---|---|---|---|---|---|",
        ]
    )
    for row in top_candidates:
        lines.append(
            "| {template_key} | {domain} | {salvage_potential} | {workstream} | {promotion} | {rewrite_hypothesis} |".format(
                template_key=row["template_key"],
                domain=row["domain"],
                salvage_potential=row["salvage_potential"],
                workstream=row["workstream"],
                promotion="ready" if row["promotion_gate"]["eligible_now"] else "not_ready",
                rewrite_hypothesis=_compact_cell(str(row.get("rewrite_hypothesis", "")).strip() or "Needs explicit salvage hypothesis."),
            )
        )
    return "\n".join(lines) + "\n"


def _build_board_row(
    *,
    row: dict[str, Any],
    template: DomainTemplate,
    registry_entry: dict[str, Any],
    thresholds: dict[str, Any],
    scarcity_context: dict[str, Counter],
) -> dict[str, Any]:
    """Build one salvage-board row."""
    latest_run = row.get("latest_run") or {}
    telemetry = latest_run.get("telemetry", {}) if isinstance(latest_run, dict) else {}
    problem_kinds = _problem_kinds_from_telemetry(telemetry)
    rejection_reasons = row.get("rejection_reasons", [])
    if not isinstance(rejection_reasons, list):
        rejection_reasons = []
    status_detail = row.get("status_detail", {})
    salvage_potential = _infer_salvage_potential(
        current_status=str(row.get("current_status", "")).strip(),
        rejection_reasons=rejection_reasons,
        problem_kinds=problem_kinds,
        status_detail=status_detail,
    )
    inferred_stage = _infer_salvage_stage(
        rejection_reasons=rejection_reasons,
        problem_kinds=problem_kinds,
        status_detail=status_detail,
        current_status=str(row.get("current_status", "")).strip(),
    )
    salvage_stage = str(registry_entry.get("salvage_stage", "")).strip() or inferred_stage
    diversity_contribution = _build_diversity_contribution(
        row=row,
        template=template,
        scarcity_context=scarcity_context,
    )
    workstream = _infer_workstream(
        current_status=str(row.get("current_status", "")).strip(),
        status_detail=status_detail,
        problem_kinds=problem_kinds,
    )
    promotion_gate = _evaluate_promotion_gate(
        row=row,
        thresholds=thresholds,
        workstream=workstream,
    )
    salvage_attempt_count = int(registry_entry.get("salvage_attempt_count", 0) or 0)
    last_rewrite_type = str(registry_entry.get("last_rewrite_type", "")).strip()
    if last_rewrite_type and last_rewrite_type in REWRITE_TYPE_TO_STAGE:
        salvage_stage = REWRITE_TYPE_TO_STAGE[last_rewrite_type]
    rewrite_hypothesis = str(registry_entry.get("rewrite_hypothesis", "")).strip() or _default_rewrite_hypothesis(
        rejection_reasons=rejection_reasons,
        problem_kinds=problem_kinds,
        status_detail=status_detail,
        current_status=str(row.get("current_status", "")).strip(),
    )
    rewrite_outcome = str(registry_entry.get("rewrite_outcome", "")).strip()
    retirement_blocker = str(registry_entry.get("retirement_blocker", "")).strip()
    retireable = _is_retireable(
        rejection_reasons=rejection_reasons,
        salvage_attempt_count=salvage_attempt_count,
        retirement_blocker=retirement_blocker,
    )
    return {
        "template_key": row.get("template_key", template.template_key),
        "domain": row["domain"],
        "topic": template.template_domain,
        "question_family": template.question_family,
        "answer_type": template.answer_type,
        "reasoning_style": template.reasoning_style,
        "temporal_mode": template.temporal_mode,
        "current_status": row["current_status"],
        "latest_live_status": row["latest_live_status"],
        "best_known_semantic_status": row["best_known_semantic_status"],
        "pass_rate": row.get("reliability", {}).get("pass_rate"),
        "candidate_yield_rate": row.get("reliability", {}).get("candidate_yield_rate"),
        "semantic_repro_rate": row.get("reliability", {}).get("semantic_repro_rate"),
        "top_rejection_reasons": rejection_reasons[:5],
        "top_request_problem_kinds": problem_kinds[:5],
        "salvage_potential": salvage_potential,
        "salvage_stage": salvage_stage,
        "salvage_attempt_count": salvage_attempt_count,
        "last_rewrite_type": last_rewrite_type,
        "rewrite_hypothesis": rewrite_hypothesis,
        "rewrite_outcome": rewrite_outcome,
        "retirement_blocker": retirement_blocker,
        "retireable": retireable,
        "diversity_contribution": diversity_contribution,
        "promotion_gate": promotion_gate,
        "workstream": workstream,
        "status_detail_bucket": str(status_detail.get("bucket", "")).strip(),
    }


def _build_diversity_context(
    proven_rows: list[dict[str, Any]],
    template_map: dict[str, DomainTemplate],
) -> dict[str, Counter]:
    """Build scarcity counters from proven templates."""
    topic_counts = Counter()
    answer_type_counts = Counter()
    reasoning_style_counts = Counter()
    temporal_mode_counts = Counter()
    for row in proven_rows:
        template_key = str(row.get("template_key", "") or row.get("domain", "")).strip()
        template = template_map.get(template_key)
        if template is None:
            continue
        topic_counts[template.topic] += 1
        answer_type_counts[template.answer_type] += 1
        reasoning_style_counts[template.reasoning_style] += 1
        temporal_mode_counts[template.temporal_mode] += 1
    return {
        "topic": topic_counts,
        "answer_type": answer_type_counts,
        "reasoning_style": reasoning_style_counts,
        "temporal_mode": temporal_mode_counts,
    }


def _build_diversity_contribution(
    *,
    row: dict[str, Any],
    template: DomainTemplate,
    scarcity_context: dict[str, Counter],
) -> dict[str, Any]:
    """Estimate how much a template helps diversify the proven portfolio."""
    topic_count = scarcity_context["topic"].get(template.topic, 0)
    answer_type_count = scarcity_context["answer_type"].get(template.answer_type, 0)
    reasoning_style_count = scarcity_context["reasoning_style"].get(template.reasoning_style, 0)
    temporal_mode_count = scarcity_context["temporal_mode"].get(template.temporal_mode, 0)

    score = 0
    if topic_count <= 2:
        score += 2
    elif topic_count <= 5:
        score += 1
    if answer_type_count <= 4:
        score += 1
    if reasoning_style_count <= 2:
        score += 1
    if template.temporal_mode != "atemporal" and temporal_mode_count <= 1:
        score += 1

    if score >= 3:
        level = "high"
    elif score >= 1:
        level = "medium"
    else:
        level = "low"
    return {
        "level": level,
        "topic_proven_count": topic_count,
        "answer_type_proven_count": answer_type_count,
        "reasoning_style_proven_count": reasoning_style_count,
        "temporal_mode_proven_count": temporal_mode_count,
    }


def _problem_kinds_from_telemetry(telemetry: dict[str, Any]) -> list[str]:
    """Return stable request/problem kinds ordered by frequency."""
    if not isinstance(telemetry, dict):
        return []
    problems = telemetry.get("problems", [])
    if not isinstance(problems, list):
        return []
    counter = Counter()
    for problem in problems:
        if not isinstance(problem, dict):
            continue
        kind = str(problem.get("kind", "")).strip()
        if kind:
            counter[kind] += 1
    return [kind for kind, _ in counter.most_common()]


def _infer_salvage_potential(
    *,
    current_status: str,
    rejection_reasons: list[str],
    problem_kinds: list[str],
    status_detail: dict[str, Any],
) -> str:
    """Infer coarse salvage potential from current evidence."""
    if any(reason in LOW_SALVAGE_REASONS for reason in rejection_reasons):
        return "low"
    if current_status == "rejected_only":
        return "high"
    if any(reason in HIGH_SALVAGE_REASONS for reason in rejection_reasons):
        return "high"
    if any(kind in QUERY_HEAVY_PROBLEM_KINDS for kind in problem_kinds):
        return "high"
    bucket = str(status_detail.get("bucket", "")).strip()
    if bucket in {"implemented_sparse_2026", "implemented_sparse_2026_seeded"}:
        return "medium"
    if current_status == "error":
        return "medium"
    return "low"


def _infer_salvage_stage(
    *,
    rejection_reasons: list[str],
    problem_kinds: list[str],
    status_detail: dict[str, Any],
    current_status: str,
) -> str:
    """Infer the next salvage ladder stage."""
    if current_status == "proven":
        return "proven"
    if any(kind in QUERY_HEAVY_PROBLEM_KINDS for kind in problem_kinds):
        return "query_rewrite"
    if "canonical_question_failed_validation" in rejection_reasons:
        return "canonical_question_rewrite"
    if any(reason in {"subject_topic_mismatch", "duplicate_subject_resource", "no_english_label", "no_answer_label"} for reason in rejection_reasons):
        return "template_definition_rewrite"
    bucket = str(status_detail.get("bucket", "")).strip()
    if bucket in {"implemented_sparse_2026", "implemented_sparse_2026_seeded"}:
        return "family_scope_rewrite"
    return "template_definition_rewrite"


def _infer_workstream(
    *,
    current_status: str,
    status_detail: dict[str, Any],
    problem_kinds: list[str],
) -> str:
    """Infer the next workstream label for a non-proven template."""
    if current_status == "rejected_only":
        return "A_semantic_rewrite"
    bucket = str(status_detail.get("bucket", "")).strip()
    if bucket in {"implemented_sparse_2026", "implemented_sparse_2026_seeded"}:
        return "B_sparse_rewrite"
    if any(kind in QUERY_HEAVY_PROBLEM_KINDS for kind in problem_kinds):
        return "C_operational_rewrite"
    return "B_sparse_rewrite"


def _evaluate_promotion_gate(
    *,
    row: dict[str, Any],
    thresholds: dict[str, Any],
    workstream: str,
) -> dict[str, Any]:
    """Evaluate whether a template looks ready for promotion."""
    reasons: list[str] = []
    if row.get("best_known_semantic_status") != "proven":
        reasons.append("semantic_status_not_proven")
    reliability = row.get("reliability", {})
    if not isinstance(reliability, dict):
        reliability = {}
    pass_rate = reliability.get("pass_rate")
    candidate_yield_rate = reliability.get("candidate_yield_rate")
    semantic_repro_rate = reliability.get("semantic_repro_rate")
    pass_rate_threshold = float(thresholds.get("pass_rate", DEFAULT_PROMOTION_THRESHOLDS["pass_rate"]))
    candidate_yield_threshold = float(
        thresholds.get("candidate_yield_rate", DEFAULT_PROMOTION_THRESHOLDS["candidate_yield_rate"])
    )
    semantic_repro_threshold = float(
        thresholds.get("semantic_repro_rate", DEFAULT_PROMOTION_THRESHOLDS["semantic_repro_rate"])
    )
    gap_score = 0.0
    if pass_rate is None or float(pass_rate) < pass_rate_threshold:
        reasons.append("pass_rate_below_threshold")
        gap_score += max(0.0, pass_rate_threshold - float(pass_rate or 0.0))
    if candidate_yield_rate is None or float(candidate_yield_rate) < candidate_yield_threshold:
        reasons.append("candidate_yield_below_threshold")
        gap_score += max(0.0, candidate_yield_threshold - float(candidate_yield_rate or 0.0))
    if row.get("best_known_semantic_status") == "rejected_only":
        if semantic_repro_rate is None or float(semantic_repro_rate) < semantic_repro_threshold:
            reasons.append("semantic_repro_below_threshold")
            gap_score += max(0.0, semantic_repro_threshold - float(semantic_repro_rate or 0.0))
    return {
        "near_ready": reasons == ["semantic_status_not_proven"],
        "eligible_now": not reasons,
        "blocked_by": reasons,
        "gap_score": round(gap_score, 4),
        "recommended_workstream": workstream,
    }


def _default_rewrite_hypothesis(
    *,
    rejection_reasons: list[str],
    problem_kinds: list[str],
    status_detail: dict[str, Any],
    current_status: str,
) -> str:
    """Generate a default salvage hypothesis for planning."""
    if any(kind in QUERY_HEAVY_PROBLEM_KINDS for kind in problem_kinds):
        return "Simplify harvesting and reduce WDQS request count before changing semantics."
    if "canonical_question_failed_validation" in rejection_reasons:
        return "Rewrite the canonical question family to preserve uniqueness and avoid leakage."
    if "subject_topic_mismatch" in rejection_reasons:
        return "Tighten topic scope using structured Wikidata signals instead of broad keyword gating."
    if "duplicate_subject_resource" in rejection_reasons:
        return "Redesign or merge the family to avoid collisions with neighboring templates."
    if "no_english_label" in rejection_reasons or "no_answer_label" in rejection_reasons:
        return "Narrow the subject class toward entities with stronger English label coverage."
    bucket = str(status_detail.get("bucket", "")).strip()
    if bucket in {"implemented_sparse_2026", "implemented_sparse_2026_seeded"}:
        return "Adjust family scope or subject typing to improve yield in the current target-time window."
    if current_status == "error":
        return "Stabilize the executor or query path before making semantic judgments about the family."
    return "Start with a template-definition rewrite and verify whether the family is scoped correctly."


def _is_retireable(
    *,
    rejection_reasons: list[str],
    salvage_attempt_count: int,
    retirement_blocker: str,
) -> bool:
    """Return whether a template has exhausted the rewrite-before-retire ladder."""
    if any(reason in LOW_SALVAGE_REASONS for reason in rejection_reasons) and salvage_attempt_count >= 3:
        return True
    return bool(retirement_blocker and salvage_attempt_count >= 3)


def _compact_cell(text: str, limit: int = 100) -> str:
    """Compact long cell text for Markdown tables."""
    if len(text) <= limit:
        return text
    return text[: limit - 3] + "..."


def _salvage_priority_rank(label: str) -> int:
    """Return sort priority for salvage potential."""
    return {"high": 0, "medium": 1, "low": 2}.get(label, 3)


def _workstream_priority_rank(label: str) -> int:
    """Return sort priority for workstream ordering."""
    return {
        "A_semantic_rewrite": 0,
        "B_sparse_rewrite": 1,
        "C_operational_rewrite": 2,
    }.get(label, 3)
