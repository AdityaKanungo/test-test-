import re
from docx import Document

def _has_tables(self, doc: Document) -> bool:
    """
    Return True if there is any table in `doc` *other than* one that:
      • contains the words 'subject', 'to', and 'from', OR
      • is composed entirely of date strings in one of:
        – October 1, 2024
        – 12/07/2025
        – 12/07/25
        – 12-07-2025
        – 12-07-25
    """
    header_keywords = {"subject", "to", "from"}
    # match letter-only tokens (with optional trailing colon)
    word_pattern = re.compile(r"\b([A-Za-z]+):?\b")
    # match full month-name dates OR numeric dates with / or -
    month_names = (
        "January|February|March|April|May|June|July|"
        "August|September|October|November|December"
    )
    date_pattern = re.compile(
        rf"^(?:"
        rf"(?:{month_names})\s+\d{{1,2}},\s*\d{{4}}"
        rf"|\d{{1,2}}[/-]\d{{1,2}}[/-]\d{{2,4}}"
        rf")$",
        re.IGNORECASE
    )

    for table in doc.tables:
        # 1) header-keyword detection
        combined = " ".join(
            cell.text for row in table.rows for cell in row.cells
        ).lower()
        tokens = {w.rstrip(":") for w in word_pattern.findall(combined)}
        if header_keywords.issubset(tokens):
            continue

        # 2) date-only detection
        cell_texts = [
            cell.text.strip()
            for row in table.rows
            for cell in row.cells
            if cell.text.strip()
        ]
        if cell_texts and all(date_pattern.match(txt) for txt in cell_texts):
            continue

        # otherwise it’s a “real” table
        return True

    # no real tables found
    return False
