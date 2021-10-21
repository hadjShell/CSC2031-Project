import re
from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, PasswordField
from wtforms.validators import Required, Email, Length, ValidationError


class RegisterForm(FlaskForm):
    # use validators to ensure all fields must be filled and in proper forms
    email = StringField(validators=[Required(), Email()])
    firstname = StringField(validators=[Required()])
    lastname = StringField(validators=[Required()])
    phone = StringField(validators=[Required()])
    # Password must be between 6 and 12 characters in length
    password = PasswordField(validators=[Required(),
                                         Length(min=6, max=12, message='Password must be between 6 and 12 characters in length.')])
    confirm_password = PasswordField(validators=[Required()])
    pin_key = StringField(validators=[Required()])
    submit = SubmitField()

    # Password must contain at least 1 digit, 1 lowercase, 1 uppercase and 1 special character
    def validate_password(self, password):
        p = re.compile(r'(?=.*\d)(?=.*[A-Z])(?=.*[a-z])(?=.*[^A-Za-z0-9])')
        if not p.match(self.password.data):
            raise ValidationError("Password must contain at least 1 digit, 1 lowercase, 1 uppercase and 1 special character.")
