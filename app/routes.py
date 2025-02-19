from flask import Blueprint, request, jsonify, render_template, url_for
from .models import db, ParkingSpot, Booking
import datetime

main = Blueprint('main', __name__)


@main.route('/')
def home():
    return render_template('index.html')


# @main.route('/api/parking-spots', methods=['GET'])
# def get_parking_spots():
#     spots = ParkingSpot.query.all()
#     spots_list = [{'id': spot.id, 'name': spot.name,
#                    'location': spot.location} for spot in spots]
#     return jsonify(spots_list)


@main.route('/api/book', methods=['POST'])
def book_parking():
    data = request.get_json()

    # Validate required fields
    required_fields = ['location_id', 'check_in_date',
                       'check_in_time', 'check_out_date', 'check_out_time']
    missing_fields = [
        field for field in required_fields if field not in data or not data[field]]
    if missing_fields:
        return jsonify({
            "error": f"Missing required fields: {', '.join(missing_fields)}"
        }), 400

    # Validate that check-in is before check-out
    try:
        check_in_dt = datetime.datetime.strptime(
            f"{data['check_in_date']} {data['check_in_time']}", "%Y-%m-%d %H:%M")
        check_out_dt = datetime.datetime.strptime(
            f"{data['check_out_date']} {data['check_out_time']}", "%Y-%m-%d %H:%M")
        if check_in_dt >= check_out_dt:
            return jsonify({"error": "Check-out must be after check-in."}), 400
    except Exception as e:
        return jsonify({"error": "Invalid date/time format."}), 400

    # Create new booking and save to the database
    try:
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
    except Exception as e:
        db.session.rollback()
        return jsonify({"error": "An error occurred while saving the booking."}), 500

    # Return a successful response with the booking ID
    return jsonify({
        'message': 'Booking successful!',
        'booking_id': new_booking.id
    })
