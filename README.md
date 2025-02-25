Overview
The AI-Powered Tax Assistant automates tax filing by extracting financial data from PDFs, performing tax calculations, and generating structured reports. It uses Google Vision OCR for text recognition and AI-based Named Entity Recognition (NER) to extract financial entities such as income, deductions, and tax paid.
1. Setup and Environment
Prerequisites
Ensure you have the following installed:

Python 3.8+
Flask (for the web application)
pip (Python package manager)
Google Vision API Key (for OCR processing)
How to Use
Login: Enter your username to access the dashboard.
Upload PDF: Upload a tax-related PDF document.
AI Processing: The AI extracts income, deductions, and tax paid from the document.
View Results: The calculated tax details will be displayed in result.html.
Download Report: (Optional) Users can save/download the tax report.
API Endpoints
Endpoint	Method	Description
/	GET	Login Page
/home	GET	Dashboard (File Upload)
/upload_pdf	POST	Processes uploaded PDF
/result	GET	Displays tax calculation results
/logout	GET	Logs out user
Configuration
Google Vision OCR API Key:
Add your Google Cloud API key in the app.py file.
Database (Optional):
You can configure SQLite/PostgreSQL for storing user data.
Troubleshooting
Issue: Flask App Not Starting?
Ensure all dependencies are installed and Flask is correctly set up.
Issue: No Data Extracted from PDF?
Check if Google Vision OCR API is set up correctly.
Issue: Wrong Tax Calculation?
Verify extracted financial data in result.html.
Contributors
Rishitha



(i tried my level best to complete as much as possible but unfortunately i could'nt complete to the fullest. This is the first Hackethon i've participated and i did learned a lot of things).
