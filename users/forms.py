import re
from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, PasswordField
from wtforms.validators import Required, Email, Length, ValidationError, EqualTo


# check if a field contains specific characters and digits, return error if yes
def character_check(form, field):
    excluded_chars = "*?!'^+%&/()=}][{$#@<>0123456789"
    for char in field.data:
        if char in excluded_chars:
            raise ValidationError(
                f"Character {char} is not allowed.")


class RegisterForm(FlaskForm):
    # all fields must be filled and in proper forms
    email = StringField(validators=[Required(), Email()])
    # name must not contain specific characters and digits
    firstname = StringField(validators=[Required(), character_check])
    lastname = StringField(validators=[Required(), character_check])
    phone = StringField(validators=[Required()])
    # Password must be between 6 and 12 characters in length
    password = PasswordField(validators=[Required(),
                                         Length(min=6, max=12, message='Password must be between 6 and 12 characters in length.')])
    # Password and confirm_password must match
    confirm_password = PasswordField(validators=[Required(),
                                                 EqualTo('password', message='Both password fields must be equal!')])
    pin_key = StringField(validators=[Required()])
    submit = SubmitField()

    # check if password contains at least 1 digit, 1 lowercase, 1 uppercase and 1 special character, return error if not
    def validate_password(self, password):
        p = re.compile(r'(?=.*\d)(?=.*[A-Z])(?=.*[a-z])(?=.*[^A-Za-z0-9])')
        if not p.match(self.password.data):
            raise ValidationError("Password must contain at least 1 digit, 1 lowercase, 1 uppercase and 1 special character.")
