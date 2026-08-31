from pathlib import Path
import pandas as pd
import re

# ============================================================
# CONFIGURATION
# ============================================================

SCRIPT_FOLDER = Path(__file__).parent

# Change this if needed
CSV_FILE = SCRIPT_FOLDER / "test_Applikationsprofil_person.csv"

ROOT_FOLDER = SCRIPT_FOLDER

# ============================================================
# COLUMN NAMES
# ============================================================

COL_ENTITY = "Entitet"
COL_RANGE = "Range"
COL_ENGLISH = "RDA element eng"
COL_IRI = "IRI"
COL_SWEDISH = "RDA element sv"
COL_LIBRIS = "Libris/KBV label"
COL_KBV_IRI = "KBV IRI"
COL_CARDINALITY = "Kardinalitet RDA-KBV"
COL_MANDATORY = "Obligatoriskt"
COL_REPEATABLE = "Repeterbart"
COL_COMMENT = "Kommentar"

# ============================================================
# HELPERS
# ============================================================

def normalize_label(text):
    text = str(text).strip().lower()

    if text.startswith("has "):
        text = text[4:]

    text = text.replace("-", " ")
    text = text.replace("_", " ")

    return " ".join(text.split())


def make_link(url):
    url = str(url).strip()

    if not url:
        return ""

    return f'{url}{url}</a>'


def find_md_file(label):

    target = normalize_label(label)

    print(f"\nLooking for: {target}")

    for md_file in ROOT_FOLDER.rglob("*.md"):

        filename = normalize_label(md_file.stem)

        print(f"   comparing with: {filename}")

        if filename == target:
            print(f"   MATCH: {md_file}")
            return md_file

    print("   NO MATCH")
    return None


def create_metadata_block(row):

    return f"""
<!-- METADATA START -->

<table>
<tr><td><strong>Entitet</strong></td><td>{row[COL_ENTITY]}</td></tr>
<tr><td><strong>Range</strong></td><td>{row[COL_RANGE]}</td></tr>
<tr><td><strong>RDA element engelska</strong></td><td>{row[COL_ENGLISH]}</td></tr>
<tr><td><strong>IRI</strong></td><td>{make_link(row[COL_IRI])}</td></tr>
<tr><td><strong>RDA element svenska</strong></td><td>{row[COL_SWEDISH]}</td></tr>
<tr><td><strong>Libris/KBV label</strong></td><td>{row[COL_LIBRIS]}</td></tr>
<tr><td><strong>KBV IRI</strong></td><td>{make_link(row[COL_KBV_IRI])}</td></tr>
<tr><td><strong>Kardinalitet RDA-KBV</strong></td><td>{row[COL_CARDINALITY]}</td></tr>
<tr><td><strong>Obligatoriskt</strong></td><td>{row[COL_MANDATORY]}</td></tr>
<tr><td><strong>Repeterbart</strong></td><td>{row[COL_REPEATABLE]}</td></tr>
<tr><td><strong>Kommentar</strong></td><td>{row[COL_COMMENT]}</td></tr>
</table>

<!-- METADATA END -->
""".strip()


def update_markdown(md_file, metadata, heading):

    text = md_file.read_text(encoding="utf-8")

    lines = text.splitlines()

    if lines and lines[0].startswith("#"):
        lines[0] = f"# {heading}"
    else:
        lines.insert(0, f"# {heading}")

    text = "\n".join(lines)

    start_marker = "<!-- METADATA START -->"
    end_marker = "<!-- METADATA END -->"

    if start_marker in text and end_marker in text:

        pattern = re.compile(
            rf"{re.escape(start_marker)}.*?{re.escape(end_marker)}",
            re.DOTALL,
        )

        text = pattern.sub(metadata, text)

    else:

        lines = text.splitlines()

        text = (
            lines[0]
            + "\n\n"
            + metadata
            + "\n\n"
            + "\n".join(lines[1:])
        )

    md_file.write_text(text, encoding="utf-8")


# ============================================================
# LOAD CSV
# ============================================================

print("\nUsing CSV:")
print(CSV_FILE.resolve())

df = pd.read_csv(
    CSV_FILE,
    sep=";",
    encoding="utf-8-sig",
    dtype=str
)

df.columns = df.columns.str.strip()
df = df.fillna("")

print("\nCSV columns found:")

for col in df.columns:
    print(f" - {col}")

# ============================================================
# VALIDATE
# ============================================================

required = [
    COL_ENTITY,
    COL_RANGE,
    COL_ENGLISH,
    COL_IRI,
    COL_SWEDISH,
    COL_LIBRIS,
    COL_KBV_IRI,
    COL_CARDINALITY,
    COL_MANDATORY,
    COL_REPEATABLE,
    COL_COMMENT,
]

missing = [c for c in required if c not in df.columns]

if missing:
    print("\nMissing columns:")
    for col in missing:
        print(f" - {col}")

    raise SystemExit(1)

# ============================================================
# SHOW MARKDOWN FILES
# ============================================================

print("\nMarkdown files found:\n")

for md_file in ROOT_FOLDER.rglob("*.md"):
    print(md_file)

# ============================================================
# PROCESS
# ============================================================

updated = 0
not_found = []

for _, row in df.iterrows():

    english_label = str(row[COL_ENGLISH]).strip()

    if not english_label:
        continue

    md_file = find_md_file(english_label)

    if md_file is None:
        not_found.append(english_label)
        continue

    metadata = create_metadata_block(row)

    update_markdown(
        md_file,
        metadata,
        english_label
    )

    print(f"UPDATED: {md_file}")

    updated += 1

# ============================================================
# SUMMARY
# ============================================================

print("\n================================")
print(f"Updated files: {updated}")
print(f"Missing files: {len(not_found)}")

if not_found:

    print("\nElements with no matching .md file:")

    for item in not_found:
        print(f" - {item}")