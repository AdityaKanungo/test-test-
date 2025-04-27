import re
from docx import Document

def _has_tables(self, doc: Document) -> bool:
    """
    Return True if there is any table in `doc` *other than* one
    that contains the words 'subject', 'to', and 'from' (in any cells).
    We'll print out the tokens for each table so you can debug why
    your header-only table is still getting counted.
    """
    header_keywords = {"subject", "to", "from"}
    # regex finds sequences of letters plus an optional trailing colon
    pattern = re.compile(r"\b([A-Za-z]+):?\b")

    for idx, table in enumerate(doc.tables):
        # gather all the raw text
        combined = " ".join(
            cell.text for row in table.rows for cell in row.cells
        )
        # find all “words” (with optional colon), lowercase, strip colon
        raw = pattern.findall(combined)
        tokens = {w.lower().rstrip(":") for w in raw}

        print(f"\nTable #{idx} raw text:\n{combined!r}")
        print(f"Table #{idx} tokens: {tokens}")

        if header_keywords.issubset(tokens):
            print(f" → Skipping table #{idx} (it has all of {header_keywords})")
            continue

        print(f" → Counting table #{idx} as “real.”")
        return True

    print("No “real” tables found.")
    return False
