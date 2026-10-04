"""Employee form: collect details in a web form and save them to MySQL."""
import os
import re
from decimal import Decimal, InvalidOperation

import mysql.connector
from dotenv import load_dotenv
from flask import Flask, flash, redirect, render_template, request, url_for

load_dotenv()

import db  # noqa: E402  (import after env vars are loaded)

app = Flask(__name__)
app.secret_key = os.getenv("FLASK_SECRET_KEY", "dev-only-secret")

EMP_ID_PATTERN = re.compile(r"^[A-Za-z0-9-]{1,20}$")
TEXT_PATTERN = re.compile(r"^[A-Za-z .'-]{2,100}$")


def validate(form) -> tuple[dict, dict]:
    """Return (clean_data, errors)."""
    data = {k: (form.get(k) or "").strip() for k in
            ("employee_name", "employee_id", "salary", "designation", "city")}
    errors = {}

    if not TEXT_PATTERN.match(data["employee_name"]):
        errors["employee_name"] = "Enter a name of 2–100 letters."
    if not EMP_ID_PATTERN.match(data["employee_id"]):
        errors["employee_id"] = "Use up to 20 letters, digits or hyphens, e.g. EMP-1024."
    try:
        salary = Decimal(data["salary"].replace(",", ""))
        if salary < 0 or salary > Decimal("9999999999.99"):
            raise InvalidOperation
        data["salary"] = salary.quantize(Decimal("0.01"))
    except (InvalidOperation, ValueError):
        errors["salary"] = "Enter a positive amount, e.g. 55000 or 55000.50."
    if not (2 <= len(data["designation"]) <= 100):
        errors["designation"] = "Enter a designation of 2–100 characters."
    if not TEXT_PATTERN.match(data["city"]):
        errors["city"] = "Enter a city name of 2–100 letters."

    data["employee_id"] = data["employee_id"].upper()
    return data, errors


@app.route("/", methods=["GET", "POST"])
def employee_form():
    form_values, errors = {}, {}

    if request.method == "POST":
        form_values, errors = validate(request.form)
        if not errors:
            try:
                db.insert_employee(form_values)
                flash(f"Saved {form_values['employee_name']} ({form_values['employee_id']}).", "success")
                return redirect(url_for("employee_form"))  # Post/Redirect/Get
            except db.DuplicateEmployeeError:
                errors["employee_id"] = "This employee ID already exists."
            except mysql.connector.Error as exc:
                app.logger.exception("Database error")
                flash(f"Could not save to the database: {exc.msg}", "error")

    try:
        employees = db.list_employees()
    except mysql.connector.Error as exc:
        employees = []
        flash(f"Could not load employees: {exc.msg}", "error")

    return render_template("form.html", values=form_values, errors=errors, employees=employees)


if __name__ == "__main__":
    app.run(debug=os.getenv("FLASK_DEBUG") == "1", host=os.getenv("FLASK_HOST", "127.0.0.1"), port=5000)