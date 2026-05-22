"""Export the reviewed Route 4 one-hop template catalog with user comments."""

from __future__ import annotations

import re
import sys
import zipfile
from pathlib import Path
from xml.etree import ElementTree
from xml.sax.saxutils import escape

ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "src"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))

from wikidata_simpleqa.route4_template_catalog import (  # noqa: E402
    DISCARDED_ROUTE4_TEMPLATE_KEYS,
    get_route4_reviewed_single_hop_templates,
    get_route4_reviewed_template_summary,
)
from wikidata_simpleqa.single_hop_template_catalog import single_hop_catalog_as_dicts  # noqa: E402


REVIEW_WORKBOOK = ROOT / "docs" / "single_hop_template_catalog_review.xlsx"
OUTPUT_WORKBOOK = ROOT / "docs" / "route4_one_hop_template_review.xlsx"
NS = {"main": "http://schemas.openxmlformats.org/spreadsheetml/2006/main"}


def _status_label(status: str) -> str:
    """Return a short human-readable status label for review."""
    normalized = status.strip()
    if not normalized:
        return "Untracked"
    return normalized.replace("_", " ").title()


def _load_existing_statuses() -> dict[str, str]:
    """Load legacy template statuses from the generated review Markdown."""
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


def _original_review_rows_with_keys() -> list[dict[str, str]]:
    """Rebuild the original sheet-1 review order, keeping hidden template keys."""
    statuses = _load_existing_statuses()
    rows: list[dict[str, str]] = []
    for row in single_hop_catalog_as_dicts():
        legacy_key = row.get("legacy_template_key", "")
        status = statuses.get(legacy_key, "New") if legacy_key else "New"
        rows.append(
            {
                "template_key": row["template_key"],
                "domain": row["domain"],
                "subdomain": row["subdomain"],
                "answer_type": row["answer_type"],
                "canonical_question_template": row["canonical_question_template"],
                "existing_status": status,
            }
        )
    rows.sort(
        key=lambda row: (
            row["domain"],
            row["subdomain"],
            row["existing_status"] != "New",
            row["canonical_question_template"],
        )
    )
    return rows


def _column_index(cell_ref: str) -> int:
    """Return a zero-based column index from an Excel cell reference."""
    letters = re.match(r"([A-Z]+)", cell_ref)
    if not letters:
        return 0
    index = 0
    for char in letters.group(1):
        index = index * 26 + ord(char) - ord("A") + 1
    return index - 1


def _shared_strings(workbook: zipfile.ZipFile) -> list[str]:
    """Read the shared string table from an XLSX archive."""
    try:
        xml = workbook.read("xl/sharedStrings.xml")
    except KeyError:
        return []
    root = ElementTree.fromstring(xml)
    values: list[str] = []
    for item in root.findall("main:si", NS):
        parts = [text.text or "" for text in item.findall(".//main:t", NS)]
        values.append("".join(parts))
    return values


def _cell_text(cell: ElementTree.Element, shared: list[str]) -> str:
    """Read text from one XLSX worksheet cell."""
    cell_type = cell.attrib.get("t")
    if cell_type == "s":
        value = cell.find("main:v", NS)
        if value is None or value.text is None:
            return ""
        return shared[int(value.text)]
    if cell_type == "inlineStr":
        parts = [text.text or "" for text in cell.findall(".//main:t", NS)]
        return "".join(parts)
    value = cell.find("main:v", NS)
    return value.text if value is not None and value.text is not None else ""


def _sheet_rows(workbook: zipfile.ZipFile, sheet_index: int) -> list[list[str]]:
    """Read a worksheet as a rectangular list of rows."""
    shared = _shared_strings(workbook)
    xml = workbook.read(f"xl/worksheets/sheet{sheet_index}.xml")
    root = ElementTree.fromstring(xml)
    rows: list[list[str]] = []
    for row in root.findall(".//main:sheetData/main:row", NS):
        values: list[str] = []
        for cell in row.findall("main:c", NS):
            column = _column_index(cell.attrib.get("r", "A1"))
            while len(values) <= column:
                values.append("")
            values[column] = _cell_text(cell, shared)
        rows.append(values)
    return rows


def _review_workbook_rows() -> tuple[list[list[str]], list[list[str]]]:
    """Read the user's reviewed workbook sheets."""
    with zipfile.ZipFile(REVIEW_WORKBOOK) as workbook:
        sheet1 = _sheet_rows(workbook, 1)
        sheet2 = _sheet_rows(workbook, 2)
    return sheet1, sheet2


def _sheet1_comments_by_template_key(sheet1_rows: list[list[str]]) -> dict[str, str]:
    """Map comments from the original first review sheet to template keys."""
    original_rows = _original_review_rows_with_keys()
    if not sheet1_rows:
        return {}
    headers = sheet1_rows[0]
    try:
        comment_index = headers.index("Comments")
    except ValueError:
        comment_index = 5

    comments: dict[str, str] = {}
    for index, original in enumerate(original_rows, start=1):
        if index >= len(sheet1_rows):
            break
        row = sheet1_rows[index]
        comment = row[comment_index].strip() if comment_index < len(row) else ""
        if comment and original["template_key"] not in DISCARDED_ROUTE4_TEMPLATE_KEYS:
            comments[original["template_key"]] = comment
    return comments


def _sheet2_comments_by_template_key(sheet2_rows: list[list[str]]) -> dict[str, str]:
    """Map notes from the user's second-sheet templates to new Route 4 keys."""
    new_templates = [
        template
        for template in get_route4_reviewed_single_hop_templates()
        if template.reasoning_recipe.get("source") == "user_review_sheet_2"
    ]
    data_rows = [row for row in sheet2_rows if row and any(cell.strip() for cell in row)]
    comments: dict[str, str] = {}
    for template, row in zip(new_templates, data_rows, strict=False):
        notes = [cell.strip() for cell in row[1:] if cell.strip()]
        if notes:
            comments[template.template_key] = " | ".join(notes)
    return comments


def _display_status(template) -> str:
    """Return the review status label for a Route 4 template."""
    if template.reasoning_recipe.get("source") == "user_review_sheet_2":
        return "User New"
    legacy_key = template.reasoning_recipe.get("legacy_template_key", "")
    if not legacy_key:
        return "New"
    return _load_existing_statuses().get(legacy_key, "New")


def _template_rows() -> list[dict[str, str]]:
    """Return final workbook rows for non-discarded reviewed Route 4 templates."""
    sheet1_rows, sheet2_rows = _review_workbook_rows()
    comments = {
        **_sheet1_comments_by_template_key(sheet1_rows),
        **_sheet2_comments_by_template_key(sheet2_rows),
    }
    rows: list[dict[str, str]] = []
    for template in get_route4_reviewed_single_hop_templates():
        rows.append(
            {
                "Domain": template.template_domain,
                "Subdomain": template.reasoning_recipe.get("subdomain", ""),
                "Answer Type": template.answer_type,
                "Canonical Template": template.canonical_question_template,
                "Existing Status": _display_status(template),
                "Comments": comments.get(template.template_key, ""),
                "Template Key": template.template_key,
                "Subject QID": template.subject_type_qid,
                "Date PID": template.date_property_pid,
                "Target PID": template.target_property_pid,
                "Answer Format": template.answer_format,
            }
        )
    rows.sort(
        key=lambda row: (
            row["Domain"],
            row["Subdomain"],
            row["Existing Status"] != "New",
            row["Canonical Template"],
        )
    )
    return rows


def _column_name(index: int) -> str:
    """Return the Excel column name for a one-based column index."""
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


def export_xlsx(path: Path, rows: list[dict[str, str]]) -> None:
    """Write the Route 4 one-hop review workbook."""
    path.parent.mkdir(parents=True, exist_ok=True)
    fieldnames = [
        "Domain",
        "Subdomain",
        "Answer Type",
        "Canonical Template",
        "Existing Status",
        "Comments",
        "Template Key",
        "Subject QID",
        "Date PID",
        "Target PID",
        "Answer Format",
    ]
    all_rows = [dict(zip(fieldnames, fieldnames, strict=False)), *rows]
    last_column = _column_name(len(fieldnames))
    dimension = f"A1:{last_column}{len(all_rows)}"
    widths = {
        "Domain": 34,
        "Subdomain": 28,
        "Answer Type": 16,
        "Canonical Template": 88,
        "Existing Status": 18,
        "Comments": 44,
        "Template Key": 44,
        "Subject QID": 14,
        "Date PID": 12,
        "Target PID": 12,
        "Answer Format": 16,
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
  <sheets><sheet name="Route4 One-Hop Review" sheetId="1" r:id="rId1"/></sheets>
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


def main() -> int:
    rows = _template_rows()
    export_xlsx(OUTPUT_WORKBOOK, rows)
    summary = get_route4_reviewed_template_summary()
    commented_rows = sum(1 for row in rows if row["Comments"])
    discarded_comments = sum(1 for row in rows if "discard" in row["Comments"].lower())
    print(
        {
            "rows": len(rows),
            "commented_rows": commented_rows,
            "discarded_comment_rows": discarded_comments,
            "route4_total": summary["total"],
            "xlsx": str(OUTPUT_WORKBOOK),
        }
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
