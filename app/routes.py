from flask import Blueprint, request, jsonify, session, flash, render_template, url_for, redirect, get_flashed_messages
from .forms import LoginForm, SignupForm
from .models import db, ParkingSpot, Booking, User
from datetime import datetime, timedelta
from werkzeug.security import generate_password_hash, check_password_hash


main = Blueprint('main', __name__)

INACTIVITY_TIMEOUT = timedelta(minutes=15)


def is_session_active():
    """ Check if user session is active or expired """
    last_activity = session.get('last_activity')
    if last_activity:
        elapsed_time = datetime.utcnow() - datetime.fromtimestamp(last_activity)
        if elapsed_time > INACTIVITY_TIMEOUT:
            session.clear()  # Logout user
            flash("You have been logged out due to inactivity.", "info")
            return False
    session['last_activity'] = datetime.utcnow(
    ).timestamp()
    return True


@main.before_request
def check_session():
    """ Automatically logout inactive users """
    if 'user_id' in session and not is_session_active():
        return redirect(url_for('main.login'))


@main.route('/')
def home():
    print("Session Data:", session)
    user = None
    user_id = session.get("user_id")

    if user_id:
        user = User.query.get(user_id)
        print("Retrieved User:", user)

    return render_template('index.html', user=user)


@main.route('/about')
def about():
    return render_template('about.html')


@main.route('/plans')
def plans():
    return render_template('plans.html')


@main.route('/testimonials')
def testimonials():
    return render_template('testimonials.html')


@main.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(username=form.username.data).first()

        if not user or not check_password_hash(user.password, form.password.data):
            flash('Invalid credentials. Please try again.', 'danger')
            return redirect(url_for('main.login'))

        session['user_id'] = user.id
        session.permanent = True
        session.modified = True
        session['last_activity'] = datetime.utcnow().timestamp()
        flash('Login successful! Welcome back.', 'success')
        return redirect(url_for('main.home'))

    if request.method == "POST":
        flash('Login failed. Please check your details and try again.', 'warning')

    return render_template('login.html', form=form)


@main.route('/logout')
def logout():
    """ Handle user logout """
    session.clear()
    flash("Logged out successfully.", "success")
    return redirect(url_for('main.login'))


@main.route('/signup', methods=['GET', 'POST'])
def signup():
    form = SignupForm()
    if form.validate_on_submit():
        existing_user_email = User.query.filter_by(
            email=form.email.data).first()
        existing_user_username = User.query.filter_by(
            username=form.username.data).first()

        if existing_user_email:
            flash(
                'Email is already registered. Please use a different one or log in.', 'danger')
            return redirect(url_for('main.signup'))

        if existing_user_username:
            flash('Username is already taken. Please choose a different one.', 'danger')
            return redirect(url_for('main.signup'))

        hashed_password = generate_password_hash(form.password.data)
        new_user = User(
            fullname=form.fullname.data,
            username=form.username.data,
            email=form.email.data,
            password=hashed_password
        )
        db.session.add(new_user)
        db.session.commit()

        flash('Registration successful! You can now log in.', 'success')
        return redirect(url_for('main.login'))

    if request.method == "POST":
        flash('Signup failed. Please check your details and try again.', 'warning')

    return render_template('signup.html', form=form)


@main.route('/api/parking-spots', methods=['GET'])
def get_parking_spots():
    spots = ParkingSpot.query.all()
    spots_list = [{'id': spot.id, 'name': spot.name,
                   'location': spot.location} for spot in spots]
    return jsonify(spots_list)


@main.route('/api/book', methods=['POST'])
def book():
    if 'user_id' not in session:
        return jsonify({"error": "Unauthorized: You must log in first."}), 401

    data = request.get_json()

    required_fields = ['location_id', 'check_in_date',
                       'check_in_time', 'check_out_date', 'check_out_time']
    missing = [field for field in required_fields if not data.get(field)]

    if missing:
        return jsonify({"error": f"Missing required fields: {', '.join(missing)}"}), 400

    # Create and save a new booking
    new_booking = Booking(
        user_id=session['user_id'],
        location_id=data['location_id'],
        check_in_date=data['check_in_date'],
        check_in_time=data['check_in_time'],
        check_out_date=data['check_out_date'],
        check_out_time=data['check_out_time'],
        promo_code=data.get('promo_code'),
        status="pending"
    )
    db.session.add(new_booking)
    db.session.commit()

    return jsonify({
        "message": "Booking successful",
        "booking_id": new_booking.id
    }), 200


@main.route('/api/user-info')
def user_info():
    if 'user_id' not in session:
        return jsonify({"error": "Not logged in"}), 401

    user = User.query.get(session['user_id'])
    if not user:
        return jsonify({"error": "User not found"}), 404

    return jsonify({"name": user.name})


@main.route('/dashboard')
def dashboard():
    if 'user_id' not in session:
        return redirect(url_for('main.login'))

    user_id = session['user_id']
    user = User.query.get(user_id)
    bookings = Booking.query.filter_by(user_id=user_id).all()

    return render_template('dashboard.html', user=user, bookings=bookings)


@main.route('/api/bookings/<int:booking_id>/status', methods=['PUT'])
def update_booking_status(booking_id):
    if 'user_id' not in session:
        return jsonify({"error": "Unauthorized"}), 401

    data = request.get_json()
    new_status = data.get("status")

    if new_status not in ["pending", "confirmed", "canceled"]:
        return jsonify({"error": "Invalid status"}), 400

    booking = Booking.query.get(booking_id)
    if not booking:
        return jsonify({"error": "Booking not found"}), 404

    booking.status = new_status
    db.session.commit()

    return jsonify({
        "message": f"Booking status updated to {new_status}",
        "booking_id": booking.id,
        "status": booking.status
    }), 200
