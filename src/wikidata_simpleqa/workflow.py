"""Shared workflow helpers for Stage 5B automation and reporting."""

from __future__ import annotations

from dataclasses import dataclass
import json
from pathlib import Path
from typing import Any


@dataclass(frozen=True, slots=True)
class RunArtifacts:
    """Artifact paths produced by one recorded generation run."""

    source_name: str
    accepted_path: Path
    rejected_path: Path
    summary_path: Path
    include_in_review: bool = True


@dataclass(frozen=True, slots=True)
class PolicyDecision:
    """One machine-readable policy decision for review-sensitive templates."""

    domain: str
    decision_type: str
    rationale: str
    approval_status: str
    reviewer: str
    decision_date: str
    allowed_property_pids: tuple[str, ...] = ()
    notes: str = ""


@dataclass(frozen=True, slots=True)
class ArtifactRegistry:
    """Registry describing which workflow artifacts belong to one root."""

    root: Path
    outputs_dir: Path
    canonical_run_artifacts: tuple[RunArtifacts, ...]
    review_source_names: tuple[str, ...]

    def all_run_artifacts(self) -> list[RunArtifacts]:
        """Return canonical artifacts plus any later focused rerun artifacts on disk."""
        artifacts = list(self.canonical_run_artifacts)
        known_summary_names = {artifact.summary_path.name for artifact in artifacts}
        discovered: list[RunArtifacts] = []
        for summary_path in sorted(
            self.outputs_dir.glob("*_summary.json"),
            key=lambda path: (path.stat().st_mtime, path.name),
        ):
            if summary_path.name in known_summary_names:
                continue
            stem = summary_path.name.removesuffix("_summary.json")
            accepted_path = self.outputs_dir / f"{stem}_accepted.jsonl"
            rejected_path = self.outputs_dir / f"{stem}_rejected.jsonl"
            if not accepted_path.exists() and not rejected_path.exists():
                continue
            discovered.append(
                RunArtifacts(
                    source_name=stem,
                    accepted_path=accepted_path,
                    rejected_path=rejected_path,
                    summary_path=summary_path,
                    include_in_review=False,
                )
            )
        return artifacts + discovered

    def review_run_artifacts(self) -> list[RunArtifacts]:
        """Return only artifact sets that should feed the review bundle."""
        artifact_map = {
            artifact.source_name: artifact
            for artifact in self.canonical_run_artifacts
        }
        review_artifacts = [
            artifact_map[name]
            for name in self.review_source_names
            if name in artifact_map
        ]
        known_default_names = {artifact.source_name for artifact in self.canonical_run_artifacts}
        discovered = [
            artifact
            for artifact in self.all_run_artifacts()
            if artifact.source_name not in known_default_names
        ]
        known_names = {artifact.source_name for artifact in review_artifacts}
        for artifact in discovered:
            if artifact.source_name in known_names:
                continue
            if _artifact_has_records(artifact.accepted_path):
                review_artifacts.append(artifact)
                known_names.add(artifact.source_name)
        return review_artifacts

    def summary_paths(self) -> list[Path]:
        """Return ordered summary paths for canonical status classification."""
        return [artifact.summary_path for artifact in self.all_run_artifacts()]

    def rejected_paths(self) -> list[Path]:
        """Return ordered rejected-record paths for canonical status classification."""
        return [artifact.rejected_path for artifact in self.all_run_artifacts()]

    def accepted_paths(self) -> list[Path]:
        """Return ordered accepted-record paths for canonical status classification."""
        return [artifact.accepted_path for artifact in self.all_run_artifacts()]


def default_artifact_registry(root: Path) -> ArtifactRegistry:
    """Return the default artifact registry for one repository root."""
    outputs = root / "outputs"
    return ArtifactRegistry(
        root=root,
        outputs_dir=outputs,
        canonical_run_artifacts=(
            RunArtifacts(
                source_name="stage5_pilot",
                accepted_path=outputs / "stage5_pilot_accepted.jsonl",
                rejected_path=outputs / "stage5_pilot_rejected.jsonl",
                summary_path=outputs / "stage5_pilot_summary.json",
                include_in_review=False,
            ),
            RunArtifacts(
                source_name="prior_proven_stage5b",
                accepted_path=outputs / "stage5b_pilot_accepted.jsonl",
                rejected_path=outputs / "stage5b_pilot_rejected.jsonl",
                summary_path=outputs / "stage5b_pilot_summary.json",
            ),
            RunArtifacts(
                source_name="unproven_templates_2026",
                accepted_path=outputs / "unproven_templates_2026_accepted.jsonl",
                rejected_path=outputs / "unproven_templates_2026_rejected.jsonl",
                summary_path=outputs / "unproven_templates_2026_summary.json",
                include_in_review=False,
            ),
            RunArtifacts(
                source_name="rerun_nonreject_2026",
                accepted_path=outputs / "unproven_nonreject_2026_rerun_accepted.jsonl",
                rejected_path=outputs / "unproven_nonreject_2026_rerun_rejected.jsonl",
                summary_path=outputs / "unproven_nonreject_2026_rerun_summary.json",
            ),
            RunArtifacts(
                source_name="rerun_missing_review_2026",
                accepted_path=outputs / "rerun_missing_review_2026_accepted.jsonl",
                rejected_path=outputs / "rerun_missing_review_2026_rejected.jsonl",
                summary_path=outputs / "rerun_missing_review_2026_summary.json",
            ),
            RunArtifacts(
                source_name="rerun_focus_templates_2026",
                accepted_path=outputs / "rerun_focus_templates_2026_accepted.jsonl",
                rejected_path=outputs / "rerun_focus_templates_2026_rejected.jsonl",
                summary_path=outputs / "rerun_focus_templates_2026_summary.json",
            ),
            RunArtifacts(
                source_name="rerun_last_untracked",
                accepted_path=outputs / "rerun_last_untracked_accepted.jsonl",
                rejected_path=outputs / "rerun_last_untracked_rejected.jsonl",
                summary_path=outputs / "rerun_last_untracked_summary.json",
                include_in_review=False,
            ),
        ),
        review_source_names=(
            "prior_proven_stage5b",
            "rerun_nonreject_2026",
            "rerun_missing_review_2026",
            "rerun_focus_templates_2026",
        ),
    )


def default_run_artifacts(root: Path) -> list[RunArtifacts]:
    """Return the canonical artifact registry used by report scripts."""
    return list(default_artifact_registry(root).canonical_run_artifacts)


def discovered_run_artifacts(root: Path) -> list[RunArtifacts]:
    """Return canonical artifacts plus any later focused rerun artifacts on disk."""
    return default_artifact_registry(root).all_run_artifacts()


def default_policy_registry_path(root: Path) -> Path:
    """Return the machine-readable policy decision registry path."""
    return root / "config" / "policy_overrides.json"


def load_policy_registry(path: Path) -> list[PolicyDecision]:
    """Load policy decisions from JSON."""
    if not path.exists():
        return []
    payload = json.loads(path.read_text(encoding="utf-8"))
    decisions: list[PolicyDecision] = []
    for item in payload.get("decisions", []):
        if not isinstance(item, dict):
            continue
        decisions.append(
            PolicyDecision(
                domain=str(item.get("domain", "")).strip(),
                decision_type=str(item.get("decision_type", "")).strip(),
                rationale=str(item.get("rationale", "")).strip(),
                approval_status=str(item.get("approval_status", "")).strip(),
                reviewer=str(item.get("reviewer", "")).strip(),
                decision_date=str(item.get("decision_date", "")).strip(),
                allowed_property_pids=tuple(
                    str(value).strip()
                    for value in item.get("allowed_property_pids", [])
                    if str(value).strip()
                ),
                notes=str(item.get("notes", "")).strip(),
            )
        )
    return decisions


def policy_registry_map(path: Path) -> dict[str, PolicyDecision]:
    """Return policy decisions keyed by domain."""
    return {
        decision.domain: decision
        for decision in load_policy_registry(path)
        if decision.domain
    }


def review_run_artifacts(root: Path) -> list[RunArtifacts]:
    """Return only artifact sets that should feed the review bundle."""
    return default_artifact_registry(root).review_run_artifacts()


def status_summary_paths(root: Path) -> list[Path]:
    """Return ordered summary paths for canonical status classification."""
    return default_artifact_registry(root).summary_paths()


def status_rejected_paths(root: Path) -> list[Path]:
    """Return ordered rejected-record paths for canonical status classification."""
    return default_artifact_registry(root).rejected_paths()


def status_accepted_paths(root: Path) -> list[Path]:
    """Return ordered accepted-record paths for canonical status classification."""
    return default_artifact_registry(root).accepted_paths()


def render_policy_registry_markdown(decisions: list[PolicyDecision]) -> str:
    """Render a short Markdown table for policy review."""
    lines = [
        "# Policy Override Registry",
        "",
        "| Domain | Decision Type | Approval | Allowed Properties | Reviewer | Date | Rationale |",
        "|---|---|---|---|---|---|---|",
    ]
    if not decisions:
        lines.append("| None | - | - | - | - | - | - |")
        return "\n".join(lines) + "\n"
    for decision in decisions:
        allowed = ", ".join(decision.allowed_property_pids) or "-"
        lines.append(
            f"| {decision.domain} | {decision.decision_type} | {decision.approval_status} | {allowed} | {decision.reviewer} | {decision.decision_date} | {decision.rationale} |"
        )
    return "\n".join(lines) + "\n"


def _artifact_has_records(path: Path) -> bool:
    """Return whether a JSONL artifact exists and contains at least one row."""
    if not path.exists():
        return False
    return any(line.strip() for line in path.read_text(encoding="utf-8").splitlines())


def render_problem_backlog_markdown(items: list[dict[str, Any]]) -> str:
    """Render open workflow problems that need higher-level follow-up."""
    lines = [
        "# Workflow Problem Backlog",
        "",
        "This file tracks issues that should be reviewed beyond the narrow per-template loop.",
        "",
    ]
    if not items:
        lines.append("- None")
        return "\n".join(lines) + "\n"
    for item in items:
        title = str(item.get("title", "")).strip() or "Untitled problem"
        scope = str(item.get("scope", "")).strip() or "workflow"
        evidence = str(item.get("evidence", "")).strip()
        next_step = str(item.get("next_step", "")).strip()
        lines.append(f"- `{scope}`: {title}")
        if evidence:
            lines.append(f"  Evidence: {evidence}")
        if next_step:
            lines.append(f"  Next step: {next_step}")
    return "\n".join(lines) + "\n"


def summarize_phase_result(name: str, *, status: str, details: dict[str, Any]) -> dict[str, Any]:
    """Build a normalized workflow phase result payload."""
    return {
        "phase": name,
        "status": status,
        "details": details,
    }
