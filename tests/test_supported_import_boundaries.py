from __future__ import annotations

import json
import os
from pathlib import Path
import subprocess
import sys


ROOT = Path(__file__).resolve().parents[1]
SUPPORTED_SCRIPTS = (
    "run_wikipedia_infobox_recipe.py",
    "run_wikipedia_infobox_pipeline.py",
    "run_route3_review.py",
    "finalize_route3_review.py",
    "run_openrouter_batch_predictions.py",
    "judge_openrouter_batch_predictions.py",
)
HISTORICAL_MODULE_PARTS = (
    "candidate_harvester",
    "cheap_model_qa",
    "generation_pipeline",
    "llm_rewrite",
    "wikidata_simpleqa.models",
    "kelm_generator",
    "pipeline",
    "route1_",
    "route4_",
    "wikidata_simpleqa.validators",
    "wikidata_client",
)
MODULE_MARKER = "__WIKIDATA_SIMPLEQA_MODULES__="
IMPORT_PROBE = """
import json
import runpy
import sys

script = sys.argv[1]
sys.argv = [script, "--help"]
try:
    runpy.run_path(script, run_name="__main__")
except SystemExit as exc:
    if exc.code not in (None, 0):
        raise
modules = sorted(name for name in sys.modules if name.startswith("wikidata_simpleqa"))
print("__WIKIDATA_SIMPLEQA_MODULES__=" + json.dumps(modules))
"""


def _probe_help(script_name: str) -> tuple[subprocess.CompletedProcess[str], list[str]]:
    script = ROOT / "scripts" / script_name
    env = os.environ.copy()
    env["PYTHONPATH"] = os.pathsep.join((str(ROOT / "src"), str(ROOT / "scripts")))
    completed = subprocess.run(
        [sys.executable, "-c", IMPORT_PROBE, str(script)],
        cwd=ROOT,
        env=env,
        text=True,
        capture_output=True,
        check=False,
    )
    marker_lines = [line for line in completed.stdout.splitlines() if line.startswith(MODULE_MARKER)]
    modules = json.loads(marker_lines[-1][len(MODULE_MARKER) :]) if marker_lines else []
    return completed, modules


def test_supported_script_set_is_explicit() -> None:
    assert all((ROOT / "scripts" / name).is_file() for name in SUPPORTED_SCRIPTS)


def test_supported_scripts_expose_clean_process_help() -> None:
    for script_name in SUPPORTED_SCRIPTS:
        completed, _ = _probe_help(script_name)
        assert completed.returncode == 0, (
            f"{script_name} --help failed\nstdout:\n{completed.stdout}\nstderr:\n{completed.stderr}"
        )


def test_supported_help_does_not_import_historical_package_modules() -> None:
    for script_name in SUPPORTED_SCRIPTS:
        completed, modules = _probe_help(script_name)
        assert completed.returncode == 0
        assert not any(part in module for module in modules for part in HISTORICAL_MODULE_PARTS)


def test_package_initialization_exports_only_supported_settings() -> None:
    env = os.environ.copy()
    env["PYTHONPATH"] = str(ROOT / "src")
    completed = subprocess.run(
        [
            sys.executable,
            "-c",
            "import json, sys, wikidata_simpleqa; "
            "print(json.dumps({'exports': wikidata_simpleqa.__all__, "
            "'modules': sorted(name for name in sys.modules "
            "if name.startswith('wikidata_simpleqa'))}))",
        ],
        cwd=ROOT,
        env=env,
        text=True,
        capture_output=True,
        check=True,
    )
    payload = json.loads(completed.stdout)
    assert payload["exports"] == ["Settings"]


def test_recipe_uses_package_worker_support_api() -> None:
    source = (ROOT / "scripts" / "run_wikipedia_infobox_recipe.py").read_text(encoding="utf-8")
    assert "from run_wikipedia_infobox_pipeline import" not in source
