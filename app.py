from flask import Flask, render_template, request, send_file
from datetime import datetime
import calendar
import io
import uuid
from weasyprint import HTML
import math
app = Flask(__name__)

# -------------------------------
# Helpers
# -------------------------------
def safe_float(value):
    try:
        return float(value)
    except (ValueError, TypeError):
        return 0

def format_date(value):
    try:
        return datetime.strptime(value, "%Y-%m-%d").strftime("%d/%m/%Y")
    except:
        return ""

def get_working_days_in_month(date_str):
    try:
        dt = datetime.strptime(date_str, "%Y-%m-%d")
        year, month = dt.year, dt.month
        _, num_days = calendar.monthrange(year, month)

        working_days = 0
        for day in range(1, num_days + 1):
            if calendar.weekday(year, month, day) != 6: # 6 is Sunday
                working_days += 1
        return working_days
    except:
        return 0

# -------------------------------
# Routes
# -------------------------------
@app.route("/")
def index():
    return render_template("form.html")

@app.route("/generate", methods=["POST"])
def generate():
    # 1. Capture Dates
    billing_from_raw = request.form.get("billing_from", "")
    billing_to_raw = request.form.get("billing_to", "")

    # 2. Get Working Days for the month selected
    working_days_in_month = get_working_days_in_month(billing_from_raw)

    # 3. Get Amount1 (The Base Amount for calculations)
    amount1_input = safe_float(request.form.get("amount1", "0"))

    # 4. Calculate Rates automatically
    # Both Rate and Rate1 derived from Amount1 / Working Days
    auto_calculated_rate = amount1_input / working_days_in_month if working_days_in_month > 0 else 0.0

    # 5. Build Data Dictionary
    data = {
        "date": format_date(request.form.get("date", "")),
        "name": request.form.get("name", ""),
        "company_name": request.form.get("company_name", ""),
        "charge_type" : request.form.get("charge_type", ""),
        "billing_from": format_date(billing_from_raw),
        "billing_to": format_date(billing_to_raw),
        "billing_period": request.form.get("billing_period", ""),
        "description1": request.form.get("description1", ""),

        # Days inputs from form
        "days": safe_float(request.form.get("days", "0")),
        "days1" : request.form.get("days1", "Monthly"),
        "days2": safe_float(request.form.get("days2", "0")),
        "extra_days": safe_float(request.form.get("extra_days", "0")),
        "toll_days": safe_float(request.form.get("toll_days", "0")),

        # The Automated Rates
        "rate": round(auto_calculated_rate, 2),
        "rate1": round(auto_calculated_rate, 2),

        # Static/Other Rates
        "rate2": safe_float(request.form.get("rate2", "0")),
        "extra_rate": safe_float(request.form.get("extra_rate", "0")),
        "toll_rate": safe_float(request.form.get("toll_rate", "0")),

        # Meta info
        "month_working_days": working_days_in_month
    }

    # 6. Final Line Item Calculations
    # Amount = Days * Auto-calculated Rate
    # Amount1 = The full fixed monthly amount provided

    line_amount = data["days"] * data["rate"]
    line_amount1 = amount1_input
    line_amount2 = data["days2"] * data["rate2"]
    extra_amount = data["extra_days"] * data["extra_rate"]
    toll_amount = data["toll_days"] * data["toll_rate"]

    total = line_amount + line_amount2 + extra_amount + toll_amount

    # Update data for HTML rendering
    data.update({
        "amount": round(line_amount,2),
        "amount1": round(line_amount1,2),
        "amount2": round(line_amount2,2),
        "extra_amount": round(extra_amount,2),
        "toll_amount": round(toll_amount,2),
        "total": math.floor(total)
    })

    # 7. PDF Generation
    html_out = render_template("invoice.html", **data)
    pdf_file = io.BytesIO()

    try:
        HTML(string=html_out).write_pdf(pdf_file)
    except Exception as e:
        return f"Dependency Error: {e}. Check WeasyPrint/GTK installation."

    pdf_file.seek(0)

    return send_file(
        pdf_file,
        as_attachment=True,
        download_name=f"Invoice_{uuid.uuid4().hex[:8]}.pdf",
        mimetype="application/pdf"
    )

if __name__ == "__main__":
    app.run(debug=True, threaded=False)
