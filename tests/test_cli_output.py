from __future__ import annotations

from io import BytesIO, TextIOWrapper
from pathlib import Path

import pytest

from wikidata_simpleqa.cli_output import print_json_summary


ROOT = Path(__file__).resolve().parents[1]


def test_print_json_summary_reconfigures_stream_to_utf8() -> None:
    raw = BytesIO()
    stream = TextIOWrapper(raw, encoding="ascii")

    print_json_summary({"label": "Häuser"}, stream=stream)
    stream.flush()

    assert stream.encoding.lower().replace("-", "") == "utf8"
    assert raw.getvalue().decode("utf-8").splitlines() == ['{', '  "label": "Häuser"', '}']
    stream.detach()


@pytest.mark.parametrize(
    ("script_name", "expected_call_count"),
    [
        ("run_wikipedia_infobox_pipeline.py", 1),
        ("run_wikipedia_infobox_recipe.py", 3),
        ("run_route3_review.py", 1),
        ("finalize_route3_review.py", 1),
    ],
)
def test_route3_summary_boundaries_use_utf8_printer(
    script_name: str,
    expected_call_count: int,
) -> None:
    source = (ROOT / "scripts" / script_name).read_text(encoding="utf-8")

    assert "from wikidata_simpleqa.cli_output import print_json_summary" in source
    assert source.count("print_json_summary(") == expected_call_count
    assert "print(json.dumps(" not in source
