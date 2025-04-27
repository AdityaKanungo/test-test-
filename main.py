import re
from docx import Document

def _has_tables(self, doc: Document) -> bool:
    """
    Return True if there is any table in `doc` *other than* one that:
      • contains the words 'subject', 'to', and 'from' (in any cells), OR
      • is composed entirely of date strings.
    """
    header_keywords = {"subject", "to", "from"}
    # match letter-only tokens (with optional trailing colon)
    word_pattern = re.compile(r"\b([A-Za-z]+):?\b")
    # match dates like "MM/DD/YYYY", "M/D/YY", or ISO "YYYY-MM-DD"
    date_pattern = re.compile(r"^(?:\d{1,2}[/-]\d{1,2}[/-]\d{2,4}|\d{4}-\d{2}-\d{2})$")

    for table in doc.tables:
        # 1) grab all text for header-keyword detection
        combined = " ".join(
            cell.text for row in table.rows for cell in row.cells
        ).lower()

        # extract pure-word tokens
        raw_words = word_pattern.findall(combined)
        tokens = {w.rstrip(":") for w in raw_words}

        # if it has all header keywords, skip it
        if header_keywords.issubset(tokens):
            continue

        # 2) check for date-only tables
        #    collect every non-empty cell’s trimmed text
        cell_texts = [
            cell.text.strip()
            for row in table.rows
            for cell in row.cells
            if cell.text.strip()
        ]

        # if there is at least one cell, and *every* cell matches our date regex → skip
        if cell_texts and all(date_pattern.match(txt) for txt in cell_texts):
            continue

        # otherwise it’s a “real” table
        return True

    # no real tables found
    return False
