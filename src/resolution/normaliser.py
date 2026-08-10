from __future__ import annotations
import unicodedata
import re

LEGAL_SUFFIXES = [
    r"\binc\b\.?", r"\bincorporated\b", r"\bcorp\b\.?", r"\bcorporation\b",
    r"\bllc\b", r"\bltd\b\.?", r"\blimited\b", r"\bco\b\.?", r"\bcompany\b",
    r"\bgmbh\b", r"\bag\b", r"\bplc\b", r"\bsa\b", r"\bpte\b",
]
SUFFIX_PATTERN = re.compile(r"(" + "|".join(LEGAL_SUFFIXES) + r")$", re.IGNORECASE)


def normalise_name(name: str) -> str:
    """
    Core canonicalisation for entity names.
    - Unicode NFC normalization
    - Lowercase
    - Strip legal suffixes
    - Remove punctuation
    - Collapse whitespace
    """
    if not name:
        return ""

    # 1. Unicode normalisation (NFC)
    name = unicodedata.normalize("NFC", str(name))

    # 2. Lowercase
    name = name.lower()

    # 3. Strip trailing legal suffixes (may need multiple passes if "co ltd")
    prev = ""
    while name != prev:
        prev = name
        name = SUFFIX_PATTERN.sub("", name).strip()

    # 4. Remove punctuation
    name = re.sub(r"[^\w\s]", "", name)

    # 5. Collapse whitespace
    name = re.sub(r"\s+", " ", name).strip()

    return name
