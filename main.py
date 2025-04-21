from pdf2docx import Converter
from docx import Document
from docx2pdf import convert
import os

class PDFStrikethroughRedactor:
    """
    Removes strikethrough text from all PDFs in input_dir and writes results to output_dir.
    Only processes (and re-exports) PDFs where strikethrough text is found; otherwise copies as-is.
    """

    def __init__(self, input_dir: str, output_dir: str):
        self.input_dir = input_dir
        self.output_dir = output_dir
        os.makedirs(output_dir, exist_ok=True)
        self._temp_docx = "temp_converted.docx"
        self._cleaned_docx = "temp_cleaned.docx"

    def _convert_pdf_to_docx(self, pdf_path: str):
        converter = Converter(pdf_path)
        converter.convert(self._temp_docx)
        converter.close()

    def _detect_and_remove_strikes(self) -> bool:
        doc = Document(self._temp_docx)
        found = False
        for para in doc.paragraphs:
            for run in para.runs:
                if run.font.strike:
                    run.text = ""
                    found = True
        if found:
            doc.save(self._cleaned_docx)
        return found

    def _convert_docx_to_pdf(self, output_pdf: str):
        convert(self._cleaned_docx, output_pdf)

    def _copy_pdf(self, src: str, dst: str):
        with open(src, "rb") as f_src, open(dst, "wb") as f_dst:
            f_dst.write(f_src.read())

    def _cleanup(self):
        for path in (self._temp_docx, self._cleaned_docx):
            if os.path.exists(path):
                os.remove(path)

    def process_all(self):
        for entry in os.scandir(self.input_dir):
            if not entry.name.lower().endswith(".pdf"):
                continue

            src_pdf = entry.path
            dst_pdf = os.path.join(self.output_dir, entry.name)
            print(f"\nProcessing {entry.name}…")

            # 1. Convert to DOCX
            self._convert_pdf_to_docx(src_pdf)

            # 2. Detect & remove strikes in one pass
            if self._detect_and_remove_strikes():
                print(" → Strikethrough found. Exporting cleaned PDF.")
                self._convert_docx_to_pdf(dst_pdf)
            else:
                print(" → No strikethrough found. Copying original PDF.")
                self._copy_pdf(src_pdf, dst_pdf)

            # 3. Clean up temp files
            self._cleanup()


if __name__ == "__main__":
    redactor = PDFStrikethroughRedactor("input_pdfs", "output_pdfs")
    redactor.process_all()
