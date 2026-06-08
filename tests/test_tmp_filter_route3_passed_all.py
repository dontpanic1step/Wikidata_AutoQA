"""Tests for the temporary Route 3 passed_all repair filter."""

from __future__ import annotations

import sys

from test_support import ROOT  # noqa: F401

SCRIPTS = ROOT / "scripts"
if str(SCRIPTS) not in sys.path:
    sys.path.insert(0, str(SCRIPTS))

from tmp_filter_route3_passed_all import route3_tmp_filter_rejection_reasons  # noqa: E402


def test_tmp_filter_rejects_external_links_source_table() -> None:
    record = {
        "question": "What is the archived example value?",
        "source_metadata": {
            "selected_source_table": {
                "table_index": 2,
                "section_heading": "External links",
                "rows": [["Name", "Value"], ["Alpha", "Beta"]],
                "markdown": "| Name | Value |\n| --- | --- |\n| Alpha | Beta |",
            }
        },
    }

    assert route3_tmp_filter_rejection_reasons(record) == [
        "no_external_links_tables:external_links_section",
    ]


def test_tmp_filter_rejects_external_links_table_from_subject_anchor_scope() -> None:
    record = {
        "question": "What is the archived example value?",
        "source_metadata": {
            "subject_anchors": {
                "table_scopes": [
                    {
                        "table_index": 7,
                        "table_title": "External archive",
                        "nearby_section_heading": "External links",
                    }
                ]
            },
            "parsed_tables": [
                {
                    "table_index": 7,
                    "section_heading": "External links",
                    "rows": [["Name", "Value"], ["Alpha", "Beta"]],
                    "markdown": "| Name | Value |\n| --- | --- |\n| Alpha | Beta |",
                }
            ],
        },
    }

    assert route3_tmp_filter_rejection_reasons(record) == [
        "no_external_links_tables:external_links_section",
    ]


def test_tmp_filter_rejects_award_what_year_without_month() -> None:
    record = {
        "question": "In which year did Jane Doe win the Example Award for Harbor Lights?",
        "source_metadata": {},
    }

    assert route3_tmp_filter_rejection_reasons(record) == ["post_rewrite_award_year_without_month"]


def test_tmp_filter_allows_oversized_selected_table_for_temporary_rerun() -> None:
    record = {
        "question": "What value is listed for Alpha?",
        "source_metadata": {
            "selected_source_table": {
                "table_index": 1,
                "section_heading": "Results",
                "rows": [["Name", "Value"] for _ in range(41)],
                "markdown": "| Name | Value |",
            }
        },
    }

    assert route3_tmp_filter_rejection_reasons(record) == []
