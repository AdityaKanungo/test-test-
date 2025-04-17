import os
import re
import pandas as pd
import pdfplumber
from datetime import datetime
from docx import Document
from fpdf import FPDF
from typing import List, Tuple

class PolicyTextExtractor:
    def __init__(self, folder_path: str):
        """
        Initialize the PolicyTextExtractor with a folder path.
        
        Args:
            folder_path (str): Path to the folder containing Word or PDF documents.
        """
        self.folder_path = folder_path
        self.submission_pattern = re.compile(r"^date:.*$", re.IGNORECASE)

    def process_documents(self) -> pd.DataFrame:
        """
        Process all documents (Word or PDF) in the given folder.

        Returns:
            pd.DataFrame: DataFrame containing extracted metadata and content for each document.
        """
        extracted_data = []

        for file_name in os.listdir(self.folder_path):
            full_path = os.path.join(self.folder_path, file_name)

            # Convert Word document to redacted PDF if needed
            if file_name.lower().endswith('.docx'):
                pdf_path = self.convert_docx_to_pdf_redacted(full_path)
            elif file_name.lower().endswith('.pdf'):
                pdf_path = full_path
            else:
                continue  # Skip unsupported formats

            # Extract metadata and text from the PDF
            doc_data = self.extract_future_memos(pdf_path)
            extracted_data.append(doc_data)

        return pd.DataFrame(extracted_data)

    def convert_docx_to_pdf_redacted(self, docx_path: str) -> str:
        """
        Convert Word document to PDF while redacting strikethrough text.

        Args:
            docx_path (str): Path to the .docx file.

        Returns:
            str: Path to the generated PDF file.
        """
        doc = Document(docx_path)
        redacted_text = []

        for para in doc.paragraphs:
            line = ""
            for run in para.runs:
                # Skip text with strikethrough
                if run.font.strike:
                    continue
                line += run.text
            redacted_text.append(line)

        # Create PDF and write redacted content
        pdf_path = docx_path.replace(".docx", "_redacted.pdf")
        pdf = FPDF()
        pdf.add_page()
        pdf.set_auto_page_break(auto=True, margin=15)
        pdf.set_font("Arial", size=12)

        for line in redacted_text:
            pdf.multi_cell(0, 10, line)

        pdf.output(pdf_path)
        return pdf_path

    def extract_text_and_tables(self, page) -> str:
        """
        Extract both text and tables from a PDF page and preserve table positions in context.

        Args:
            page (pdfplumber.page.Page): PDF page object.

        Returns:
            str: Text content with table placeholders inserted in correct order.
        """
        content = page.extract_text() or ""
        tables = page.find_tables()

        if tables:
            tables_sorted = sorted(tables, key=lambda tbl: tbl.bbox[1], reverse=False)
            content_lines = content.split("\n") if content else []
            updated_content = ""
            current_line_y = page.bbox[1]

            for line in content_lines:
                line_bbox = page.within_bbox(page.bbox).search(line, regex=False)
                line_top = line_bbox[0]['top'] if line_bbox else current_line_y

                # Insert tables before current line if they appear above it
                while tables_sorted and line_top > tables_sorted[0].bbox[1]:
                    table = tables_sorted.pop(0)
                    table_content = "\n[TABLE]\n"
                    for row in table.extract():
                        cleaned_row = ['' if cell is None else cell.strip() for cell in row]
                        table_content += ' | '.join(cleaned_row) + "\n"
                    table_content += "[/TABLE]\n"
                    updated_content += table_content

                updated_content += line + "\n"
                current_line_y = line_top

            # Add any remaining tables at the end
            for table in tables_sorted:
                table_content = "\n[TABLE]\n"
                for row in table.extract():
                    cleaned_row = ['' if cell is None else cell.strip() for cell in row]
                    table_content += ' | '.join(cleaned_row) + "\n"
                table_content += "[/TABLE]\n"
                updated_content += table_content

            return updated_content
        return content

    def extract_future_memos(self, pdf_path: str) -> dict:
        """
        Extract the full text and metadata from a given PDF document.

        Args:
            pdf_path (str): Path to the PDF file.

        Returns:
            dict: Dictionary containing metadata and full document text.
        """
        all_text_lines = []
        submission_date = None

        with pdfplumber.open(pdf_path) as pdf:
            for page in pdf.pages:
                page_text = self.extract_text_and_tables(page)
                if not page_text:
                    continue

                lines = page_text.splitlines()
                for line in lines:
                    all_text_lines.append(line)
                    if submission_date is None and self.submission_pattern.match(line.strip()):
                        submission_date = line.strip()

        full_text = "\n".join(all_text_lines)
        parsed_date = self.extract_date(full_text)

        return {
            'doc_name': os.path.basename(pdf_path),
            'doc_type': 'OPS Memo',
            'chapter': 'Chapter 1',
            'sub_chapter': 'Sub Chapter 1',
            'date_modified': parsed_date or submission_date,
            'document': full_text
        }

    def extract_date(self, text: str) -> str:
        """
        Extract the latest date found in the document text using regex.

        Args:
            text (str): The full document text.

        Returns:
            str: The latest date found (in YYYY-MM-DD format) or None if not found.
        """
        # Patterns for both textual and numeric dates
        patterns = [
            r'\b(?:January|February|March|April|May|June|July|August|September|October|November|December)\s+\d{1,2},\s+\d{4}',
            r'\b\d{1,2}/\d{1,2}/\d{2,4}'
        ]
        matches = []
        for pattern in patterns:
            matches.extend(re.findall(pattern, text, flags=re.IGNORECASE))

        parsed_dates = []
        for match in matches:
            try:
                parsed_dates.append(pd.to_datetime(match).date())
            except Exception:
                pass

        return str(max(parsed_dates)) if parsed_dates else None
