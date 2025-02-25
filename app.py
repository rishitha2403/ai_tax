import os
import fitz  # PyMuPDF
from flask import Flask, request, redirect, url_for, session, render_template

app = Flask(__name__)
app.secret_key = 'your_secret_key'  # Needed for session management

# Tax deduction rules (Simplified)
TAX_RATE = 0.2
DEDUCTIONS = {"healthcare": 0.1, "education": 0.15, "donations": 0.2}

def extract_text_from_pdf(pdf_path):
    """Extract text from a PDF file."""
    text = ""
    doc = fitz.open(pdf_path)
    for page in doc:
        text += page.get_text("text") + "\n"
    return text

@app.route("/upload_pdf", methods=["POST"])
def upload_pdf():
    """Processes a PDF file, calculates tax, and redirects to the result page."""
    if 'file' not in request.files:
        return {"error": "No file provided"}, 400

    file = request.files['file']
    if not file.filename.endswith(".pdf"):
        return {"error": "Invalid file type"}, 400

    # Save the file temporarily
    file_path = "temp.pdf"
    file.save(file_path)

    # Extract text from the PDF
    extracted_text = extract_text_from_pdf(file_path)

    # Mocked tax values (in real case, extract them from text using NLP)
    income = 50000  # Assume extracted income
    expenses = {"healthcare": 2000, "education": 3000, "donations": 1500}

    # Calculate deductions
    total_deductions = sum(expenses[cat] * DEDUCTIONS[cat] for cat in expenses)
    taxable_income = max(income - total_deductions, 0)
    tax = taxable_income * TAX_RATE

    # Prepare the result dictionary
    result = {
        "extracted_text": extracted_text[:500],  # Show first 500 characters
        "income": income,
        "deductions": total_deductions,
        "taxable_income": taxable_income,
        "calculated_tax": tax
    }

    # Save the result in the session
    session['result'] = result

    # Redirect to the result page (which will render result.html)
    return redirect(url_for('result'))

@app.route("/result")
def result():
    """Displays the tax calculation results using result.html."""
    result = session.get('result')
    if not result:
        return "No result found", 404
    return render_template("result.html", result=result)

@app.route("/")
def home():
    return render_template("view.html")

if __name__ == "__main__":
    app.run(debug=True)
