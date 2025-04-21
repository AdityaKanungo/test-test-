import os
import re

import pdfplumber
import pandas as pd

# Pattern to match lines starting with 'Date:' (case-insensitive)
DATE_RE = re.compile(r"^date:\s*(.*)$", re.IGNORECASE)

class PolicyTextextractor:
    """
    Scans a directory for PDF files, extracts text and tables,
    identifies document dates, and compiles everything into a DataFrame.
    """
    def __init__(self, input_dir: str):
        self.input_dir = input_dir

    def extract_text_and_tables(self, page) -> str:
        """
        Extract text from a pdfplumber page, embedding any tables
        within [TABLE]...[/TABLE] markers in their document order.
        """
        text = page.extract_text() or ""
        tables = page.find_tables()
        if not tables:
            return text

        tables = sorted(tables, key=lambda t: t.bbox[1])
        lines = text.split("\n")
        out_lines = []
        ti = 0

        for line in lines:
            # Insert tables that appear before this line
            while ti < len(tables) and len(out_lines) >= int(tables[ti].bbox[1] // 10):
                tbl = tables[ti]
                out_lines.append("[TABLE]")
                for row in tbl.extract():
                    cells = [cell.strip() if cell else "" for cell in row]
                    out_lines.append(" | ".join(cells))
                out_lines.append("[/TABLE]\n")
                ti += 1
            out_lines.append(line)

        # Append any remaining tables
        while ti < len(tables):
            tbl = tables[ti]
            out_lines.append("[TABLE]")
            for row in tbl.extract():
                cells = [cell.strip() if cell else "" for cell in row]
                out_lines.append(" | ".join(cells))
            out_lines.append("[/TABLE]\n")
            ti += 1

        return "\n".join(out_lines)

    def extract_date(self, raw) -> pd.Timestamp or str:
        """
        Parse out known date formats (e.g., 'January 1, 2025' or '1/1/2025')
        from a raw string. Returns the latest parsed date or the raw value if
        parsing fails.
        """
        try:
            patterns = [
                r"(?:January|February|March|April|May|June|July|August|September|October|November|December)\s+\d{1,2},\s+\d{4}",
                r"\b\d{1,2}/\d{1,2}/\d{2,4}\b"
            ]
            matches = []
            for pat in patterns:
                matches += re.findall(pat, str(raw))
            if matches:
                dates = pd.to_datetime(matches, errors='coerce')
                return dates.max().date()
        except Exception:
            pass
        return raw

    def extract_future_memos(self, pdf_path: str) -> pd.DataFrame:
        """
        For a given PDF, extract all text and tables, find the first
        'Date:' line as the document's date, and return a single-row
        DataFrame with metadata and content.
        """
        all_lines = []
        found_date = None

        with pdfplumber.open(pdf_path) as pdf:
            for page in pdf.pages:
                txt = self.extract_text_and_tables(page)
                for line in txt.splitlines():
                    all_lines.append(line)
                    if found_date is None:
                        m = DATE_RE.match(line.strip())
                        if m:
                            found_date = m.group(1).strip()

        full_text = "\n".join(all_lines)
        df = pd.DataFrame([{
            "doc_name": os.path.basename(pdf_path),
            "Document Type": "OPS Memo",
            "chapter": "Chapter 1",
            "sub_chapter": "sub chapter 1",
            "date_modified": found_date,
            "document": full_text
        }])

        # Parse and filter date, then drop the raw column
        df["date_modified_filter"] = df["date_modified"].apply(self.extract_date)
        return df.drop(columns=["date_modified"])

    def run(self) -> pd.DataFrame:
        """
        Process all PDFs in input_dir and return a concatenated DataFrame.
        """
        records = []
        for fname in os.listdir(self.input_dir):
            if not fname.lower().endswith('.pdf'):
                continue
            path = os.path.join(self.input_dir, fname)
            if os.path.isfile(path):
                records.append(self.extract_future_memos(path))

        if records:
            return pd.concat(records, ignore_index=True)
        return pd.DataFrame()

if __name__ == "__main__":
    INPUT_FOLDER = "path/to/your/pdfs"
    extractor = PolicyTextextractor(INPUT_FOLDER)
    result_df = extractor.run()
    pd.set_option("display.max_colwidth", None)
    print(result_df)
