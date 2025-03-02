from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField, BooleanField
from wtforms.validators import DataRequired, Length, Email, EqualTo


class LoginForm(FlaskForm):
    username = StringField("Username", validators=[
                           DataRequired(), Length(min=3, max=20)])
    password = PasswordField("Password", validators=[DataRequired()])
    remember = BooleanField("Remember Me")
    submit = SubmitField("Login")


class SignupForm(FlaskForm):
    fullname = StringField("Full Name", validators=[DataRequired()])
    email = StringField("Email", validators=[DataRequired(), Email()])
    username = StringField("Username", validators=[
                           DataRequired(), Length(min=3, max=20)])
    password = PasswordField("Password", validators=[
                             DataRequired(), Length(min=6)])
    confirm_password = PasswordField("Confirm Password", validators=[
                                     DataRequired(), EqualTo('password')])
    terms = BooleanField("Accept Terms", validators=[DataRequired()])
    submit = SubmitField("Sign Up")
