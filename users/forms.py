import re
from flask_wtf import FlaskForm, RecaptchaField
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
                                         Length(min=6, max=12,
                                                message='Password must be between 6 and 12 characters in length.')])
    # Password and confirm_password must match
    confirm_password = PasswordField(validators=[Required(),
                                                 EqualTo('password', message='Both password fields must be equal!')])
    # PIN Key must be exactly 32 characters in length.
    pin_key = StringField(validators=[Required(),
                                      Length(min=32, max=32,
                                             message='PIN Key must be exactly 32 characters in length.')])
    submit = SubmitField()

    # check if password contains at least 1 digit, 1 lowercase, 1 uppercase and 1 special character, return error if not
    def validate_password(self, password):
        p = re.compile(r'(?=.*\d)(?=.*[A-Z])(?=.*[a-z])(?=.*[^A-Za-z0-9])')
        if not p.match(self.password.data):
            raise ValidationError(
                "Password must contain at least 1 digit, 1 lowercase, 1 uppercase and 1 special character.")

    # check if phone is in the valid form, return error if not
    def validate_phone(self, phone):
        p = re.compile(r'(\d{4})-(\d{3})-(\d{4})')
        if not p.match(self.phone.data):
            raise ValidationError("Phone must be of the form XXXX-XXX-XXXX(including dashes).")


class LoginForm(FlaskForm):
    email = StringField(validators=[Required(), Email()])
    password = PasswordField(validators=[Required()])
    pin = StringField(validators=[Required()])
    recaptcha = RecaptchaField()
    submit = SubmitField()
