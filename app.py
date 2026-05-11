import os
from flask import (
    Flask, render_template, request, redirect,
    url_for, session, flash
)
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime


app = Flask(__name__)
app.secret_key = os.environ.get("SECRET_KEY", "hackathon_trip_it4320_secret")

BASE_DIR = os.path.abspath(os.path.dirname(__file__))
DB_PATH  = os.path.join(BASE_DIR, "reservations.db")

app.config["SQLALCHEMY_DATABASE_URI"] = f"sqlite:///{DB_PATH}"
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

db = SQLAlchemy(app)



class Reservation(db.Model):
    __tablename__ = "reservations"

    id             = db.Column(db.Integer, primary_key=True, autoincrement=True)
    passengerName  = db.Column(db.Text, nullable=False)
    seatRow        = db.Column(db.Integer, nullable=False)
    seatColumn     = db.Column(db.Integer, nullable=False)
    eTicketNumber  = db.Column(db.Text, nullable=False)
    created        = db.Column(
        db.DateTime, nullable=False,
        default=datetime.utcnow
    )


class Admin(db.Model):
    __tablename__ = "admins"

    username = db.Column(db.Text, primary_key=True)
    password = db.Column(db.Text, nullable=False)

def get_cost_matrix():
    """Return a 12×4 pricing matrix. Columns: A=$100, B=$75, C=$50, D=$100."""
    return [[100, 75, 50, 100] for _ in range(12)]


def generate_ticket_number(first_name: str) -> str:
    """
    Build an e-ticket code from the passenger's first name.

    Pattern: name[0].upper() then interleave 'I','N','F','O' with
    name[1..4] (lowercase), then append 'TC4320'.

    Examples:
        Alice  → AIlNiFcOeTC4320
        Bob    → BIoNbFOTC4320
        John   → JIoNhFnOTC4320
    """
    separators = ["I", "N", "F", "O"]
    name = first_name.strip()
    code = name[0].upper()
    for idx, sep in enumerate(separators):
        code += sep
        letter_idx = idx + 1
        if letter_idx < len(name):
            code += name[letter_idx].lower()
    code += "TC4320"
    return code


COL_LABELS = ["A", "B", "C", "D"]


def build_seat_grid():
    """Return the full 12×4 grid with reservation data keyed by (row, col)."""
    reservations = Reservation.query.all()
    taken = {}
    for r in reservations:
        taken[(r.seatRow, r.seatColumn)] = r
    return taken



@app.route("/")
def index():
    return render_template("index.html")



@app.route("/reserve", methods=["GET", "POST"])
def reserve():
    cost_matrix = get_cost_matrix()
    taken = build_seat_grid()

    if request.method == "POST":
        first_name = request.form.get("first_name", "").strip()
        last_name  = request.form.get("last_name",  "").strip()
        row_raw    = request.form.get("seat_row",   "").strip()
        col_raw    = request.form.get("seat_col",   "").strip()

        errors = []

        
        if not first_name:
            errors.append("First name is required.")
        elif not first_name.isalpha():
            errors.append("First name must contain only letters.")

        if not last_name:
            errors.append("Last name is required.")
        elif not last_name.isalpha():
            errors.append("Last name must contain only letters.")

        
        try:
            seat_row = int(row_raw) - 1          # convert to 0-indexed
            if seat_row < 0 or seat_row > 11:
                errors.append("Seat row must be between 1 and 12.")
        except (ValueError, TypeError):
            seat_row = None
            errors.append("Seat row must be a number between 1 and 12.")

        
        col_upper = col_raw.upper()
        if col_upper not in COL_LABELS:
            seat_col = None
            errors.append("Seat column must be A, B, C, or D.")
        else:
            seat_col = COL_LABELS.index(col_upper)

        
        if not errors and seat_row is not None and seat_col is not None:
            if (seat_row, seat_col) in taken:
                errors.append(
                    f"Seat {seat_row + 1}{COL_LABELS[seat_col]} is already reserved. "
                    "Please choose another seat."
                )

        if errors:
            return render_template(
                "reserve.html",
                errors=errors,
                taken=taken,
                cost_matrix=cost_matrix,
                col_labels=COL_LABELS,
                form=request.form,
            )

        
        passenger_name = f"{first_name} {last_name}"
        ticket         = generate_ticket_number(first_name)
        cost           = cost_matrix[seat_row][seat_col]

        new_res = Reservation(
            passengerName=passenger_name,
            seatRow=seat_row,
            seatColumn=seat_col,
            eTicketNumber=ticket,
        )
        db.session.add(new_res)
        db.session.commit()

        return render_template(
            "confirm.html",
            passenger_name=passenger_name,
            seat_row=seat_row + 1,
            seat_col=COL_LABELS[seat_col],
            ticket=ticket,
            cost=cost,
        )

    return render_template(
        "reserve.html",
        errors=[],
        taken=taken,
        cost_matrix=cost_matrix,
        col_labels=COL_LABELS,
        form={},
    )



@app.route("/admin/login", methods=["GET", "POST"])
def admin_login():
    if request.method == "POST":
        username = request.form.get("username", "").strip()
        password = request.form.get("password", "").strip()

        admin = Admin.query.filter_by(
            username=username, password=password
        ).first()

        if admin:
            session["admin"] = username
            return redirect(url_for("admin_dashboard"))

        return render_template(
            "admin_login.html",
            error="Invalid username or password. Please try again."
        )

    return render_template("admin_login.html", error=None)



@app.route("/admin")
def admin_dashboard():
    if "admin" not in session:
        flash("Please log in to access the admin area.", "warning")
        return redirect(url_for("admin_login"))

    cost_matrix  = get_cost_matrix()
    reservations = Reservation.query.order_by(Reservation.created).all()
    taken        = {(r.seatRow, r.seatColumn): r for r in reservations}
    total_sales  = sum(
        cost_matrix[r.seatRow][r.seatColumn] for r in reservations
    )

    return render_template(
        "admin.html",
        reservations=reservations,
        taken=taken,
        cost_matrix=cost_matrix,
        col_labels=COL_LABELS,
        total_sales=total_sales,
        admin_user=session["admin"],
    )



@app.route("/admin/delete/<int:res_id>", methods=["POST"])
def delete_reservation(res_id):
    if "admin" not in session:
        return redirect(url_for("admin_login"))

    res = db.session.get(Reservation, res_id)
    if res:
        name = res.passengerName
        db.session.delete(res)
        db.session.commit()
        flash(f"Reservation for {name} (Seat {res.seatRow + 1}"
              f"{COL_LABELS[res.seatColumn]}) has been deleted.", "success")
    else:
        flash("Reservation not found.", "danger")

    return redirect(url_for("admin_dashboard"))


@app.route("/admin/logout")
def admin_logout():
    session.pop("admin", None)
    flash("You have been logged out.", "info")
    return redirect(url_for("index"))



if __name__ == "__main__":
    with app.app_context():
        db.create_all()
    app.run(debug=True, host="0.0.0.0", port=5000)
