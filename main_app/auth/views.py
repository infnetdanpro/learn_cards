from datetime import datetime
from flask import Blueprint, render_template, flash, request, redirect, url_for
from flask_login import login_user, logout_user, current_user, login_required
from main_app import login_manager
from main_app.auth.models import User
from main_app.auth.forms import RegisterForm, LoginForm
from main_app.database import db
from main_app.tools.password import hash_password, verify_password


auth = Blueprint('auth', __name__, template_folder='templates')


@login_manager.user_loader
def load_user(user_id):
    return User.get(user_id)


@auth.route('/auth/register', methods=['GET', 'POST'])
def register():
    form = RegisterForm(request.form)
    if request.method == 'POST' and form.validate_on_submit():
        user_exists = User.check_exists(email=form.email.data)
        if not user_exists:
            user = User(name=form.name.data, 
                        email=form.email.data, 
                        password=hash_password(form.password.data))
            db.session.add(user)
            db.session.commit()
            flash('User successfully registered', 'success')
            return redirect(url_for('auth.login'))
        else:
            flash('User is exists!', 'danger')
    return render_template('main/auth/register.html', form=form)


@auth.route('/auth/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('card.index'))
    form = LoginForm(request.form)
    if request.method == 'POST' and form.validate_on_submit():
        user = User.get_by_email(email=form.email.data)
        if user:
            password_compared = verify_password(user.password, form.password.data)
            if password_compared:
                user.last_logget_at = datetime.now()
                db.session.commit()
                login_user(user, remember=form.remember.data, force=True)
                flash('User successfully logged in', 'success')
                return redirect(url_for('card.index'))
            flash('User email or password is incorrect', 'danger')
        else:
            flash('User not found', 'danger')
    return render_template('main/auth/login.html', form=form)


@auth.route('/auth/logout', methods=['GET'])
@login_required
def logout():
    if current_user.is_authenticated:
        flash('User successfully logged out', 'warning')
        logout_user()
        return redirect(url_for('card.index'))
    else:
        flash('User not found', 'error')
        return redirect(url_for('card.index'))
