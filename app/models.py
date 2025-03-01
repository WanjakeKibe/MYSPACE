from . import db

class ParkingSpot(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    location = db.Column(db.String(200), nullable=False)


class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    fullname = db.Column(db.String(150), nullable=False)
    username = db.Column(db.String(80), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password = db.Column(db.String(200), nullable=False)


class Booking(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    location_id = db.Column(db.Integer, db.ForeignKey(
        'parking_spot.id'), nullable=False)
    check_in_date = db.Column(db.String(10), nullable=False)
    check_in_time = db.Column(db.String(5), nullable=False)
    check_out_date = db.Column(db.String(10), nullable=False)
    check_out_time = db.Column(db.String(5), nullable=False)
    promo_code = db.Column(db.String(20))
