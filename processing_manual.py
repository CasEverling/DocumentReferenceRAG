# process_manual.py
import os
import io
from typing import List
from PIL import Image

from manual_database import ManualDatabase
from pdf_utils import pdf_to_images
from gpt_vision import gpt_extract_text_hierarchy


DATA_DIR = "data"
MANUALS_DIR = os.path.join(DATA_DIR, "manuals")
PAGES_DIR = os.path.join(DATA_DIR, "pages")
CROPS_DIR = os.path.join(DATA_DIR, "crops")


os.makedirs(MANUALS_DIR, exist_ok=True)
os.makedirs(PAGES_DIR, exist_ok=True)
os.makedirs(CROPS_DIR, exist_ok=True)


def process_manual(pdf_path: str, make: str, model: str, year: int, police_or_civil: str) -> int:
    """
    - Create MANUAL entry
    - Render pages to PNG
    - GPT extracts text blocks
    - Store sections/images in SQLite
    - Save page PNGs and cropped image PNGs locally
    Returns manual_id.
    """

    db = ManualDatabase()
    manual_id = db.add_manual(make, model, year, police_or_civil)

    # Copy PDF to local manual folder with manual_id
    import shutil

    final_pdf_path = os.path.join(MANUALS_DIR, f"{manual_id}.pdf")
    shutil.copy2(pdf_path, final_pdf_path)

    pages: List[bytes] = pdf_to_images(final_pdf_path)

    for page_index, page_bytes in enumerate(pages, start=1):
        # Save page image
        page_path = os.path.join(PAGES_DIR, f"{manual_id}_{page_index}.png")
        with open(page_path, "wb") as f:
            f.write(page_bytes)

        # Load into PIL for cropping
        pil_img = Image.open(io.BytesIO(page_bytes)).convert("RGB")
        width, height = pil_img.size

        blocks = gpt_extract_text_hierarchy(page_bytes)

        for block in blocks:
            x = float(block.get("x", 0.0))
            y = float(block.get("y", 0.0))
            w = float(block.get("w", 0.0))
            h = float(block.get("h", 0.0))
            desc = block.get("description", "")
            hierarchy = block.get("hierarchy", [])

            # Insert image metadata, get image_id
            image_id = db.add_image(manual_id, page_index, x, y, w, h, desc)

            # Crop the region and save
            # Assume x, y, w, h are normalized (0..1)
            left = max(0, int(x * width))
            top = max(0, int(y * height))
            right = min(width, int((x + w) * width))
            bottom = min(height, int((y + h) * height))

            if right > left and bottom > top:
                crop = pil_img.crop((left, top, right, bottom))
                crop_path = os.path.join(CROPS_DIR, f"{image_id}.png")
                crop.save(crop_path, format="PNG")

            # Insert section if present
            if hierarchy:
                db.add_section(manual_id, None, page_index, page_index, " > ".join(hierarchy))

    return manual_id
