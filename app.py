from flask import Flask, render_template, request, send_file
from datetime import datetime, timedelta
import calendar
import io
import uuid
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
# Logic: Count days in month excluding Sundays
# -------------------------------
def get_working_days_in_month(date_str):
    try:
        # Assumes date_str is "YYYY-MM-DD" from HTML date input
        dt = datetime.strptime(date_str, "%Y-%m-%d")
        year, month = dt.year, dt.month
        
        # Get total days in that specific month
        _, num_days = calendar.monthrange(year, month)
        
        working_days = 0
        for day in range(1, num_days + 1):
            # calendar.weekday: 0=Mon, 6=Sun
            if calendar.weekday(year, month, day) != 6:
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
    # 1. Capture Raw Data
    billing_from_raw = request.form.get("billing_from", "")
    billing_to_raw = request.form.get("billing_to", "")
    
    # 2. Extract Month Data & Calculate Working Days
    # We use the month from 'billing_from' as the reference
    working_days_count = get_working_days_in_month(billing_from_raw)
    
    # 3. Get Amount1 (The total to be divided)
    # Ensure your form.html has an input named "amount1"
    total_amount1 = safe_float(request.form.get("amount1", "0"))
    
    # 4. Calculate Rate 1 (Amount1 / Working Days in Month)
    calculated_rate1 = total_amount1 / working_days_count if working_days_count > 0 else 0.0

    # 5. Build Data Dictionary for Template
    data = {
        "date": format_date(request.form.get("date", "")),
        "name": request.form.get("name", ""),
        "company_name": request.form.get("company_name", ""),
        "charge_type": request.form.get("charge_type", ""),
        "billing_from": format_date(billing_from_raw),
        "billing_to": format_date(billing_to_raw),
        "billing_period": request.form.get("billing_period", ""),
        "description1": request.form.get("description1", ""),
        
        # Days & Rates
        "days": safe_float(request.form.get("days", "0")),
        "rate": safe_float(request.form.get("rate", "0")),
        "days1": request.form.get("days1", "").strip() or "Monthly",
        "rate1": round(calculated_rate1, 2), # This is our auto-calculated daily rate
        "days2": safe_float(request.form.get("days2", "0")),
        "rate2": safe_float(request.form.get("rate2", "0")),
        "extra_days": safe_float(request.form.get("extra_days", "0")),
        "extra_rate": safe_float(request.form.get("extra_rate", "0")),
        "toll_days": safe_float(request.form.get("toll_days", "0")),
        "toll_rate": safe_float(request.form.get("toll_rate", "0")),
        
        # Helper for display
        "month_working_days": working_days_count
    }

    # 6. Final Calculations for the Invoice
    amount = data["days"] * data["rate"]
    amount1 = total_amount1  # This is the full month amount provided by user
    amount2 = data["days2"] * data["rate2"]
    extra_amount = data["extra_days"] * data["extra_rate"]
    toll_amount = data["toll_days"] * data["toll_rate"]
    
    total = amount + amount1 + amount2 + extra_amount + toll_amount

    # Update data dict with calculated amounts
    data.update({
        "amount": round(amount, 2),
        "amount1": round(amount1, 2),
        "amount2": round(amount2, 2),
        "extra_amount": round(extra_amount, 2),
        "toll_amount": round(toll_amount, 2),
        "total": round(total, 2)
    })

    # 7. Render HTML & Generate PDF
    html_out = render_template("invoice.html", **data)
    
    pdf_file = io.BytesIO()
    try:
        HTML(string=html_out).write_pdf(pdf_file)
    except Exception as e:
        return f"WeasyPrint Error: {e}. Please ensure GTK/Pango libraries are installed."
    
    pdf_file.seek(0)

    return send_file(
        pdf_file,
        as_attachment=True,
        download_name=f"Invoice_{uuid.uuid4().hex[:8]}.pdf",
        mimetype="application/pdf"
    )

if __name__ == "__main__":
    # threaded=False is often required when using WeasyPrint/GTK on certain systems
    app.run(debug=True, threaded=False)
