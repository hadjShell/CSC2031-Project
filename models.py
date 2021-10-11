from datetime import datetime
from flask_login import UserMixin
from app import db


class User(db.Model, UserMixin):
    __tablename__ = 'users'

    id = db.Column(db.Integer, primary_key=True)

    # User authentication information.
    email = db.Column(db.String(100), nullable=False, unique=True)
    password = db.Column(db.String(100), nullable=False)
    pin_key = db.Column(db.String(100), nullable=False)

    # User activity information
    registered_on = db.Column(db.DateTime, nullable=True)
    last_logged_in = db.Column(db.DateTime, nullable=True)
    current_logged_in = db.Column(db.DateTime, nullable=True)

    # User information
    firstname = db.Column(db.String(100), nullable=False)
    lastname = db.Column(db.String(100), nullable=False)
    phone = db.Column(db.String(100), nullable=False)
    role = db.Column(db.String(100), nullable=False, default='user')

    # crypto key for user's lottery draws
    draw_key = db.Column(db.BLOB)

    # Define the relationship to Draw
    draws = db.relationship('Draw')

    def __init__(self, email, firstname, lastname, phone, password, pin_key, role):
        self.email = email
        self.firstname = firstname
        self.lastname = lastname
        self.phone = phone
        self.password = password
        self.pin_key = pin_key
        self.draw_key = None
        self.role = role
        self.registered_on = datetime.now()
        self.last_logged_in = None
        self.current_logged_in = None


class Draw(db.Model):
    __tablename__ = 'draws'

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey(User.id), nullable=False)
    draw = db.Column(db.String(100), nullable=False)
    played = db.Column(db.BOOLEAN, nullable=False, default=False)
    match = db.Column(db.BOOLEAN, nullable=False, default=False)
    win = db.Column(db.BOOLEAN, nullable=False)
    round = db.Column(db.Integer, nullable=False, default=0)

    def __init__(self, user_id, draw, win, round):
        self.user_id = user_id
        self.draw = draw
        self.played = False
        self.match = False
        self.win = win
        self.round = round


def init_db():
    db.drop_all()
    db.create_all()
    admin = User(email='admin@email.com',
                 password='Admin1!',
                 pin_key='BFB5S34STBLZCOB22K6PPYDCMZMH46OJ',
                 firstname='Alice',
                 lastname='Jones',
                 phone='0191-123-4567',
                 role='admin')

    db.session.add(admin)
    db.session.commit()


