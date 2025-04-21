from PDFNetPython3 import PDFDoc, Annot

# Load the PDF
doc = PDFDoc("example.pdf")
doc.InitSecurityHandler()

# Loop through annotations
for page in doc.GetPageIterator():
    for annot in page.GetAnnots():
        if annot.GetType() == Annot.e_StrikeOut:
            annot.Erase()
doc.Save("cleaned.pdf", 0)
