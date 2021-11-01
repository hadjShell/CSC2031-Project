# IMPORTS
import logging
from datetime import datetime
from functools import wraps
import pyotp
from flask import Blueprint, render_template, flash, redirect, url_for, request, session, current_app
from flask_login import login_user, logout_user, current_user
from flask_login.config import EXEMPT_METHODS
from werkzeug.security import check_password_hash
from app import db
from models import User
from users.forms import RegisterForm, LoginForm

# CONFIG
users_blueprint = Blueprint('users', __name__, template_folder='templates')


# custom login _required decorator
def login_required(func):
    @wraps(func)
    def decorated_view(*args, **kwargs):
        if request.method in EXEMPT_METHODS:
            return func(*args, **kwargs)
        elif not current_user.is_authenticated:
            # log anonymous users invalid attempts
            logging.warning('SECURITY - Anonymous invalid access [%s]', request.remote_addr)
            return current_app.login_manager.unauthorized()
        return func(*args, **kwargs)

    return decorated_view


# VIEWS
# view registration
@users_blueprint.route('/register', methods=['GET', 'POST'])
def register():
    # create signup form object
    form = RegisterForm()

    # if request method is POST or form is valid
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        # if this returns a user, then the email already exists in database

        # if email already exists redirect user back to signup page with error message so user can try again
        if user:
            flash('Email address already exists')
            return render_template('register.html', form=form)

        # create a new user with the form data
        new_user = User(email=form.email.data,
                        firstname=form.firstname.data,
                        lastname=form.lastname.data,
                        phone=form.phone.data,
                        password=form.password.data,
                        pin_key=form.pin_key.data,
                        role='user')

        # add the new user to the database
        db.session.add(new_user)
        db.session.commit()

        # log user registration
        logging.warning('SECURITY - User registration [%s, %s, %s]',
                        form.firstname.data, form.lastname.data, request.remote_addr)

        # sends user to login page
        return redirect(url_for('users.login'))

    # if request method is GET or form not valid re-render signup page
    return render_template('register.html', form=form)


# view user login
@users_blueprint.route('/login', methods=['GET', 'POST'])
def login():
    # if session attribute logins does not exist create attribute logins
    if not session.get('logins'):
        session['logins'] = 0
    # if login attempts is 3 or more create an error message
    elif session.get('logins') >= 3:
        flash('Number of incorrect logins exceeded')

    form = LoginForm()

    if form.validate_on_submit():
        # increase login attempts by 1
        session['logins'] += 1

        user = User.query.filter_by(email=form.email.data).first()

        # username not matched or associated password not matched
        if not user or not check_password_hash(user.password, form.password.data):
            # if no match create appropriate error message based on login attempts
            if session['logins'] == 3:
                flash('Number of incorrect logins exceeded')
            elif session['logins'] == 2:
                flash('Please check your login details and try again. 1 login attempt remaining')
            else:
                flash('Please check your login details and try again. 2 login attempts remaining')

            # log user invalid login
            logging.warning('SECURITY - Invalid login attempt [%s, %s, %s, %s]',
                            current_user.id, current_user.firstname, current_user.lastname, request.remote_addr)

            return render_template('login.html', form=form)

        # generation of user's PIN key matched user's input token
        if pyotp.TOTP(user.pin_key).verify(form.pin.data):
            # if user is verified reset login attempts to 0
            session['logins'] = 0

            login_user(user)

            # record login activity into database
            user.last_logged_in = user.current_logged_in
            user.current_logged_in = datetime.now()
            db.session.add(user)
            db.session.commit()

            # log user login
            logging.warning('SECURITY - Log in [%s, %s, %s, %s]',
                            current_user.id, current_user.firstname, current_user.lastname, request.remote_addr)

            # end user goes to profile page, admin goes to admin page
            if current_user.role == 'admin':
                return redirect(url_for('admin.admin'))
            else:
                return redirect(url_for('users.profile'))
        else:
            flash("You have supplied an invalid 2FA token!", "danger")

    return render_template('login.html', form=form)


# view user profile
@users_blueprint.route('/profile')
@login_required
def profile():
    return render_template('profile.html', name=current_user.firstname)


# view user account
@users_blueprint.route('/account')
@login_required
def account():
    return render_template('account.html',
                           acc_no=current_user.id,
                           email=current_user.email,
                           firstname=current_user.firstname,
                           lastname=current_user.lastname,
                           phone=current_user.phone)


# view user logout
@users_blueprint.route('/logout')
@login_required
def logout():
    # log user logout
    logging.warning('SECURITY - Log out [%s, %s, %s, %s]',
                    current_user.id, current_user.firstname, current_user.lastname, request.remote_addr)

    logout_user()
    return redirect(url_for('index'))
