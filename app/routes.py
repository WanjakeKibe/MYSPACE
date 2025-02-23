from flask import Blueprint, request, jsonify, session, flash, render_template, url_for, redirect, get_flashed_messages
from .forms import LoginForm, SignupForm
from .models import db, ParkingSpot, Booking, User
import datetime
from werkzeug.security import generate_password_hash, check_password_hash


main = Blueprint('main', __name__)


@main.route('/')
def home():
    return render_template('index.html')


@main.route('/about')
def about():
    return render_template('about.html')


@main.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(username=form.username.data).first()

        if not user:
            flash('Username not found. Please sign up first.', 'danger')
            return redirect(url_for('main.login'))

        if not check_password_hash(user.password, form.password.data):
            flash('Incorrect password. Please try again.', 'danger')
            return redirect(url_for('main.login'))

        session['user_id'] = user.id
        flash('Login successful! Welcome back.', 'success')
        return redirect(url_for('main.home'))

    if request.method == "POST":
        flash('Login failed. Please check your details and try again.', 'warning')

    return render_template('login.html', form=form)


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


# @main.route('/api/parking-spots', methods=['GET'])
# def get_parking_spots():
#     spots = ParkingSpot.query.all()
#     spots_list = [{'id': spot.id, 'name': spot.name,
#                    'location': spot.location} for spot in spots]
#     return jsonify(spots_list)


@main.route('/api/book', methods=['POST'])
def book():
    data = request.get_json()

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
