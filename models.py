from flask_sqlalchemy import SQLAlchemy
from datetime import datetime

db = SQLAlchemy()

class Reservation(db.Model):
    __tablename__ = "reservations"

    id = db.Column(db.Integer, primary_key=True)

    passengerName = db.Column(db.String(100), nullable=False)

    seatRow = db.Column(db.Integer, nullable=False)

    seatColumn = db.Column(db.Integer, nullable=False)

    eTicketNumber = db.Column(db.String(20), unique=True, nullable=False)

    created = db.Column(db.DateTime, default=datetime.utcnow)

    def __repr__(self):
        return f"<Reservation {self.passengerName}>"


class Admin(db.Model):
    __tablename__ = "admins"

    id = db.Column(db.Integer, primary_key=True)

    username = db.Column(db.String(50), unique=True, nullable=False)

    password = db.Column(db.String(50), nullable=False)

    def __repr__(self):
        return f"<Admin {self.username}>"