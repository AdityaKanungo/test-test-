
from docx import Document
import tempfile
from docx2pdf import convert
import re
import os
import fitz  # PyMuPDF

class StrikethroughRedactor:
    """
    Utility class to redact strikethrough text from .docx or .pdf files
    and convert/save the cleaned document as a PDF file.
    """

    def __init__(self, file_path: str):
        """
        Initialize the redactor with a given file path.

        Parameters:
            file_path (str): Path to the input .docx or .pdf file.
        """
        self.file_path = file_path
        self.strikethrough_texts = []

    def redact_strikethrough_docx(self, output_pdf_path: str):
        """
        Remove strikethrough text from a docx file and save as PDF.
        """
        doc = Document(self.file_path)
        for para in doc.paragraphs:
            for run in para.runs:
                if run.font.strike:
                    self.strikethrough_texts.append(run.text)
                    run.text = ''

        fd, temp_docx_path = tempfile.mkstemp(suffix=".docx")
        os.close(fd)

        try:
            doc.save(temp_docx_path)
            convert(temp_docx_path, output_pdf_path)
        finally:
            if os.path.exists(temp_docx_path):
                os.remove(temp_docx_path)

    def redact_strikethrough_pdf(self, output_pdf_path: str):
        """
        Remove strikethrough annotations from a PDF file and save it.
        """
        doc = fitz.open(self.file_path)

        for page in doc:
            annot = page.first_annot
            while annot:
                annot_type = annot.type[0]
                if annot_type == fitz.PDF_ANNOT_STRIKE_OUT:
                    strike_text = annot.info.get("content", "")
                    self.strikethrough_texts.append(strike_text)
                    page.delete_annot(annot)
                annot = annot.next

        doc.save(output_pdf_path)

    def redact_and_save_pdf(self, output_pdf_path: str):
        """
        Detect file type (.docx or .pdf) and perform appropriate redaction.
        """
        if self.file_path.lower().endswith('.docx'):
            self.redact_strikethrough_docx(output_pdf_path)
        elif self.file_path.lower().endswith('.pdf'):
            self.redact_strikethrough_pdf(output_pdf_path)
        else:
            raise ValueError("Unsupported file type. Only .docx or .pdf are allowed.")


if __name__ == "__main__":
    input_file = 'OPS 23-12-05.docx'  # can be '.docx' or '.pdf'
    output_file = re.sub(r"\.docx$|\.pdf$", "_redacted.pdf", input_file)

    redactor = StrikethroughRedactor(input_file)
    redactor.redact_and_save_pdf(output_file)

    print(f"Strikethrough texts removed: {redactor.strikethrough_texts}")
