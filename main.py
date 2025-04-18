
import os
import re
import tempfile

import pdfplumber
import pandas as pd
from docx import Document
from docx2pdf import convert

# ---------------------------
# Utility: redact strikethrough runs and convert .docx → .pdf
# ---------------------------
class StrikethroughRedactor:
    """
    Remove any strike-through text from a .docx file, and produce a cleaned PDF.
    """
    def __init__(self, docx_path: str):
        self.docx_path = docx_path
        self.doc = Document(docx_path)
    
    def redact(self):
        """Strip out all runs with font.strike=True."""
        for para in self.doc.paragraphs:
            for run in para.runs:
                if run.font.strike:
                    run.text = ""
    
    def to_pdf(self, output_pdf_path: str):
        """
        Save the modified .docx to a temp file and convert it to PDF.
        The temp file is removed afterwards.
        """
        fd, tmp_path = tempfile.mkstemp(suffix=".docx")
        os.close(fd)
        try:
            self.doc.save(tmp_path)
            convert(tmp_path, output_pdf_path)
        finally:
            if os.path.exists(tmp_path):
                os.remove(tmp_path)

# ---------------------------
# Text + tables extraction from a single pdfplumber page
# ---------------------------
def extract_text_and_tables(page):
    text = page.extract_text() or ""
    tables = page.find_tables()
    if not tables:
        return text

    # sort tables by their vertical position
    tables = sorted(tables, key=lambda t: t.bbox[1])
    lines = text.split("\n")
    out, ti = "", 0  # ti = index into tables

    for line in lines:
        # find approximate line y‑position
        # (pdfplumber doesn’t easily map text → bbox, so we assume tables are interleaved roughly in order)
        # whenever our next table’s top edge is “before” we’d place more text,
        # dump the table first
        while ti < len(tables):
            tbl = tables[ti]
            # heuristic: if we've written more lines than the table’s row‑count,
            # assume it belongs here
            if len(out.split("\n")) >= tbl.bbox[1] // 10:
                break
            # otherwise embed the table now
            out += "\n[TABLE]\n"
            for row in tbl.extract():
                row = [cell.strip() if cell else "" for cell in row]
                out += " | ".join(row) + "\n"
            out += "[/TABLE]\n\n"
            ti += 1
        out += line + "\n"

    # any leftover tables
    while ti < len(tables):
        tbl = tables[ti]
        out += "\n[TABLE]\n"
        for row in tbl.extract():
            row = [cell.strip() if cell else "" for cell in row]
            out += " | ".join(row) + "\n"
        out += "[/TABLE]\n\n"
        ti += 1

    return out

# ---------------------------
# Pull out a “Date: …” line (first match) and compile full text
# ---------------------------
DATE_RE = re.compile(r"^date:\s*(.*)$", re.IGNORECASE)

def extract_future_memos(pdf_path: str) -> pd.DataFrame:
    """
    Open PDF, extract all pages’ text+tables, look for the first “Date: …” line,
    and return a 1‑row DataFrame with:
      - doc_name
      - doc_type      (always “OPS Memo” here)
      - chapter       (hardcoded “Chapter 1”)
      - sub_chapter   (hardcoded “sub chapter 1”)
      - date_modified (the raw “Date: …” line, or None)
      - document      (the full combined text with [TABLE] markers)
    """
    all_lines = []
    found_date = None

    with pdfplumber.open(pdf_path) as pdf:
        for page in pdf.pages:
            txt = extract_text_and_tables(page)
            for line in txt.splitlines():
                all_lines.append(line)
                if found_date is None:
                    m = DATE_RE.match(line.strip())
                    if m:
                        found_date = m.group(1).strip()

    full_text = "\n".join(all_lines)
    df = pd.DataFrame([{
        "doc_name": os.path.basename(pdf_path),
        "doc_type": "OPS Memo",
        "chapter": "Chapter 1",
        "sub_chapter": "sub chapter 1",
        "date_modified": found_date,
        "document": full_text
    }])
    return df

# ---------------------------
# Try parsing any obvious date formats; else return raw string
# ---------------------------
def extract_date(raw):
    try:
        # Month names or M/D/YYYY
        patterns = [
            r"(?:January|February|March|April|May|June|July|August|September|October|November|December)\s+\d{1,2},\s+\d{4}",
            r"\b\d{1,2}/\d{1,2}/\d{2,4}\b"
        ]
        matches = []
        for pat in patterns:
            matches += re.findall(pat, str(raw))
        if matches:
            # take the latest one chronologically
            dates = pd.to_datetime(matches)
            return dates.max().date()
    except Exception:
        pass
    return raw

# ---------------------------
# Main orchestration
# ---------------------------
def process_directory(input_dir: str) -> pd.DataFrame:
    """
    Walk `input_dir`, handle .docx → PDF conversion (with redaction),
    then run extraction on each PDF, returning a concatenated DataFrame.
    """
    dfs = []
    for fname in os.listdir(input_dir):
        path = os.path.join(input_dir, fname)
        lower = fname.lower()
        # skip hidden / non‑files
        if not os.path.isfile(path) or fname.startswith("."):
            continue

        # If Word doc, redact & convert
        if lower.endswith(".docx"):
            redactor = StrikethroughRedactor(path)
            redactor.redact()
            pdf_path = path[:-5] + ".pdf"
            redactor.to_pdf(pdf_path)
        # If it's already a PDF, just use it
        elif lower.endswith(".pdf"):
            pdf_path = path
        else:
            # ignore everything else
            continue

        # Extract into a 1‑row DataFrame
        df = extract_future_memos(pdf_path)

        # Clean & parse date
        df = df.rename(columns={"doc_type": "Document Type"})
        df["date_modified_filter"] = df["date_modified"].apply(extract_date)
        df = df.drop(columns=["date_modified"])

        dfs.append(df)

    # Combine all into one table
    if dfs:
        return pd.concat(dfs, ignore_index=True)
    else:
        return pd.DataFrame()

if __name__ == "__main__":
    # 1) Point this at your folder of .docx/.pdf files:
    INPUT_FOLDER = "path/to/your/docs"

    final_df = process_directory(INPUT_FOLDER)
    pd.set_option("display.max_colwidth", None)
    print(final_df)
