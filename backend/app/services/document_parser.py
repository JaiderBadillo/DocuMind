import io
import re
import html
from pathlib import Path
from typing import Tuple, Dict, Any, List, Optional
from ..core.config import STORAGE_DIR

IMAGES_STORAGE_DIR = STORAGE_DIR / "images"
IMAGES_STORAGE_DIR.mkdir(parents=True, exist_ok=True)

def get_doc_images_dir(doc_id: int) -> Path:
    d = IMAGES_STORAGE_DIR / f"doc_{doc_id}"
    d.mkdir(parents=True, exist_ok=True)
    return d

def text_lines_to_html(raw_text: str) -> str:
    """Converts plain text or markdown tables and headings into structured HTML."""
    lines = raw_text.splitlines()
    html_parts = []
    table_buffer = []
    
    def flush_table(buf: List[str]) -> str:
        if not buf:
            return ""
        out = ['<table class="doc-table"><thead><tr>']
        # header
        headers = [c.strip() for c in buf[0].split('|') if c.strip()]
        for h in headers:
            out.append(f'<th>{html.escape(h)}</th>')
        out.append('</tr></thead><tbody>')
        for row in buf[1:]:
            # Skip divider line like |---|---|
            if re.match(r'^\s*\|?[-:\s|]+\|?\s*$', row):
                continue
            cells = [c.strip() for c in row.split('|') if c.strip()]
            if cells:
                out.append('<tr>' + ''.join(f'<td>{html.escape(c)}</td>' for c in cells) + '</tr>')
        out.append('</tbody></table>')
        return "".join(out)

    for line in lines:
        s = line.strip()
        if '|' in s and len(s.split('|')) >= 3:
            table_buffer.append(s)
        else:
            if table_buffer:
                html_parts.append(flush_table(table_buffer))
                table_buffer = []
            if s.startswith('# '):
                html_parts.append(f'<h1>{html.escape(s[2:].strip())}</h1>')
            elif s.startswith('## '):
                html_parts.append(f'<h2>{html.escape(s[3:].strip())}</h2>')
            elif s.startswith('### '):
                html_parts.append(f'<h3>{html.escape(s[4:].strip())}</h3>')
            elif s.startswith('• ') or s.startswith('- ') or s.startswith('* '):
                html_parts.append(f'<ul><li>{html.escape(s[2:].strip())}</li></ul>')
            elif s:
                html_parts.append(f'<p>{html.escape(s)}</p>')
    if table_buffer:
        html_parts.append(flush_table(table_buffer))
    return "\n".join(html_parts)


def extract_docx_content(file_path: Path, doc_id: Optional[int] = None) -> Tuple[str, str, int]:
    """Extracts raw text, rich HTML with tables & images from a Word DOCX document."""
    try:
        import docx
        from docx.text.paragraph import Paragraph
        from docx.table import Table
        
        doc = docx.Document(str(file_path))
        html_elements = []
        raw_text_parts = []
        images_count = 0
        doc_img_dir = get_doc_images_dir(doc_id) if doc_id else None

        # Extract embedded images from relationships
        image_rel_map = {}
        try:
            for rel_id, rel in doc.part.related_parts.items():
                if hasattr(rel, "content_type") and "image" in rel.content_type:
                    ext = rel.partname.split(".")[-1] if "." in rel.partname else "png"
                    img_name = f"docx_img_{rel_id}.{ext}"
                    if doc_img_dir:
                        dest = doc_img_dir / img_name
                        with open(dest, "wb") as f_img:
                            f_img.write(rel.blob)
                        image_rel_map[rel_id] = f"/api/documents/{doc_id}/images/{img_name}"
                    else:
                        image_rel_map[rel_id] = img_name
                    images_count += 1
        except Exception as e:
            print(f"[DOCX Parser] Advertencia extrayendo imágenes de relaciones: {e}")

        # Iterate through body elements in sequential order
        for child in doc.element.body:
            tag = child.tag
            if tag.endswith('p'):
                p = Paragraph(child, doc)
                text = p.text.strip()
                style_name = p.style.name.lower() if p.style else ""
                
                # Check for images referenced inside this paragraph's XML
                p_xml = child.xml
                p_images = []
                for rel_id, img_url in image_rel_map.items():
                    if rel_id in p_xml:
                        p_images.append(img_url)

                for img_url in p_images:
                    html_elements.append(
                        f'<div class="doc-img-wrapper"><img src="{img_url}" class="doc-img" alt="Imagen del documento" /></div>'
                    )

                if text:
                    raw_text_parts.append(text)
                    if "heading 1" in style_name or "título 1" in style_name:
                        html_elements.append(f'<h1>{html.escape(text)}</h1>')
                    elif "heading 2" in style_name or "título 2" in style_name:
                        html_elements.append(f'<h2>{html.escape(text)}</h2>')
                    elif "heading 3" in style_name or "título 3" in style_name:
                        html_elements.append(f'<h3>{html.escape(text)}</h3>')
                    elif style_name.startswith("list") or text.startswith("• ") or text.startswith("- "):
                        clean_item = text.lstrip("•-* ").strip()
                        html_elements.append(f'<ul><li>{html.escape(clean_item)}</li></ul>')
                    else:
                        html_elements.append(f'<p>{html.escape(text)}</p>')

            elif tag.endswith('tbl'):
                t = Table(child, doc)
                table_html = ['<table class="doc-table">']
                is_header = True
                table_text_rows = []
                
                for row in t.rows:
                    cells = [cell.text.strip() for cell in row.cells]
                    if not any(cells):
                        continue
                    tag_cell = 'th' if is_header else 'td'
                    row_html = '<tr>' + ''.join(f'<{tag_cell}>{html.escape(c)}</{tag_cell}>' for c in cells) + '</tr>'
                    table_text_rows.append(" | ".join(cells))
                    
                    if is_header:
                        table_html.append('<thead>' + row_html + '</thead><tbody>')
                        is_header = False
                    else:
                        table_html.append(row_html)
                        
                if not is_header:
                    table_html.append('</tbody>')
                table_html.append('</table>')
                
                if table_text_rows:
                    html_elements.append("".join(table_html))
                    raw_text_parts.append("\n".join(table_text_rows))

        # Fallback if body iteration produced no elements
        if not html_elements and doc.paragraphs:
            for p in doc.paragraphs:
                if p.text.strip():
                    raw_text_parts.append(p.text.strip())
                    html_elements.append(f'<p>{html.escape(p.text.strip())}</p>')

        clean_raw_text = "\n\n".join(raw_text_parts)
        rich_html = "\n".join(html_elements) if html_elements else text_lines_to_html(clean_raw_text)
        return clean_raw_text, rich_html, images_count
    except Exception as e:
        print(f"[DOCX Parser] Error procesando con python-docx: {e}")
        # Plain text fallback
        return extract_txt_content(file_path, doc_id)


def extract_pdf_content(file_path: Path, doc_id: Optional[int] = None) -> Tuple[str, str, int]:
    """Extracts text, detected tables, and embedded images from a PDF using pypdf."""
    try:
        import pypdf
        reader = pypdf.PdfReader(str(file_path))
        text_parts = []
        html_elements = []
        images_count = 0
        doc_img_dir = get_doc_images_dir(doc_id) if doc_id else None

        for page_idx, page in enumerate(reader.pages):
            page_num = page_idx + 1
            
            # Extract images from PDF page
            try:
                for img_idx, img in enumerate(page.images):
                    img_name = f"pdf_p{page_num}_img{img_idx+1}_{img.name}"
                    if doc_img_dir:
                        dest = doc_img_dir / img_name
                        with open(dest, "wb") as f_img:
                            f_img.write(img.data)
                        img_url = f"/api/documents/{doc_id}/images/{img_name}"
                        html_elements.append(
                            f'<div class="doc-img-wrapper"><img src="{img_url}" class="doc-img" alt="Imagen página {page_num}" /></div>'
                        )
                    images_count += 1
            except Exception as e:
                print(f"[PDF Parser] Advertencia extrayendo imagen página {page_num}: {e}")

            # Extract page text
            page_text = page.extract_text() or ""
            if page_text.strip():
                text_parts.append(page_text.strip())
                page_html = text_lines_to_html(page_text)
                html_elements.append(page_html)

        clean_raw_text = "\n\n".join(text_parts)
        rich_html = "\n".join(html_elements)
        return clean_raw_text, rich_html, images_count
    except Exception as e:
        raise ValueError(f"Error procesando archivo PDF: {str(e)}")


def extract_txt_content(file_path: Path, doc_id: Optional[int] = None) -> Tuple[str, str, int]:
    """Extracts text and structures markdown tables/headings into HTML."""
    raw_text = ""
    try:
        with open(file_path, "r", encoding="utf-8") as f:
            raw_text = f.read()
    except UnicodeDecodeError:
        with open(file_path, "r", encoding="latin-1") as f:
            raw_text = f.read()

    rich_html = text_lines_to_html(raw_text)
    return raw_text, rich_html, 0


def parse_document(file_path: Path, extension: str, doc_id: Optional[int] = None) -> Dict[str, Any]:
    """Unified document parser for PDF, DOCX, and TXT files, with rich HTML and image support."""
    ext = extension.lower()
    if not ext.startswith("."):
        ext = f".{ext}"
        
    if ext == ".txt":
        raw_text, content_html, img_count = extract_txt_content(file_path, doc_id)
    elif ext == ".pdf":
        raw_text, content_html, img_count = extract_pdf_content(file_path, doc_id)
    elif ext == ".docx":
        raw_text, content_html, img_count = extract_docx_content(file_path, doc_id)
    else:
        raise ValueError(f"Formato no soportado: {ext}. Formatos permitidos: .pdf, .docx, .txt")

    clean_text = "\n".join([line.strip() for line in raw_text.splitlines() if line.strip()])
    word_count = len(clean_text.split())
    char_count = len(clean_text)

    return {
        "raw_text": clean_text,
        "content_html": content_html,
        "word_count": word_count,
        "char_count": char_count,
        "images_extracted": img_count
    }
