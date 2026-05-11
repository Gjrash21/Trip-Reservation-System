from models import db, Reservation, Admin
from utils import get_cost_matrix, generate_eticket


def init_db(app):

    db.init_app(app)

    with app.app_context():
        db.create_all()


def add_reservation(passenger_name, seat_row, seat_column):
    try:
        #avoid double booking
        existing = Reservation.query.filter_by(
            seatRow=seat_row,
            seatColumn=seat_column
        ).first()

        if existing:
            return None

        ticket = generate_eticket()

        reservation = Reservation(
            passengerName=passenger_name,
            seatRow=seat_row,
            seatColumn=seat_column,
            eTicketNumber=ticket
        )

        db.session.add(reservation)

        db.session.commit()

        return ticket

    except Exception as e:
        db.session.rollback()
        print("Error adding reservation:", e)
        return None


def get_all_reservations():
    try:
        return Reservation.query.all()

    except Exception as e:
        print("Error getting reservations:", e)
        return []


def delete_reservation(res_id):
    try:
        reservation = Reservation.query.get(res_id)

        if reservation:
            db.session.delete(reservation)
            db.session.commit()
            return True

        return False

    except Exception as e:
        db.session.rollback()
        print("Error deleting reservation:", e)
        return False


def calculate_total_sales():
    try:
        reservations = Reservation.query.all()
        cost_matrix = get_cost_matrix()
        total = 0

        for r in reservations:
            total += cost_matrix[r.seatRow][r.seatColumn]

        return total

    except Exception as e:
        print("Error calculating total sales:", e)
        return 0


def get_taken_seats():
    try:
        reservations = Reservation.query.all()

        taken = set()

        for r in reservations:
            taken.add((r.seatRow, r.seatColumn))

        return taken

    except Exception as e:
        print("Error getting taken seats:", e)

        return set()


def validate_admin(username, password):
    try:
        admin = Admin.query.filter_by(
            username=username,
            password=password
        ).first()

        return admin

    except Exception as e:
        print("Admin validation error:", e)

        return None
    