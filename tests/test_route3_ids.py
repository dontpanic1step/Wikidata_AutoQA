"""Tests for stable Route 3 record IDs."""

from __future__ import annotations

from wikidata_simpleqa.route3_ids import assign_unique_route3_record_ids, route3_record_id


def test_route3_record_id_uses_run_date_and_triadic_page_id_entry() -> None:
    record = {
        "question": "Who designed the example building?",
        "answer": "Jane Doe",
        "answer_type": "Person",
        "source_metadata": {
            "page_id_list_entry": {
                "page_id": 123,
                "answer_type": "Person",
                "table_type": "infobox",
            }
        },
    }

    assert route3_record_id(record, run_date="2026-05-25") == "route3_20260525_p123_person_infobox"


def test_assign_unique_route3_record_ids_hashes_only_collisions() -> None:
    records = [
        {
            "question": "Who designed the first example?",
            "answer": "Jane Doe",
            "answer_type": "Person",
            "source_metadata": {
                "page_id": 123,
                "selected_source_table": {"table_type": "infobox"},
            },
        },
        {
            "question": "Who designed the second example?",
            "answer": "John Doe",
            "answer_type": "Person",
            "source_metadata": {
                "page_id": 123,
                "selected_source_table": {"table_type": "infobox"},
            },
        },
    ]

    assign_unique_route3_record_ids(records, run_date="2026-05-25")

    assert records[0]["id"].startswith("route3_20260525_p123_person_infobox_")
    assert records[1]["id"].startswith("route3_20260525_p123_person_infobox_")
    assert records[0]["id"] != records[1]["id"]
