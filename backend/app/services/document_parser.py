import io
from pathlib import Path
from typing import Tuple, Dict, Any

def extract_text_from_txt(file_path: Path) -> str:
    """Reads plain text file with auto-detecting encodings."""
    try:
        with open(file_path, "r", encoding="utf-8") as f:
            return f.read()
    except UnicodeDecodeError:
        with open(file_path, "r", encoding="latin-1") as f:
            return f.read()

def extract_text_from_pdf(file_path: Path) -> str:
    """Extracts text from PDF using pypdf."""
    try:
        import pypdf
        reader = pypdf.PdfReader(str(file_path))
        text_parts = []
        for i, page in enumerate(reader.pages):
            page_text = page.extract_text() or ""
            if page_text.strip():
                text_parts.append(page_text.strip())
        return "\n\n".join(text_parts)
    except Exception as e:
        raise ValueError(f"Error procesando archivo PDF: {str(e)}")

def extract_text_from_docx(file_path: Path) -> str:
    """Extracts text from Word DOCX including paragraphs and tables."""
    try:
        import docx
        doc = docx.Document(str(file_path))
        text_parts = []
        
        # Read section headers if any
        try:
            for section in doc.sections:
                for h_para in section.header.paragraphs:
                    if h_para.text.strip():
                        text_parts.append(h_para.text.strip())
        except Exception:
            pass

        # Read paragraphs
        for para in doc.paragraphs:
            if para.text.strip():
                text_parts.append(para.text.strip())
                
        # Read tables (crucial for invoices and contracts)
        for table in doc.tables:
            table_lines = []
            for row in table.rows:
                row_cells = [cell.text.strip() for cell in row.cells if cell.text.strip()]
                if row_cells:
                    table_lines.append(" | ".join(row_cells))
            if table_lines:
                text_parts.append("\n".join(table_lines))
                
        return "\n\n".join(text_parts)
    except Exception as e:
        raise ValueError(f"Error procesando archivo Word DOCX: {str(e)}")

def parse_document(file_path: Path, extension: str) -> Dict[str, Any]:
    """Unified document parser for PDF, DOCX, and TXT files."""
    ext = extension.lower()
    if not ext.startswith("."):
        ext = f".{ext}"
        
    if ext == ".txt":
        raw_text = extract_text_from_txt(file_path)
    elif ext == ".pdf":
        raw_text = extract_text_from_pdf(file_path)
    elif ext == ".docx":
        raw_text = extract_text_from_docx(file_path)
    else:
        raise ValueError(f"Formato no soportado: {ext}. Formatos permitidos: .pdf, .docx, .txt")

    clean_text = "\n".join([line.strip() for line in raw_text.splitlines() if line.strip()])
    word_count = len(clean_text.split())
    char_count = len(clean_text)

    return {
        "raw_text": clean_text,
        "word_count": word_count,
        "char_count": char_count
    }
