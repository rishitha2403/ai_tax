import os
import fitz  # PyMuPDF
import pytesseract
from PIL import Image
import io
import spacy
import re
from flask import Flask, request, redirect, url_for, session, render_template, flash

app = Flask(__name__)
app.secret_key = 'your_secret_key'  # Needed for session management

# Tax deduction rules (Example values; adjust as needed)
TAX_RATE = 0.2
DEDUCTIONS = {
    "healthcare": 0.1,
    "education": 0.15,
    "donations": 0.2,
    "housing_loan": 0.12,
    "retirement_savings": 0.08
}

# Load spaCy model (optional: can be used in future for refinement)
#nlp = spacy.load("en_core_web_sm")

# (Optional) On Windows, set the Tesseract executable path:
# pytesseract.pytesseract.tesseract_cmd = r"C:\Program Files\Tesseract-OCR\tesseract.exe"

def extract_text_from_pdf(pdf_path):
    """
    Extracts text from a PDF file using:
      - PyMuPDF for digital PDFs.
      - Tesseract OCR for scanned PDFs.
    """
    extracted_text = ""
    doc = fitz.open(pdf_path)
    
    for page_num, page in enumerate(doc, start=1):
        # Try extracting digital text first.
        text = page.get_text("text")
        extracted_text += f"\n--- Page {page_num} ---\n{text}\n"
        
        # If no text found, attempt OCR on images.
        if not text.strip():
            for img_index, img in enumerate(page.get_images(full=True), start=1):
                xref = img[0]
                base_image = doc.extract_image(xref)
                image_bytes = base_image["image"]
                image = Image.open(io.BytesIO(image_bytes))
                ocr_text = pytesseract.image_to_string(image)
                extracted_text += f"\n--- OCR from Image {img_index} (Page {page_num}) ---\n{ocr_text}\n"
    
    return extracted_text.strip()


def extract_financial_data(text):
    """
    Extracts financial data from text using regex.
    Handles multiple income sources, deductions, and tax paid.
    """
    financial_info = {
        "income": 0,
        "deductions": {},
        "total_deductions": 0,
        "tax_paid": 0
    }

    # Extract Income Sources (Salary, Bonus, Other Income)
    income_regex = re.compile(r"(?:(?:gross\s*annual\s*salary|total\s*income|salary)[^\d]{0,10}|bonus|other\s*income)[^\d]{0,10}₹?\s?([\d,]+)", re.IGNORECASE)
    income_matches = income_regex.findall(text)
    
    if income_matches:
        financial_info["income"] = sum(int(x.replace(",", "")) for x in income_matches if x.replace(",", "").isdigit())

    # Extract Deductions (Standard Deduction, HRA, EPF, Health Insurance, etc.)
    deduction_patterns = {
        "standard_deduction": r"standard\s*deduction[^\d]{0,10}₹?\s?([\d,]+)",
        "hra": r"house\s*rent\s*allowance\s*\(HRA\)[^\d]{0,10}₹?\s?([\d,]+)",
        "epf": r"provident\s*fund\s*\(EPF\)[^\d]{0,10}₹?\s?([\d,]+)",
        "health_insurance": r"health\s*insurance\s*\(80D\)[^\d]{0,10}₹?\s?([\d,]+)",
        "education_loan": r"education\s*loan\s*interest\s*\(80E\)[^\d]{0,10}₹?\s?([\d,]+)",
        "donations": r"donations\s*\(80G\)[^\d]{0,10}₹?\s?([\d,]+)",
        "other_deductions": r"other\s*deductions[^\d]{0,10}₹?\s?([\d,]+)"
    }

    for key, pattern in deduction_patterns.items():
        match = re.search(pattern, text, re.IGNORECASE)
        if match:
            try:
                financial_info["deductions"][key] = int(match.group(1).replace(",", ""))
            except ValueError:
                financial_info["deductions"][key] = 0

    # Sum all deductions
    financial_info["total_deductions"] = sum(financial_info["deductions"].values())

    # Extract Tax Paid (TDS, Final Tax Paid)
    tax_paid_regex = re.compile(r"(?:tax\s*already\s*paid|TDS)[^\d]{0,10}₹?\s?([\d,]+)", re.IGNORECASE)
    tax_paid_match = tax_paid_regex.search(text)
    if tax_paid_match:
        try:
            financial_info["tax_paid"] = int(tax_paid_match.group(1).replace(",", ""))
        except ValueError:
            financial_info["tax_paid"] = 0

    return financial_info

def calculate_tax(financial_data):
    """
    Calculates tax based on extracted financial data.
    - Deducts allowable expenses from income.
    - Computes taxable income and tax due.
    """
    income = financial_data["income"]
    total_deductions = financial_data["total_deductions"]
    taxable_income = max(income - total_deductions, 0)

    # Apply standard tax rate
    tax_due = taxable_income * TAX_RATE

    return {
        "income": income,
        "total_deductions": total_deductions,
        "taxable_income": taxable_income,
        "calculated_tax": tax_due,
        "tax_paid": financial_data["tax_paid"],
        "final_tax_liability": tax_due - financial_data["tax_paid"]
    }


@app.route("/", methods=["GET", "POST"])
def login():
    """Handles user login."""
    if request.method == "POST":
        username = request.form["username"]
        # Accept any password if username is "rishitha"
        if username.lower() == "rishitha":
            session["user"] = username
            return redirect(url_for("home"))
        else:
            flash("Invalid username!", "error")
    return render_template("login.html")

@app.route("/home")
def home():
    """Main Dashboard for Uploading PDFs."""
    if "user" in session:
        return render_template("view.html", user=session["user"])
    return redirect(url_for("login"))

@app.route("/upload_pdf", methods=["POST"])
def upload_pdf():
    """
    Processes an uploaded PDF:
      - Extracts text (PyMuPDF & OCR)
      - Extracts financial details
      - Calculates tax
    """
    if "file" not in request.files:
        flash("No file provided!", "error")
        return redirect(url_for("home"))

    file = request.files["file"]
    if not file.filename.endswith(".pdf"):
        flash("Invalid file type! Only PDFs allowed.", "error")
        return redirect(url_for("home"))

    file_path = "temp.pdf"
    file.save(file_path)

    # Step 1: Extract text from the PDF
    extracted_text = extract_text_from_pdf(file_path)

    # Step 2: Extract financial data
    financial_data = extract_financial_data(extracted_text)

    # Step 3: Calculate tax
    tax_data = calculate_tax(financial_data)

    # Store results in session
    session["result"] = {
        "extracted_text": "",
        "financial_data": financial_data,
        **tax_data
    }

    return redirect(url_for("result"))

@app.route("/result")
def result():
    """Displays the tax calculation results."""
    if "result" not in session:
        flash("No tax calculation found!", "error")
        return redirect(url_for("home"))
    return render_template("result.html", result=session["result"])

@app.route("/logout")
def logout():
    """Logs out the user."""
    session.pop("user", None)
    return redirect(url_for("login"))

if __name__ == "__main__":
    app.run(debug=True)
