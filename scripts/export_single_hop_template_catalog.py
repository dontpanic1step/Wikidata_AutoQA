"""Export the expanded statusless single-hop template catalog."""

from __future__ import annotations

import json
import sys
import zipfile
from collections import Counter
from pathlib import Path
from xml.sax.saxutils import escape

ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "src"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))

from wikidata_simpleqa.single_hop_template_catalog import (  # noqa: E402
    get_single_hop_subdomain_plan,
    single_hop_catalog_as_dicts,
    single_hop_catalog_summary,
)


def _count_lines(rows: list[dict[str, str]], key: str) -> list[str]:
    counts = Counter(row[key] for row in rows)
    return [f"| {value} | {counts[value]} |" for value in sorted(counts)]


def _status_label(status: str) -> str:
    """Return a short human-readable status label for review."""
    normalized = status.strip()
    if not normalized:
        return "Untracked"
    return normalized.replace("_", " ").title()


def _load_existing_statuses() -> dict[str, str]:
    """Load current template statuses from the generated review Markdown."""
    path = ROOT / "docs" / "template_catalog_review.md"
    statuses: dict[str, str] = {}
    if not path.exists():
        return statuses
    for line in path.read_text(encoding="utf-8").splitlines():
        if not line.startswith("| ") or line.startswith("|---"):
            continue
        cells = [cell.strip() for cell in line.strip("|").split("|")]
        if len(cells) < 5 or cells[1] == "Template":
            continue
        statuses[cells[1]] = _status_label(cells[4])
    return statuses


def _review_rows(rows: list[dict[str, str]]) -> list[dict[str, str]]:
    """Return the four-column workbook view requested for review."""
    statuses = _load_existing_statuses()
    review_rows: list[dict[str, str]] = []
    for row in rows:
        legacy_key = row.get("legacy_template_key", "")
        status = statuses.get(legacy_key, "New") if legacy_key else "New"
        review_rows.append(
            {
                "Domain": row["domain"],
                "Subdomain": row["subdomain"],
                "Answer Type": row["answer_type"],
                "Canonical Template": row["canonical_question_template"],
                "Existing Status": status,
            }
        )
    review_rows.sort(
        key=lambda row: (
            row["Domain"],
            row["Subdomain"],
            row["Existing Status"] != "New",
            row["Canonical Template"],
        )
    )
    return review_rows


def _column_name(index: int) -> str:
    """Return the Excel column name for a 1-based column index."""
    name = ""
    while index:
        index, remainder = divmod(index - 1, 26)
        name = chr(65 + remainder) + name
    return name


def _sheet_cell(value: str, row_index: int, column_index: int, style: int | None = None) -> str:
    """Return one inline-string worksheet cell."""
    cell_reference = f"{_column_name(column_index)}{row_index}"
    style_attribute = f' s="{style}"' if style is not None else ""
    return (
        f'<c r="{cell_reference}" t="inlineStr"{style_attribute}>'
        f'<is><t xml:space="preserve">{escape(value)}</t></is>'
        "</c>"
    )


def export_review_xlsx(path: Path, rows: list[dict[str, str]]) -> None:
    """Write the compact review workbook requested by the user."""
    path.parent.mkdir(parents=True, exist_ok=True)
    review_rows = _review_rows(rows)
    fieldnames = ["Domain", "Subdomain", "Answer Type", "Canonical Template", "Existing Status"]
    all_rows = [dict(zip(fieldnames, fieldnames, strict=False)), *review_rows]
    last_column = _column_name(len(fieldnames))
    dimension = f"A1:{last_column}{len(all_rows)}"
    widths = {
        "Domain": 34,
        "Subdomain": 28,
        "Answer Type": 16,
        "Canonical Template": 80,
        "Existing Status": 20,
    }
    column_widths = [
        f'<col min="{index}" max="{index}" width="{widths[fieldname]}" customWidth="1"/>'
        for index, fieldname in enumerate(fieldnames, start=1)
    ]
    worksheet_rows = []
    for row_index, row in enumerate(all_rows, start=1):
        cells = [
            _sheet_cell(
                row.get(fieldname, ""),
                row_index,
                column_index,
                style=1 if row_index == 1 else None,
            )
            for column_index, fieldname in enumerate(fieldnames, start=1)
        ]
        worksheet_rows.append(f'<row r="{row_index}">{"".join(cells)}</row>')
    worksheet_xml = f"""<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
<worksheet xmlns="http://schemas.openxmlformats.org/spreadsheetml/2006/main" xmlns:r="http://schemas.openxmlformats.org/officeDocument/2006/relationships">
  <dimension ref="{dimension}"/>
  <sheetViews><sheetView workbookViewId="0"><pane ySplit="1" topLeftCell="A2" activePane="bottomLeft" state="frozen"/></sheetView></sheetViews>
  <cols>{"".join(column_widths)}</cols>
  <sheetData>{"".join(worksheet_rows)}</sheetData>
  <autoFilter ref="{dimension}"/>
</worksheet>
"""
    workbook_xml = """<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
<workbook xmlns="http://schemas.openxmlformats.org/spreadsheetml/2006/main" xmlns:r="http://schemas.openxmlformats.org/officeDocument/2006/relationships">
  <sheets><sheet name="Single-Hop Review" sheetId="1" r:id="rId1"/></sheets>
</workbook>
"""
    workbook_rels_xml = """<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
<Relationships xmlns="http://schemas.openxmlformats.org/package/2006/relationships">
  <Relationship Id="rId1" Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/worksheet" Target="worksheets/sheet1.xml"/>
  <Relationship Id="rId2" Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/styles" Target="styles.xml"/>
</Relationships>
"""
    root_rels_xml = """<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
<Relationships xmlns="http://schemas.openxmlformats.org/package/2006/relationships">
  <Relationship Id="rId1" Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/officeDocument" Target="xl/workbook.xml"/>
</Relationships>
"""
    styles_xml = """<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
<styleSheet xmlns="http://schemas.openxmlformats.org/spreadsheetml/2006/main">
  <fonts count="2"><font><sz val="11"/><name val="Calibri"/></font><font><b/><sz val="11"/><name val="Calibri"/></font></fonts>
  <fills count="2"><fill><patternFill patternType="none"/></fill><fill><patternFill patternType="gray125"/></fill></fills>
  <borders count="1"><border><left/><right/><top/><bottom/><diagonal/></border></borders>
  <cellStyleXfs count="1"><xf numFmtId="0" fontId="0" fillId="0" borderId="0"/></cellStyleXfs>
  <cellXfs count="2"><xf numFmtId="0" fontId="0" fillId="0" borderId="0" xfId="0"/><xf numFmtId="0" fontId="1" fillId="0" borderId="0" xfId="0" applyFont="1"/></cellXfs>
  <cellStyles count="1"><cellStyle name="Normal" xfId="0" builtinId="0"/></cellStyles>
</styleSheet>
"""
    content_types_xml = """<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
<Types xmlns="http://schemas.openxmlformats.org/package/2006/content-types">
  <Default Extension="rels" ContentType="application/vnd.openxmlformats-package.relationships+xml"/>
  <Default Extension="xml" ContentType="application/xml"/>
  <Override PartName="/xl/workbook.xml" ContentType="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet.main+xml"/>
  <Override PartName="/xl/worksheets/sheet1.xml" ContentType="application/vnd.openxmlformats-officedocument.spreadsheetml.worksheet+xml"/>
  <Override PartName="/xl/styles.xml" ContentType="application/vnd.openxmlformats-officedocument.spreadsheetml.styles+xml"/>
</Types>
"""
    with zipfile.ZipFile(path, "w", compression=zipfile.ZIP_DEFLATED) as workbook:
        workbook.writestr("[Content_Types].xml", content_types_xml)
        workbook.writestr("_rels/.rels", root_rels_xml)
        workbook.writestr("xl/workbook.xml", workbook_xml)
        workbook.writestr("xl/_rels/workbook.xml.rels", workbook_rels_xml)
        workbook.writestr("xl/styles.xml", styles_xml)
        workbook.writestr("xl/worksheets/sheet1.xml", worksheet_xml)


def export_json(path: Path, rows: list[dict[str, str]]) -> None:
    """Write the machine-readable expanded catalog."""
    path.parent.mkdir(parents=True, exist_ok=True)
    payload = {
        "summary": single_hop_catalog_summary(),
        "templates": rows,
    }
    path.write_text(json.dumps(payload, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")


def export_markdown(path: Path, rows: list[dict[str, str]]) -> None:
    """Write the human-readable expanded catalog."""
    path.parent.mkdir(parents=True, exist_ok=True)
    summary = single_hop_catalog_summary()
    lines = [
        "# Single-Hop Template Expansion Catalog",
        "",
        "This statusless catalog extracts current single-hop templates that are not ordinal/count templates, normalizes answer types to `Person`, `Place`, `Number`, `Date`, and `Other`, and adds generated route-neutral single-hop templates for later migration.",
        "",
        "## Headline Stats",
        "",
        f"- Total templates: `{summary['total_templates']}`",
        f"- Existing extracted templates: `{summary['origin_counts'].get('existing_single_hop_non_ordinal_non_count', 0)}`",
        f"- Generated expansion templates: `{summary['origin_counts'].get('generated_single_hop_expansion', 0)}`",
        "",
        "## Domain Axis",
        "",
        "| Domain | Count |",
        "|---|---:|",
        *_count_lines(rows, "domain"),
        "",
        "## Answer Type Axis",
        "",
        "| Answer Type | Count |",
        "|---|---:|",
        *_count_lines(rows, "answer_type"),
        "",
        "## Proposed Subdomains",
        "",
    ]
    for domain, subdomains in get_single_hop_subdomain_plan().items():
        lines.append(f"- **{domain}**: {', '.join(subdomains)}")
    lines.extend(
        [
            "",
            "## Full Catalog",
            "",
            "| Domain | Subdomain | Template Key | Answer Type | Subject QID | Date PID | Target PID | Canonical Question | Candidate Search Query | Origin |",
            "|---|---|---|---|---|---|---|---|---|---|",
        ]
    )
    for row in rows:
        query = row["candidate_search_query"].replace("\n", "<br>")
        lines.append(
            "| {domain} | {subdomain} | {template_key} | {answer_type} | {subject_type_qid} | {date_property_pid} | {target_property_pid} | {canonical_question_template} | `{query}` | {origin} |".format(
                **{**row, "query": query}
            )
        )
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def main() -> int:
    rows = single_hop_catalog_as_dicts()
    json_path = ROOT / "docs" / "single_hop_template_catalog.json"
    markdown_path = ROOT / "docs" / "single_hop_template_catalog.md"
    xlsx_path = ROOT / "docs" / "single_hop_template_catalog_review.xlsx"
    export_json(json_path, rows)
    export_markdown(markdown_path, rows)
    export_review_xlsx(xlsx_path, rows)
    print(
        {
            "rows": len(rows),
            "json": str(json_path),
            "markdown": str(markdown_path),
            "xlsx": str(xlsx_path),
        }
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
