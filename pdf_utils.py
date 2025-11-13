# pdf_utils.py
import fitz  # PyMuPDF
from typing import List


def pdf_to_images(pdf_path: str, max_pages: int | None = None, dpi: int = 200) -> List[bytes]:
    """
    Renders each PDF page to a PNG byte array using PyMuPDF.
    """
    images: List[bytes] = []
    with fitz.open(pdf_path) as doc:
        page_count = len(doc)
        limit = min(page_count, max_pages) if max_pages else page_count

        for i in range(limit):
            page = doc[i]
            pix = page.get_pixmap(dpi=dpi)
            images.append(pix.tobytes("png"))

    return images
