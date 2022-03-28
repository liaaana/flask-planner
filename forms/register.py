from flask_wtf import FlaskForm
from wtforms import PasswordField, StringField, TextAreaField, SubmitField
from wtforms.fields import EmailField
from wtforms.validators import DataRequired


class RegisterForm(FlaskForm):
    register_email = EmailField('Почта', validators=[DataRequired()], render_kw={"placeholder": "Почта"})
    register_password = PasswordField('Пароль', validators=[DataRequired()], render_kw={"placeholder": "Пароль"})
    register_password_again = PasswordField('Повторите пароль', validators=[DataRequired()], render_kw={"placeholder": "Повторите пароль"})
    register_surname = StringField('Фамилия', validators=[DataRequired()], render_kw={"placeholder": "Фамилия"})
    register_name = StringField('Имя', validators=[DataRequired()], render_kw={"placeholder": "Имя"})
    register_submit = SubmitField('Создать аккаунт')