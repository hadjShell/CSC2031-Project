from flask_wtf import FlaskForm
from wtforms import SubmitField, IntegerField
from wtforms.validators import Required, NumberRange


class DrawForm(FlaskForm):
    draw_value1 = IntegerField(validators=[Required(),
                                           NumberRange(min=0, max=60, message='Draw value must be between 0 and 60.')])
    draw_value2 = IntegerField(validators=[Required(),
                                           NumberRange(min=draw_value1.data, max=60,
                                                       message='Draw value must be between the previous value and 60.')])
    draw_value3 = IntegerField(validators=[Required(),
                                           NumberRange(min=draw_value2.data, max=60,
                                                       message='Draw value must be between the previous value and 60.')])
    draw_value4 = IntegerField(validators=[Required(),
                                           NumberRange(min=draw_value3.data, max=60,
                                                       message='Draw value must be between the previous value and 60.')])
    draw_value5 = IntegerField(validators=[Required(),
                                           NumberRange(min=draw_value4.data, max=60,
                                                       message='Draw value must be between the previous value and 60.')])
    draw_value6 = IntegerField(validators=[Required(),
                                           NumberRange(min=draw_value5.data, max=60,
                                                       message='Draw value must be between the previous value and 60.')])
    submit = SubmitField()
