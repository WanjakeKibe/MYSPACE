from flask import Blueprint, request, jsonify, render_template, url_for
from .models import db, ParkingSpot, Booking
import datetime

main = Blueprint('main', __name__)


@main.route('/')
def home():
    return render_template('index.html')


@main.route('/about')
def about():
    return render_template('about.html')


# @main.route('/api/parking-spots', methods=['GET'])
# def get_parking_spots():
#     spots = ParkingSpot.query.all()
#     spots_list = [{'id': spot.id, 'name': spot.name,
#                    'location': spot.location} for spot in spots]
#     return jsonify(spots_list)


@main.route('/api/book', methods=['POST'])
def book():
    data = request.get_json()

    # Minimal required fields check
    required_fields = ['location_id', 'check_in_date',
                       'check_in_time', 'check_out_date', 'check_out_time']
    missing = [field for field in required_fields if not data.get(field)]
    if missing:
        return jsonify({"error": f"Missing required fields: {', '.join(missing)}"}), 400

    # Create and save a new booking
    new_booking = Booking(
        location_id=data['location_id'],
        check_in_date=data['check_in_date'],
        check_in_time=data['check_in_time'],
        check_out_date=data['check_out_date'],
        check_out_time=data['check_out_time'],
        promo_code=data.get('promo_code')
    )
    db.session.add(new_booking)
    db.session.commit()

    return jsonify({
        "message": "Booking successful",
        "booking_id": new_booking.id
    }), 200
