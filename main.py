from pdf2docx import Converter
from docx import Document
from docx2pdf import convert
import os

def remove_strikethrough_from_pdf(input_pdf_path, output_pdf_path):
    # Step 1: Convert PDF to DOCX
    temp_docx_path = "temp_converted.docx"
    print("Converting PDF to DOCX...")
    converter = Converter(input_pdf_path)
    converter.convert(temp_docx_path)
    converter.close()

    # Step 2: Remove strikethrough text
    print("Removing strikethrough text...")
    doc = Document(temp_docx_path)
    for paragraph in doc.paragraphs:
        for run in paragraph.runs:
            if run.font.strike:
                run.text = ''  # Redact strikethrough text

    cleaned_docx_path = "temp_cleaned.docx"
    doc.save(cleaned_docx_path)

    # Step 3: Convert cleaned DOCX back to PDF
    print("Converting cleaned DOCX to PDF...")
    convert(cleaned_docx_path, output_pdf_path)

    # Step 4: Clean up temporary files
    os.remove(temp_docx_path)
    os.remove(cleaned_docx_path)
    print(f"Done! Cleaned PDF saved at: {output_pdf_path}")

# Example usage
remove_strikethrough_from_pdf("input.pdf", "output_cleaned.pdf")
