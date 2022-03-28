from flask_wtf import FlaskForm
from wtforms import SubmitField


class TasksForm(FlaskForm):
    submit = SubmitField('Сохранить')

