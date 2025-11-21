# app.py
import base64
import os
from flask import Flask, request, jsonify, send_file
from manual_database import ManualDatabase
from process_manual import process_manual, pdf_to_pages
from gpt_vision import client
import sqlite3
import io
import fitz

app = Flask(__name__)

# Storage directory for uploaded manuals
MANUAL_PDF_DIR = "manual_storage"
os.makedirs(MANUAL_PDF_DIR, exist_ok=True)


# --------------------------
#  CREATE TABLES
# --------------------------
@app.route("/create_tables", methods=["POST"])
def create_tables():
    db = ManualDatabase()
    return jsonify({"status": "tables created"})


# --------------------------
#  UPLOAD + PROCESS MANUAL
# --------------------------
@app.route("/process_manual", methods=["POST"])
def route_process_manual():
    """
    Body (JSON):
    {
        "pdf_base64": "<b64>",
        "make": "Ford",
        "model": "Crown Vic",
        "year": 2010,
        "police_or_civil": "Police"
    }
    """

    try:
        data = request.get_json()
        pdf_b64 = data["pdf_base64"]
        make = data["make"]
        model = data["model"]
        year = int(data["year"])
        police_or_civil = data["police_or_civil"]

        # Decode PDF
        pdf_bytes = base64.b64decode(pdf_b64)
        pdf_path = os.path.join(MANUAL_PDF_DIR, "upload_temp.pdf")
        with open(pdf_path, "wb") as f:
            f.write(pdf_bytes)

        # Process manual
        manual_id = process_manual(
            pdf_path=pdf_path,
            make=make,
            model=model,
            year=year,
            police_or_civil=police_or_civil
        )

        # Save a permanent copy of the PDF
        final_pdf_path = os.path.join(MANUAL_PDF_DIR, f"{manual_id}.pdf")
        os.rename(pdf_path, final_pdf_path)

        return jsonify({"manual_id": manual_id})

    except Exception as e:
        print("Error in /process_manual:", e)
        return jsonify({"error": str(e)}), 500


# --------------------------
#  GET REFERENCES ENDPOINT
# --------------------------
@app.route("/get_references", methods=["POST"])
def get_references():
    """
    Input:
    {
        "manual_id": 6,
        "query": "How do I remove the rear seat?"
    }

    Output:
    {
        "sections": [...],
        "images": [...]
    }
    """

    try:
        data = request.get_json()
        manual_id = int(data["manual_id"])
        query = data["query"]

        db = ManualDatabase()

        # Get all headings
        conn = db.conn
        cur = conn.cursor()
        cur.execute("""
            SELECT Level, Page, Description FROM SECTIONS
            WHERE ManualId = ?
        """, (manual_id,))
        sections = cur.fetchall()

        # Create a prompt for GPT to choose best references
        section_text = "\n".join(
            [f"[p{p}] (L{lvl}) {desc}" for (lvl, p, desc) in sections]
        )

        prompt = f"""
You are a retrieval system for a vehicle service manual.

User query:
"{query}"

Here are the available manual sections:
{section_text}

Return a JSON object with two arrays:
- sections: list of objects {{page, description}}
- images: list of objects {{page, description}}

Only include the most relevant results.
Return ONLY JSON.
"""

        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[{"role": "user", "content": prompt}],
            temperature=0
        )

        raw = response.choices[0].message.content.strip()

        # Validate JSON safely
        import json
        return jsonify(json.loads(raw))

    except Exception as e:
        print("Error in /get_references:", e)
        return jsonify({"error": str(e)}), 500


# --------------------------
#  GET FULL PAGE IMAGE
# --------------------------
@app.route("/get_page", methods=["POST"])
def get_page():
    """
    Input:
    {
        "manual_id": 6,
        "page": 3
    }

    Returns raw PNG image of that page.
    """
    try:
        data = request.get_json()
        manual_id = int(data["manual_id"])
        page_index = int(data["page"]) - 1  # zero-based

        pdf_path = os.path.join(MANUAL_PDF_DIR, f"{manual_id}.pdf")
        if not os.path.exists(pdf_path):
            return jsonify({"error": "PDF not found"}), 404

        doc = fitz.open(pdf_path)
        if page_index >= len(doc):
            return jsonify({"error": "Page out of range"}), 400

        pix = doc[page_index].get_pixmap(dpi=150)
        img_bytes = pix.tobytes("png")

        return send_file(
            io.BytesIO(img_bytes),
            mimetype="image/png",
            as_attachment=False,
            download_name=f"manual_{manual_id}_page_{page_index+1}.png"
        )

    except Exception as e:
        print("Error in /get_page:", e)
        return jsonify({"error": str(e)}), 500


@app.route("/", methods=["GET"])
def index():
    return jsonify({"message": "Manual Processing API is running"})


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8000, debug=True)
