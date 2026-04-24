from flask import Flask, render_template, request
import pdfplumber
from google import genai
import os

app = Flask(__name__)

# Gemini client (reads API key from environment variable)
client = genai.Client()

UPLOAD_FOLDER = "uploads"
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

@app.route("/")
def home():
    return render_template("index.html")

@app.route("/upload", methods=["POST"])
def upload():
    if "pdf" not in request.files:
        return "No file uploaded"

    file = request.files["pdf"]

    if file.filename == "":
        return "No file selected"

    # File type check
    if not file.filename.lower().endswith(".pdf"):
        return "Please upload a PDF file"

    pdf_path = os.path.join(UPLOAD_FOLDER, file.filename)
    file.save(pdf_path)

    text = ""

    try:
        with pdfplumber.open(pdf_path) as pdf:
            for page in pdf.pages:
                page_text = page.extract_text()
                if page_text:
                    text += page_text + "\n"
    except Exception as e:
        return f"Error reading PDF: {str(e)}"

    # Limit text size (important for API)
    text = text[:12000]

    try:
        response = client.models.generate_content(
            model="gemini-2.0-flash",   # stable model
            contents=f"Summarize this PDF in simple language:\n\n{text}"
        )
        summary = response.text
    except Exception as e:
        return f"AI Error: {str(e)}"

    return render_template("index.html", summary=summary)


# 🔥 IMPORTANT: Render Deployment Fix
if __name__ == "__main__":
    port = int(os.environ.get("PORT", 10000))
    app.run(host="0.0.0.0", port=port)