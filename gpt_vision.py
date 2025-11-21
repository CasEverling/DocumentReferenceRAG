# gpt_vision.py
import json
import base64
import time
from openai import OpenAI

client = OpenAI(api_key="your-api-key-here")

def gpt_extract(page_png_bytes):
    img_b64 = base64.b64encode(page_png_bytes).decode("utf-8")

    prompt = """
    You are extracting structured information from a vehicle service manual.

    Return JSON with:
    - headings: array of heading objects { type, description, level, x, y, w, h }
    - images: array of image objects { type, description, x, y, w, h }

    - Identify headings by font size, boldness, caps, or placement.
    - level 1 = major section, level 2 = subsection, level 3 = sub-subsection.
    - Images are diagrams or photos.

    JSON only, no explanation.
    """

    # FIXED: The ONLY change required
    image_block = {
        "type": "image_url",
        "image_url": {
            "url": f"data:image/png;base64,{img_b64}"
        }
    }

    response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[
            {
                "role": "user",
                "content": [
                    {"type": "text", "text": prompt},
                    image_block
                ]
            }
        ],
        max_tokens=4000,
        temperature=0
    )

    # Return content of message
    raw = response.choices[0].message.content.strip()

    # Clean multiple concatenated JSON objects if GPT returns them
    if raw.startswith("{") and raw.endswith("}"):
        return json.loads(raw)

    # Case: GPT returned multiple objects separated by newlines
    pieces = []
    for chunk in raw.split("\n"):
        chunk = chunk.strip()
        if chunk.startswith("{") and chunk.endswith("}"):
            try:
                pieces.append(json.loads(chunk))
            except:
                pass

    if len(pieces) == 1:
        return pieces[0]

    # If multiple blocks, merge headings and images
    merged = {"headings": [], "images": []}
    for p in pieces:
        merged["headings"] += p.get("headings", [])
        merged["images"] += p.get("images", [])

    return merged
