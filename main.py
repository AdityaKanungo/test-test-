import re
from pathlib import Path
from datetime import date
import pandas as pd
import pdfplumber

class PolicyTextExtractor:
    # ——— pre-compiled regexes —————————————————————————————————————————————————
    SUBMISSION_RE = re.compile(r'^\s*submitted.*$', re.IGNORECASE)
    DATE_PATTERNS = [
        # e.g. “January 1, 2025”
        re.compile(
            r'(?:January|February|March|April|May|June|'
            r'July|August|September|October|November|December)'
            r'\s+\d{1,2},\s+\d{4}'
        ),
        # e.g. “1/1/2025” or “01/01/25”
        re.compile(r'\b\d{1,2}/\d{1,2}/\d{2,4}\b'),
    ]

    def extract_text_and_tables(self, page) -> str:
        """
        Extract text from a pdfplumber page, interleaving any tables
        wrapped in [TABLE]…[/TABLE], in their vertical order.
        """
        text = page.extract_text() or ""
        tables = sorted(page.find_tables(), key=lambda t: t.bbox[1])
        out_lines: list[str] = []
        tbl_i = 0

        for line in text.splitlines():
            # insert any tables that belong before this line
            while tbl_i < len(tables) and (tables[tbl_i].bbox[1] // 10) <= len(out_lines):
                out_lines.append("[TABLE]")
                for row in tables[tbl_i].extract():
                    cells = [(c.strip() if c else "") for c in row]
                    out_lines.append(" | ".join(cells))
                out_lines.append("[/TABLE]")
                tbl_i += 1

            out_lines.append(line)

        # append any remaining tables
        while tbl_i < len(tables):
            out_lines.append("[TABLE]")
            for row in tables[tbl_i].extract():
                cells = [(c.strip() if c else "") for c in row]
                out_lines.append(" | ".join(cells))
            out_lines.append("[/TABLE]")
            tbl_i += 1

        return "\n".join(out_lines)

    def parse_date(self, raw: str | None) -> date | str | None:
        """
        From a raw “submitted…” line, pull out any date patterns,
        parse them, and return the latest date object; if nothing
        matches or parsing fails, return the raw string (or None).
        """
        if not raw:
            return None

        found: list[str] = []
        for pat in self.DATE_PATTERNS:
            found += pat.findall(raw)

        if not found:
            return raw

        dates = pd.to_datetime(found, errors="coerce").dropna()
        return dates.max().date() if not dates.empty else raw

    def extract_document(self, pdf_path: Path, doc_type: str) -> pd.DataFrame:
        """
        Open one PDF, stitch all pages’ text+tables together, capture
        the first “submitted…” line, parse its date, and return a
        one‐row DataFrame.
        """
        all_lines: list[str] = []
        submission_line: str | None = None

        with pdfplumber.open(pdf_path) as pdf:
            for page in pdf.pages:
                page_txt = self.extract_text_and_tables(page)
                for line in page_txt.splitlines():
                    if submission_line is None and self.SUBMISSION_RE.match(line):
                        submission_line = line.strip()
                    all_lines.append(line)

        full_text = "\n".join(all_lines)
        parsed_date = self.parse_date(submission_line)

        return pd.DataFrame({
            "doc_name":      [pdf_path.name],
            "Document Type": [doc_type],
            "date_modified": [parsed_date],
            "document":      [full_text],
        })

    def extract_directory(self, directory: str, doc_type: str) -> pd.DataFrame:
        """
        Process all PDFs in `directory`, label them all as `doc_type`,
        and return the concatenated DataFrame.
        """
        records: list[pd.DataFrame] = []
        dir_path = Path(directory)

        for pdf_path in sorted(dir_path.glob("*.pdf")):
            records.append(self.extract_document(pdf_path, doc_type))

        return pd.concat(records, ignore_index=True) if records else pd.DataFrame()


if __name__ == "__main__":
    # define your two input folders here:
    ops_memo_dir   = r"Adding documents to Index\Strikethrough\Input_files\OPS_Memos"
    clar_dir       = r"Adding documents to Index\Strikethrough\Input_files\Policy_Clarification"
    output_xlsx    = r"Adding documents to Index\Strikethrough\Extracted_Policy_Text.xlsx"

    extractor = PolicyTextExtractor()

    # extract each folder separately, with its own doc‐type label
    ops_df  = extractor.extract_directory(ops_memo_dir, "OPS Memo")
    clar_df = extractor.extract_directory(clar_dir,     "Policy Clarification")

    # combine them into one DataFrame
    result_df = pd.concat([ops_df, clar_df], ignore_index=True)

    # inspect & write out
    print(result_df)
    result_df.to_excel(output_xlsx, index=False)