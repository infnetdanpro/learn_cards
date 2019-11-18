from flask_wtf import FlaskForm
from wtforms import BooleanField, StringField, PasswordField, SubmitField
from wtforms.validators import DataRequired, Email, Length, EqualTo


class RegisterForm(FlaskForm):
    name = StringField('Your name')
    email = StringField('Enter your Email', [DataRequired(), Email('Please enter valid email')])
    password = PasswordField('Password', [Length(min=4, max=25), DataRequired(), EqualTo('confirm_password', message='Password and Confirm password not equal!')])
    confirm_password = PasswordField('Repeat password')
    accept_policy = BooleanField('I read and accept Private Policy', [DataRequired()])
    submit = SubmitField('Register')


class LoginForm(FlaskForm):
    email = StringField('Email', [DataRequired(), Email()])
    password = PasswordField('Password', [Length(min=4, max=25), DataRequired()])
    remember = BooleanField('Remember me')
    submit = SubmitField('Log in')