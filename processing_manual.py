# process_manual.py
import fitz
from gpt_vision import gpt_extract
from manual_database import ManualDatabase
import json

def process_manual(pdf_path, make, model, year, police_or_civil):
    print(f"Processing PDF: {pdf_path}")

    # Create database connection
    db = ManualDatabase()

    # Insert manual metadata and get manual_id
    manual_id = db.add_manual(make, model, year, police_or_civil)

    # Open PDF
    doc = fitz.open(pdf_path)

    for page_index in range(len(doc)):
        print(f"Processing page {page_index + 1}/{len(doc)}")

        page = doc[page_index]
        pix = page.get_pixmap(dpi=200)
        img_bytes = pix.tobytes("png")

        try:
            blocks = gpt_extract(img_bytes)
        except:
            print("Page failed. Skipping.")
            continue

        # Normalize GPT output format
        headings = []
        images = []

        if isinstance(blocks, dict):
            if "headings" in blocks:
                headings = blocks["headings"]
                images = blocks.get("images", [])
            elif "elements" in blocks:
                headings = [e for e in blocks["elements"] if e.get("type") == "heading"]
                images = [e for e in blocks["elements"] if e.get("type") == "image"]
        elif isinstance(blocks, list):
            headings = [e for e in blocks if e.get("type") == "heading"]
            images = [e for e in blocks if e.get("type") == "image"]

        # Store headings
        for h in headings:
            db.add_section(
                manual_id=manual_id,
                parent_id=None,
                start_page=page_index + 1,
                end_page=page_index + 1,
                description=h["description"],
                level=h.get("level", 1)
            )

        # Store images
        for img in images:
            db.add_image(
                manual_id=manual_id,
                page_index=page_index + 1,
                x=img["x"],
                y=img["y"],
                w=img["w"],
                h=img["h"],
                text=img["description"],
            )

    doc.close()
    db.close()
    print("DONE.")
    return manual_id
