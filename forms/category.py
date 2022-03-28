from flask_wtf import FlaskForm
from wtforms import StringField
from wtforms import SubmitField
from wtforms.validators import DataRequired
from wtforms.widgets import ColorInput


class CategoryForm(FlaskForm):
    name = StringField('Название', validators=[DataRequired()], render_kw={"placeholder": 'Название'})
    color = StringField('Цвет', widget=ColorInput(), validators=[DataRequired()])
    submit = SubmitField('Готово')

