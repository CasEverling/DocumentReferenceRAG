# gpt_vision.py
import base64
import json
import time
import os
from openai import OpenAI

client = OpenAI(api_key=os.environ.get("OPENAI_API_KEY"))


def gpt_extract_text_hierarchy(image_bytes: bytes, retries: int = 3):
    """
    Sends one page image to GPT-4o Vision.
    Returns a list of structured text blocks (dicts).
    Each block: {description, x, y, w, h, hierarchy}
    """

    image_b64 = base64.b64encode(image_bytes).decode("utf-8")
    prompt = (
        "Extract all text blocks from this manual page and return as a JSON array. "
        "Each element must include: description, x, y, w, h, hierarchy. "
        "Coordinates must be normalized between 0 and 1 relative to width and height."
    )

    for attempt in range(1, retries + 1):
        try:
            resp = client.chat.completions.create(
                model="gpt-4o-mini",
                messages=[
                    {"role": "system", "content": "You are an OCR-to-structure extractor."},
                    {
                        "role": "user",
                        "content": [
                            {"type": "text", "text": prompt},
                            {"type": "image_url", "image_url": f"data:image/png;base64,{image_b64}"},
                        ],
                    },
                ],
                temperature=0,
                max_tokens=2000,
            )

            raw = resp.choices[0].message.content.strip()
            start, end = raw.find("["), raw.rfind("]")
            return json.loads(raw[start : end + 1])
        except Exception as e:
            print(f"⚠️ GPT extract attempt {attempt} failed: {e}")
            time.sleep(2**attempt)

    raise Exception("GPT extraction failed after retries")
