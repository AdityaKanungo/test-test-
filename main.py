import os
import tempfile
import pandas as pd
from docx import Document
from pdf2docx import Converter

class DocumentAuditor:
    """
    Class to audit documents for presence of strikethroughs and tables.
    """

    def __init__(self, input_dir: str):
        """
        Initialize auditor with input directory.
        """
        self.input_dir = input_dir

    def _convert_pdf_to_docx(self, pdf_path: str, docx_path: str) -> None:
        """
        Internal method to convert PDF to DOCX.
        """
        converter = Converter(pdf_path)
        converter.convert(docx_path)
        converter.close()

    def _has_strikethrough(self, doc: Document) -> bool:
        """
        Check if document has any strikethrough text.
        """
        for para in doc.paragraphs:
            for run in para.runs:
                if run.font.strike:
                    return True
        for table in doc.tables:
            for row in table.rows:
                for cell in row.cells:
                    for para in cell.paragraphs:
                        for run in para.runs:
                            if run.font.strike:
                                return True
        return False

    def _has_tables(self, doc: Document) -> bool:
        """
        Check if document has any tables.
        """
        return len(doc.tables) > 0

    def audit(self, output_excel_path: str) -> None:
        """
        Audit all documents in the input directory.
        Exports audit results to an Excel file.
        """
        audit_results = []

        for filename in os.listdir(self.input_dir):
            input_path = os.path.join(self.input_dir, filename)
            has_strike = False
            has_table = False

            if filename.lower().endswith('.docx'):
                doc = Document(input_path)
                has_strike = self._has_strikethrough(doc)
                has_table = self._has_tables(doc)

            elif filename.lower().endswith('.pdf'):
                with tempfile.NamedTemporaryFile(delete=False, suffix=".docx") as tmp_file:
                    temp_docx_path = tmp_file.name

                try:
                    self._convert_pdf_to_docx(input_path, temp_docx_path)
                    doc = Document(temp_docx_path)
                    has_strike = self._has_strikethrough(doc)
                    has_table = self._has_tables(doc)
                finally:
                    if os.path.exists(temp_docx_path):
                        os.remove(temp_docx_path)

            audit_results.append({
                "Filename": filename,
                "Has Strikethrough": "Yes" if has_strike else "No",
                "Has Tables": "Yes" if has_table else "No"
            })

        df_audit = pd.DataFrame(audit_results)
        df_audit.to_excel(output_excel_path, index=False)
        print(f"Audit report saved to: {output_excel_path}")
