from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, PasswordField
from wtforms.validators import Required, Email


class RegisterForm(FlaskForm):
    # use validators to ensure all fields must be filled and in proper forms
    email = StringField(validators=[Required(), Email()])
    firstname = StringField(validators=[Required()])
    lastname = StringField(validators=[Required()])
    phone = StringField(validators=[Required()])
    password = PasswordField(validators=[Required()])
    confirm_password = PasswordField(validators=[Required()])
    pin_key = StringField(validators=[Required()])
    submit = SubmitField()
