import os
import re
import tempfile
from docx import Document
from docx2pdf import convert

class StrikethroughRedactor:
    """
    A utility class to redact strikethrough text from a .docx file
    and convert the cleaned document to a PDF file.
    """

    def __init__(self, docx_path: str):
        """
        Initialize the redactor with a given .docx file path.
        Parameters:
            docx_path (str): Path to the input .docx file.
        """
        self.docx_path = docx_path
        self.doc = Document(docx_path)
        self.strikethrough_texts = []

    def redact_strikethrough(self):
        """
        Remove strikethrough text from the docx file.
        """
        for para in self.doc.paragraphs:
            for run in para.runs:
                if run.font.strike:
                    self.strikethrough_texts.append(run.text)
                    run.text = ''

    def convert_to_pdf(self, output_pdf_path: str):
        """
        Convert the modified document to PDF.
        Parameters:
            output_pdf_path (str): Path to save the converted PDF.
        """
        fd, temp_docx_path = tempfile.mkstemp(suffix=".docx")
        os.close(fd)

        try:
            self.doc.save(temp_docx_path)
            convert(temp_docx_path, output_pdf_path)
        finally:
            if os.path.exists(temp_docx_path):
                os.remove(temp_docx_path)

def process_directory(input_dir: str):
    """
    Process all .docx files in a given directory.
    Parameters:
        input_dir (str): Directory containing .docx files.
    """
    for filename in os.listdir(input_dir):
        if filename.lower().endswith(".docx"):
            docx_path = os.path.join(input_dir, filename)
            output_pdf_path = os.path.splitext(docx_path)[0] + ".pdf"

            print(f"Processing: {filename}")
            redactor = StrikethroughRedactor(docx_path)
            redactor.redact_strikethrough()
            redactor.convert_to_pdf(output_pdf_path)
            print(f"Saved PDF: {output_pdf_path}")

if __name__ == "__main__":
    directory_path = "path/to/your/docx/folder"  # Update this path
    process_directory(directory_path)
