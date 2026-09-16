from pathlib import Path
import pandas as pd
import re

# ==========================================
# CONFIGURATION
# ==========================================

EXCEL_FILE = "Applikationsprofiler Official RDA.xlsx"
ROOT_DIR = "."

BEGIN_MARKER = "<!-- BEGIN METADATA -->"
END_MARKER = "<!-- END METADATA -->"

# ==========================================
# LOAD ALL SHEETS
# ==========================================

sheets = pd.read_excel(EXCEL_FILE, sheet_name=None)

required_columns = [
    "RDA engelska",
    "RDA svenska",
    "Entitet",
    "Libris",
    "Obligatoriskt",
    "Repeterbart",
    "Kommentar",
]

# ==========================================
# FIND ALL MARKDOWN FILES
# ==========================================

markdown_files = {
    p.stem.lower(): p
    for p in Path(ROOT_DIR).rglob("*.md")
}

updated = 0
missing_files = []

# ==========================================
# PROCESS EACH SHEET
# ==========================================

for sheet_name, df in sheets.items():

    if "RDA engelska" not in df.columns:
        continue

    for _, row in df.iterrows():

        if pd.isna(row.get("RDA engelska")):
            continue

        element_name = str(row["RDA engelska"]).strip()

        filename = (
            element_name.lower()
            .replace(" ", "-")
            .replace("/", "-")
        )

        md_file = markdown_files.get(filename)

        if not md_file:
            missing_files.append(filename)
            continue

        rda_sv = str(row.get("RDA svenska", "")).strip()
        entity = str(row.get("Entitet", "")).strip()
        libris = str(row.get("Libris", "")).strip()
        mandatory = str(row.get("Obligatoriskt", "")).strip()
        repeatable = str(row.get("Repeterbart", "")).strip()
        comment = str(row.get("Kommentar", "")).strip()

        table = f"""
{BEGIN_MARKER}

| Fält | Värde |
|-------|--------|
| RDA svenska | {rda_sv} |
| Entitet | {entity} |
| Libris | {libris} |
| Obligatoriskt | {mandatory} |
| Repeterbart | {repeatable} |

## Kommentar

{comment}

{END_MARKER}
""".strip()

        content = md_file.read_text(encoding="utf-8")

        pattern = re.compile(
            re.escape(BEGIN_MARKER)
            + r".*?"
            + re.escape(END_MARKER),
            re.DOTALL
        )

        if pattern.search(content):
            content = pattern.sub(table, content)
        else:
            content = table + "\n\n" + content

        md_file.write_text(content, encoding="utf-8")
        updated += 1

print(f"Updated: {updated}")

if missing_files:
    print("\nNo matching markdown file found for:")
    for item in sorted(set(missing_files)):
        print(f"  - {item}")