from flask_wtf import FlaskForm
from wtforms import StringField, TextAreaField
from wtforms import BooleanField, SubmitField, DateField, RadioField, TimeField
from wtforms.validators import DataRequired, Length, InputRequired, Optional
from wtforms.widgets import TimeInput, DateInput


class TaskForm(FlaskForm):
    title = StringField('Заголовок', validators=[DataRequired()],
                        render_kw={"placeholder": 'Заголовок'})
    content = TextAreaField("Содержание", render_kw={"placeholder": 'Содержание'})
    date = DateField('Дата', widget=DateInput(), validators=[Optional()])
    start_time = TimeField('Время начала', widget=TimeInput(), validators=[Optional()])
    end_time = TimeField('Время окончания', widget=TimeInput(), validators=[Optional()])
    category = RadioField('Категория', default=1)
    submit = SubmitField('Готово')

