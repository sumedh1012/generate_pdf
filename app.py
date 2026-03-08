from flask import Flask, render_template, request, send_file
from docxtpl import DocxTemplate
from docx2pdf import convert
import os
import uuid
from datetime import datetime
import io
from weasyprint import HTML


app = Flask(__name__)

# -------------------------------
# Helper: Safe float conversion
# -------------------------------
def safe_float(value):
    try:
        return float(value)
    except (ValueError, TypeError):
        return 0.0


# -------------------------------
# Helper: Format date to dd/mm/yyyy
# -------------------------------
def format_date(value):
    try:
        return datetime.strptime(value, "%Y-%m-%d").strftime("%d/%m/%Y")
    except:
        return ""


# -------------------------------
# Home Route
# -------------------------------
@app.route("/")
def index():
    return render_template("form.html")


# -------------------------------
# Generate Invoice Route
# -------------------------------
"""@app.route("/generate", methods=["POST"])
def generate():

    # Format dates
    formatted_date = format_date(request.form.get("date", ""))
    formatted_billing_from = format_date(request.form.get("billing_from", ""))
    formatted_billing_to = format_date(request.form.get("billing_to", ""))

    # Collect form data
    data = {
        "date": formatted_date,
        "name": request.form.get("name", ""),
        "company_name": request.form.get("company_name", ""),
        "charge_type": request.form.get("charge_type", ""),
        "billing_from": formatted_billing_from,
        "billing_to": formatted_billing_to,
        "billing_period": request.form.get("billing_period", ""),
        "description1": request.form.get("description1", ""),
        "days": request.form.get("days", "0"),
        "rate": request.form.get("rate", "0"),
        "days1": request.form.get("days1", "").strip() or "Monthly",
        "rate1": request.form.get("rate1", "0"),
        "days2": request.form.get("days2", "0"),
        "rate2": request.form.get("rate2", "0"),
        "extra_days": request.form.get("extra_days", "0"),
        "extra_rate": request.form.get("extra_rate", "0"),
        "toll_days": request.form.get("toll_days", "0"),
        "toll_rate": request.form.get("toll_rate", "0"),
    }

    # -------------------------------
    # Backend Calculation (SAFE)
    # -------------------------------
    days = safe_float(data["days"])
    rate = safe_float(data["rate"])

    rate1 = safe_float(data["rate1"])

    days2 = safe_float(data["days2"])
    rate2 = safe_float(data["rate2"])

    extra_days = safe_float(data["extra_days"])
    extra_rate = safe_float(data["extra_rate"])

    toll_days = safe_float(data["toll_days"])
    toll_rate = safe_float(data["toll_rate"])

    amount = days * rate
    amount1 = rate1
    amount2 = days2 * rate2
    extra_amount = extra_days * extra_rate
    toll_amount = toll_days * toll_rate

    total = amount + amount2 + extra_amount + toll_amount

    # Update calculated values
    data["amount"] = round(amount, 2)
    data["amount1"] = round(amount1, 2)
    data["amount2"] = round(amount2, 2)
    data["extra_amount"] = round(extra_amount, 2)
    data["toll_amount"] = round(toll_amount, 2)
    data["total"] = round(total, 2)

    # -------------------------------
    # Generate Document
    # -------------------------------
    template = DocxTemplate("template.docx")
    template.render(data)

    os.makedirs("generated", exist_ok=True)

    unique_id = str(uuid.uuid4())
    docx_path = f"generated/{unique_id}.docx"
    pdf_path = f"generated/Invoice_{unique_id}.pdf"

    template.save(docx_path)

    # Convert DOCX to PDF (Windows fix)
    pythoncom.CoInitialize()
    convert(docx_path, pdf_path)
    pythoncom.CoUninitialize()

    return send_file(pdf_path, as_attachment=True)"""


# -------------------------------
# Generate Invoice Route (WeasyPrint version)
# -------------------------------
@app.route("/generate", methods=["POST"])
def generate():
    # 1️⃣ Keep all your existing form processing and calculations
    formatted_date = format_date(request.form.get("date", ""))
    formatted_billing_from = format_date(request.form.get("billing_from", ""))
    formatted_billing_to = format_date(request.form.get("billing_to", ""))

    data = {
        "date": formatted_date,
        "name": request.form.get("name", ""),
        "company_name": request.form.get("company_name", ""),
        "charge_type": request.form.get("charge_type", ""),
        "billing_from": formatted_billing_from,
        "billing_to": formatted_billing_to,
        "billing_period": request.form.get("billing_period", ""),
        "description1": request.form.get("description1", ""),
        "days": request.form.get("days", "0"),
        "rate": request.form.get("rate", "0"),
        "days1": request.form.get("days1", "").strip() or "Monthly",
        "rate1": request.form.get("rate1", "0"),
        "days2": request.form.get("days2", "0"),
        "rate2": request.form.get("rate2", "0"),
        "extra_days": request.form.get("extra_days", "0"),
        "extra_rate": request.form.get("extra_rate", "0"),
        "toll_days": request.form.get("toll_days", "0"),
        "toll_rate": request.form.get("toll_rate", "0"),
    }

    # Calculations (same as your current code)
    days = safe_float(data["days"])
    rate = safe_float(data["rate"])
    rate1 = safe_float(data["rate1"])
    days2 = safe_float(data["days2"])
    rate2 = safe_float(data["rate2"])
    extra_days = safe_float(data["extra_days"])
    extra_rate = safe_float(data["extra_rate"])
    toll_days = safe_float(data["toll_days"])
    toll_rate = safe_float(data["toll_rate"])

    amount = days * rate
    amount1 = rate1
    amount2 = days2 * rate2
    extra_amount = extra_days * extra_rate
    toll_amount = toll_days * toll_rate
    total = amount + amount2 + extra_amount + toll_amount

    data["amount"] = round(amount, 2)
    data["amount1"] = round(amount1, 2)
    data["amount2"] = round(amount2, 2)
    data["extra_amount"] = round(extra_amount, 2)
    data["toll_amount"] = round(toll_amount, 2)
    data["total"] = round(total, 2)

    # 2️⃣ Render HTML (your existing HTML template)
    html_out = render_template("invoice.html", **data)

    # 3️⃣ Generate PDF in memory with WeasyPrint
    pdf_file = io.BytesIO()
    HTML(string=html_out).write_pdf(pdf_file)
    pdf_file.seek(0)

    # 4️⃣ Send PDF as attachment
    return send_file(
        pdf_file,
        as_attachment=True,
        download_name=f"Invoice_{uuid.uuid4()}.pdf",
        mimetype="application/pdf"
    )


# -------------------------------
# Run App
# -------------------------------
if __name__ == "__main__":
    app.run(debug=True, threaded=False)
