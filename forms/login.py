from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, BooleanField, SubmitField
from wtforms.fields import EmailField
from wtforms.validators import DataRequired


class LoginForm(FlaskForm):
    login_email = EmailField('Почта', validators=[DataRequired()], render_kw={"placeholder": "Почта"})
    login_password = PasswordField('Пароль', validators=[DataRequired()], render_kw={"placeholder": "Пароль"})
    login_remember_me = BooleanField('Запомнить меня')
    login_submit = SubmitField('Войти')