from flask import Flask, render_template, request
import pdfplumber
from google import genai
import os

app = Flask(__name__)

# The Gemini SDK automatically reads GEMINI_API_KEY from the environment
client = genai.Client()

UPLOAD_FOLDER = "uploads"
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

@app.route("/")
def home():
    return render_template("index.html")

@app.route("/upload", methods=["POST"])
def upload():
    file = request.files["pdf"]

    if not file:
        return "No file uploaded"

    pdf_path = os.path.join(UPLOAD_FOLDER, file.filename)
    file.save(pdf_path)

    text = ""
    with pdfplumber.open(pdf_path) as pdf:
        for page in pdf.pages:
            page_text = page.extract_text()
            if page_text:
                text += page_text + "\n"

    # Keep the first version simple; very long PDFs should be chunked later
    text = text[:12000]

    response = client.models.generate_content(
        model="gemini-3-flash-preview",
        contents=f"Summarize this PDF in simple language:\n\n{text}"
    )

    summary = response.text
    return render_template("index.html", summary=summary)

if __name__ == "__main__":
    app.run(debug=True)