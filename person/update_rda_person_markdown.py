import pandas as pd
from pathlib import Path
import re

# ============================================================
# SETTINGS
# ============================================================

CSV_FILE = "test_Applikationsprofil_person.csv"
ROOT_DIR = "."

# ============================================================
# FILENAME MATCHING
# ============================================================

def possible_filenames(label):

    label = str(label).strip().lower()

    # Remove leading "has " or "has_"
    label = re.sub(r"^has[_ ]+", "", label)

    variants = {
        label.replace(" ", "-") + ".md",
        label.replace(" ", "_") + ".md",
        label.replace("_", "-") + ".md",
        label.replace("-", "_") + ".md",
    }

    return list(variants)

# ============================================================
# MARKDOWN GENERATION
# ============================================================

def build_profile_block(group):

    first = group.iloc[0]

    svenska = str(first["RDA element svenska"]).strip()
    engelska = str(first["RDA element engelska"]).strip()
    entitet = str(first["Entitet"]).strip()
    range_value = str(first["Range"]).strip()
    obligatoriskt = str(first["Obligatoriskt"]).strip()
    repeterbart = str(first["Repeterbart"]).strip()
    kommentar = str(first["Kommentar"]).strip()

    lines = []

    lines.append("| | |")
    lines.append("|---|---|")

    if svenska:
        lines.append(f"| **RDA element svenska** | {svenska} |")

    if engelska:
        lines.append(f"| **RDA element engelska** | {engelska} |")

    if entitet:
        lines.append(f"| **Entitet** | {entitet} |")

    if range_value:
        lines.append(f"| **Range** | {range_value} |")

    if obligatoriskt:
        lines.append(f"| **Obligatoriskt** | {obligatoriskt} |")

    if repeterbart:
        lines.append(f"| **Repeterbart** | {repeterbart} |")

    if kommentar:
        lines.append(f"| **Kommentar** | {kommentar} |")

    seen = set()

    for _, row in group.iterrows():

        label = str(row["Libris/KBV label"]).strip()
        iri = str(row["KBV IRI"]).strip()

        if not label and not iri:
            continue

        key = (label, iri)

        if key in seen:
            continue

        seen.add(key)

        lines.append("")
        lines.append("| | |")
        lines.append("|---|---|")
        lines.append(f"| **Libris/KBV label** | {label} |")
        lines.append(f"| **KBV IRI** | {iri} |")

    return "\n".join(lines)

# ============================================================
# INSERT / UPDATE GENERATED BLOCK
# ============================================================

def replace_profile(content, profile_block):

    start_marker = "<!-- APPLICATION PROFILE START -->"
    end_marker = "<!-- APPLICATION PROFILE END -->"

    generated = (
        f"{start_marker}\n\n"
        f"{profile_block}\n\n"
        f"{end_marker}"
    )

    if start_marker in content and end_marker in content:

        pattern = (
            re.escape(start_marker)
            + r".*?"
            + re.escape(end_marker)
        )

        return re.sub(
            pattern,
            generated,
            content,
            flags=re.DOTALL
        )

    return generated + "\n\n" + content

# ============================================================
# LOAD CSV
# ============================================================

df = pd.read_csv(
    CSV_FILE,
    sep=";",
    encoding="utf-8-sig",
    dtype=str
).fillna("")

df.columns = [str(c).strip() for c in df.columns]

required = [
    "Entitet",
    "Range",
    "RDA element engelska"