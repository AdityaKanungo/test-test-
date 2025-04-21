import os
import shutil
from pdf2docx import Converter
from docx import Document
from docx2pdf import convert


class PDFStrikethroughRedactor:
    """
    A class to remove strikethrough text from multiple PDFs in a directory.
    Only processes PDFs that contain strikethrough text.
    """

    def __init__(self, input_dir: str, output_dir: str):
        self.input_dir = input_dir
        self.output_dir = output_dir
        os.makedirs(output_dir, exist_ok=True)

    def _convert_pdf_to_docx(self, pdf_path, docx_path):
        converter = Converter(pdf_path)
        converter.convert(docx_path)
        converter.close()

    def _docx_has_strikethrough(self, docx_path):
        doc = Document(docx_path)
        for paragraph in doc.paragraphs:
            for run in paragraph.runs:
                if run.font.strike:
                    return True
        return False

    def _remove_strikethrough_and_save(self, original_docx_path, cleaned_docx_path):
        doc = Document(original_docx_path)
        for paragraph in doc.paragraphs:
            for run in paragraph.runs:
                if run.font.strike:
                    run.text = ''
        doc.save(cleaned_docx_path)

    def _convert_docx_to_pdf(self, docx_path, pdf_path):
        convert(docx_path, pdf_path)

    def process_all_pdfs(self):
        for filename in os.listdir(self.input_dir):
            if filename.lower().endswith(".pdf"):
                input_pdf_path = os.path.join(self.input_dir, filename)
                output_pdf_path = os.path.join(self.output_dir, filename)

                print(f"\nProcessing: {filename}")
                temp_docx_path = "temp_converted.docx"
                cleaned_docx_path = "temp_cleaned.docx"

                try:
                    self._convert_pdf_to_docx(input_pdf_path, temp_docx_path)

                    if self._docx_has_strikethrough(temp_docx_path):
                        print("Strikethrough detected. Redacting...")
                        self._remove_strikethrough_and_save(temp_docx_path, cleaned_docx_path)
                        self._convert_docx_to_pdf(cleaned_docx_path, output_pdf_path)
                        print(f"Saved cleaned PDF to: {output_pdf_path}")
                    else:
                        print("No strikethrough found. Copying original PDF...")
                        shutil.copy(input_pdf_path, output_pdf_path)

                finally:
                    for temp_file in [temp_docx_path, cleaned_docx_path]:
                        if os.path.exists(temp_file):
                            os.remove(temp_file)


# Example usage
if __name__ == "__main__":
    redactor = PDFStrikethroughRedactor("input_pdfs", "output_pdfs")
    redactor.process_all_pdfs()
