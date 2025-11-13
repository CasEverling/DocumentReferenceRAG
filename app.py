# app.py
import os
import json
import base64

from flask import Flask, request, jsonify, send_file

from manual_database import ManualDatabase
from process_manual import process_manual, MANUALS_DIR, PAGES_DIR, CROPS_DIR


app = Flask(__name__)


@app.route("/process_manual", methods=["POST"])
def api_process_manual():
    """
    Body JSON:
    {
      "pdf_base64": "<base64PDF>",
      "make": "Ford",
      "model": "Crown Victoria",
      "year": 2010,
      "police_or_civil": "Police"
    }
    """
    try:
        data = request.get_json(force=True)
        pdf_b64 = data["pdf_base64"]
        make = data["make"]
        model = data["model"]
        year = int(data["year"])
        police_or_civil = data["police_or_civil"]

        pdf_bytes = base64.b64decode(pdf_b64)
        tmp_path = os.path.join("data", "upload_temp.pdf")
        with open(tmp_path, "wb") as f:
            f.write(pdf_bytes)

        manual_id = process_manual(
            pdf_path=tmp_path,
            make=make,
            model=model,
            year=year,
            police_or_civil=police_or_civil,
        )

        return jsonify({"manual_id": manual_id})

    except Exception as e:
        print(f"Error in /process_manual: {e}")
        return jsonify({"error": str(e)}), 500


@app.route("/get_page/<int:manual_id>/<int:page>", methods=["GET"])
def api_get_page(manual_id: int, page: int):
    """
    Returns the rendered page PNG.
    """
    page_path = os.path.join(PAGES_DIR, f"{manual_id}_{page}.png")
    if not os.path.exists(page_path):
        return jsonify({"error": "Page not found"}), 404

    return send_file(page_path, mimetype="image/png")


@app.route("/get_references", methods=["POST"])
def api_get_references():
    """
    Body JSON:
    {
      "manual_id": 123,
      "message": "How do I replace the front brake pads?"
    }

    Returns:
    {
      "sections": [
        {"manual_id": 123, "page_number": 5, "section_name": "..."},
        ...
      ],
      "images": [
        {"image_id": 42, "page_number": 5, "image_base64": "..."},
        ...
      ]
    }
    """
    try:
        data = request.get_json(force=True)
        manual_id = int(data["manual_id"])
        message = data["message"]

        db = ManualDatabase()
        manual = db.get_manual(manual_id)
        if not manual:
            return jsonify({"error": "Manual not found"}), 404

        sections = db.get_sections_by_manual(manual_id)
        images = db.get_images_by_manual(manual_id)

        # --- Simple heuristic: return all for now or filter later using GPT ---
        # You can later add a GPT call to choose the best subset based on `message`.

        sections_out = [
            {
                "manual_id": s[1],
                "page_number": s[3],
                "section_name": s[5],
            }
            for s in sections
        ]

        images_out = []
        for img in images:
            image_id = img[0]
            page_number = img[2]
            crop_path = os.path.join(CROPS_DIR, f"{image_id}.png")

            if os.path.exists(crop_path):
                with open(crop_path, "rb") as f:
                    b64_img = base64.b64encode(f.read()).decode("utf-8")
            else:
                b64_img = None

            images_out.append(
                {
                    "image_id": image_id,
                    "page_number": page_number,
                    "image_base64": b64_img,
                }
            )

        return jsonify(
            {
                "manual": {
                    "ManualId": manual[0],
                    "Make": manual[1],
                    "Model": manual[2],
                    "Year": manual[3],
                    "PoliceOrCivil": manual[4],
                },
                "message": message,
                "sections": sections_out,
                "images": images_out,
            }
        )

    except Exception as e:
        print(f"Error in /get_references: {e}")
        return jsonify({"error": str(e)}), 500


if __name__ == "__main__":
    # Dev mode
    app.run(host="0.0.0.0", port=8000, debug=True)
