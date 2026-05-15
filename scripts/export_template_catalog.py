"""Export the current template catalog for manual review."""

from __future__ import annotations

import sys
import zipfile
from collections import Counter
from pathlib import Path
from xml.sax.saxutils import escape

ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "src"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))

from wikidata_simpleqa.template_status import build_template_status_index
from wikidata_simpleqa.workflow import (
    status_accepted_paths,
    status_rejected_paths,
    status_summary_paths,
)


def _rows() -> list[dict[str, str]]:
    index = build_template_status_index(
        review_bundle_path=ROOT / "outputs" / "review_2026_all_generated_qas.tsv",
        summary_paths=status_summary_paths(ROOT),
        rejected_paths=status_rejected_paths(ROOT),
        accepted_paths=status_accepted_paths(ROOT),
        status_mode="latest_live_status",
    )
    rows: list[dict[str, str]] = []
    for template in index["templates"]:
        proven_example = template.get("proven_example") or {}
        rows.append(
            {
                "domain": str(template.get("domain", "")),
                "template": str(template.get("template_key", "")),
                "answer_type": str(template.get("answer_type", "")),
                "canonical_question": str(template.get("canonical_question_template", "")),
                "status": str(template.get("current_status", "")),
                "run_status": str(template.get("original_current_status", "")),
                "latest_live_status": str(template.get("latest_live_status", "")),
                "best_known_semantic_status": str(template.get("best_known_semantic_status", "")),
                "successful_generated_question": str(proven_example.get("question", "")),
            }
        )
    rows.sort(key=lambda row: (row["domain"], row["template"]))
    return rows


def _count_lines(rows: list[dict[str, str]], key: str) -> list[str]:
    counts = Counter(row[key] for row in rows)
    return [f"| {value} | {counts[value]} |" for value in sorted(counts)]


def _column_name(index: int) -> str:
    """Return the Excel column name for a 1-based column index."""
    name = ""
    while index:
        index, remainder = divmod(index - 1, 26)
        name = chr(65 + remainder) + name
    return name


def _sheet_cell(value: str, row_index: int, column_index: int, style: int | None = None) -> str:
    cell_reference = f"{_column_name(column_index)}{row_index}"
    style_attribute = f' s="{style}"' if style is not None else ""
    return (
        f'<c r="{cell_reference}" t="inlineStr"{style_attribute}>'
        f'<is><t xml:space="preserve">{escape(value)}</t></is>'
        "</c>"
    )


def export_xlsx(path: Path, rows: list[dict[str, str]]) -> None:
    """Write the catalog as a dependency-free XLSX workbook."""
    path.parent.mkdir(parents=True, exist_ok=True)
    fieldnames = list(rows[0].keys()) if rows else []
    all_rows = [dict(zip(fieldnames, fieldnames, strict=False)), *rows] if fieldnames else []
    last_column = _column_name(len(fieldnames)) if fieldnames else "A"
    dimension = f"A1:{last_column}{max(len(all_rows), 1)}"
    column_widths = []
    for column_index, fieldname in enumerate(fieldnames, start=1):
        values = [fieldname, *(row.get(fieldname, "") for row in rows)]
        width = max(10, min(70, max(len(value) for value in values) + 2))
        column_widths.append(
            f'<col min="{column_index}" max="{column_index}" width="{width}" customWidth="1"/>'
        )
    worksheet_rows = []
    for row_index, row in enumerate(all_rows, start=1):
        cells = [
            _sheet_cell(row.get(fieldname, ""), row_index, column_index, style=1 if row_index == 1 else None)
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
  <sheets><sheet name="Template Catalog Review" sheetId="1" r:id="rId1"/></sheets>
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


def export_markdown(path: Path, rows: list[dict[str, str]]) -> None:
    """Write the catalog as Markdown with simple review stats."""
    path.parent.mkdir(parents=True, exist_ok=True)
    lines = [
        "# Template Catalog Review",
        "",
        "## Headline Stats",
        "",
        f"- Total templates: `{len(rows)}`",
        "",
        "## Status Axis",
        "",
        "| Status | Count |",
        "|---|---:|",
        *_count_lines(rows, "status"),
        "",
        "## Run-Derived Status Axis",
        "",
        "| Run Status | Count |",
        "|---|---:|",
        *_count_lines(rows, "run_status"),
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
        "## Full Catalog",
        "",
        "| Domain | Template | Answer Type | Canonical Question | Status | Successful Generated Question |",
        "|---|---|---|---|---|---|",
    ]
    for row in rows:
        lines.append(
            "| {domain} | {template} | {answer_type} | {canonical_question} | {status} | {successful_generated_question} |".format(
                **row
            )
        )
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def main() -> int:
    rows = _rows()
    export_xlsx(ROOT / "docs" / "template_catalog_review.xlsx", rows)
    export_markdown(ROOT / "docs" / "template_catalog_review.md", rows)
    print(
        {
            "rows": len(rows),
            "xlsx": str(ROOT / "docs" / "template_catalog_review.xlsx"),
            "markdown": str(ROOT / "docs" / "template_catalog_review.md"),
        }
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
