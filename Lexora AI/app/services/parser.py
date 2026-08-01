import fitz
from docx import Document as DocxDocument


def extract_pdf(file_path):
    text = ""
    pdf = fitz.open(file_path)
    try:
        for page in pdf:
            text += page.get_text()
            text += "\n"
    finally:
        pdf.close()
    return text.strip()


def extract_docx(file_path):
    doc = DocxDocument(file_path)
    text = "\n".join(
        paragraph.text
        for paragraph in doc.paragraphs
        if paragraph.text.strip()
    )
    return text.strip()


def extract_txt(file_path):
    with open(file_path, "r", encoding="utf-8", errors="ignore") as f:
        return f.read().strip()


def extract_text(file_path):
    lower_path = file_path.lower()
    if lower_path.endswith(".pdf"):
        return extract_pdf(file_path)
    if lower_path.endswith(".docx"):
        return extract_docx(file_path)
    if lower_path.endswith(".txt"):
        return extract_txt(file_path)

    raise ValueError("Unsupported file type")