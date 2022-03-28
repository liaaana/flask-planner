<h1 align="center">Flask Planner</h1>

<p align="center">


<img src="https://img.shields.io/badge/python-3.5.7-yellow.svg">

<img src="https://img.shields.io/badge/flask-2.0.2-blue.svg">

</p>

Web-based planning application

---
Web application in which you can add, modify, delete and mark tasks as completed. Tasks that have a specific date can be seen in the calendar.

It is also possible to create categories and assign tasks to them. Categories can be changed and removed with or without removal of all the tasks included in this category. 


Made with the Flask framework in Python language


<p align="center">
<img src="https://media.giphy.com/media/A6EkYOlNEhTFy8rrSp/giphy.gif">
</p>

# Installation and launching

```
# make sure that you are in the project folder
pip install requirements.txt 
python3 main.py 
```


### Example of creating a "task_add" function.

**1. Creating a task model, where you specify what parameters each task has.**

```python
import sqlalchemy
from sqlalchemy import orm
from sqlalchemy_serializer import SerializerMixin
from .db_session import SqlAlchemyBase


class Task(SqlAlchemyBase, SerializerMixin):
    __tablename__ = 'tasks'
    id = sqlalchemy.Column(sqlalchemy.Integer, primary_key=True, autoincrement=True)
    title = sqlalchemy.Column(sqlalchemy.String, nullable=True)
    content = sqlalchemy.Column(sqlalchemy.String, nullable=True)
    date = sqlalchemy.Column(sqlalchemy.DateTime, default=None)
    start_time = sqlalchemy.Column(sqlalchemy.Time, default=None)
    end_time = sqlalchemy.Column(sqlalchemy.Time, default=None)
    is_done = sqlalchemy.Column(sqlalchemy.Boolean, default=False)
    user_id = sqlalchemy.Column(sqlalchemy.Integer, sqlalchemy.ForeignKey("users.id"))
    category_id = sqlalchemy.Column(sqlalchemy.Integer, sqlalchemy.ForeignKey("categories.id"))
    user = orm.relation('User')
    category = orm.relation('Category')
```

**2. Next, the creation of a form, through which the user can add his tasks.**

```python
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


```
**3. Using the basic template "base.html", we create an html page with which the user will interact.**



```html
{% extends "base.html" %}

{% block style %}
<link rel="stylesheet" href="../static/css/task_add_style.css">
{% endblock %}

{% block content %}
<div class="add_task">
<h2>{{ title }}</h2>
<form action="" method="post">
    {{ form.hidden_tag() }}
    <p>
        {{ form.title(class="form-control") }}<br>
        {% for error in form.title.errors %}
            <p class="alert alert-danger" role="alert">
                {{ error }}
            </p>
        {% endfor %}
    </p>
    <p>
        {{ form.content(class="form-control") }}<br>
        {% for error in form.content.errors %}
            <p class="alert alert-danger" role="alert">
                {{ error }}
            </p>
        {% endfor %}
    </p>
    <p>
        {{ form.date(class="form-control") }}<br>
        {% for error in form.date.errors %}
        <p class="alert alert-danger" role="alert">
            {{ error }}
        </p>
        {% endfor %}
    </p>
    <p>
        {{ form.start_time(class="form-control") }}<br>
        {% for error in form.start_time.errors %}
        <p class="alert alert-danger" role="alert">
            {{ error }}
        </p>
        {% endfor %}
    </p>
    <p>
        {{ form.end_time(class="form-control") }}<br>
        {% for error in form.end_time.errors %}
        <p class="alert alert-danger" role="alert">
            {{ error }}
        </p>
        {% endfor %}
    </p>
    <p>
        <div class='form_radio_group'>
        {% for i, ctg in form.category.choices %}
        <div class="form_radio_group-item">
            {% if ctg.id == form.category.default %}
            <input checked id={{ctg.id}}  name="category" type="radio" value={{ ctg.id }}>
            {% else %}
            <input id={{ctg.id}}  name="category" type="radio" value={{ ctg.id }}>
            {% endif %}
            <label for={{ctg.id}}>{{ ctg.name }}</label>
        </div>
        {% endfor %}
        </div>
        {% for error in form.category.errors %}
        <p class="alert alert-danger" role="alert">
            {{ error }}
        </p>
        {% endfor %}
    </p>
    <p>{{ form.submit(type="submit", class="button") }}</p>
    <p class='message'>{{message}}</p>
</form>
</div>
{% endblock %}
```
**4. As the last step, we connect the html page to the address '.../task_add' in main.py. The same function detects errors, takes the user back and tells him what needs to be fixed.**


```python
@app.route('/task_add', methods=['GET', 'POST']) # добавление задачи
@login_required
def add_task():
    form = TaskForm()
    db_sess = db_session.create_session()
    categories = db_sess.query(Category).filter(Category.user_id == current_user.id).all()
    form.category.choices = [(i.id, i) for i in categories]
    form.category.default = [i for i in categories if i.name == 'Без категории'][0].id
    if form.validate_on_submit():
        if request.form.get('category') is None:
            return render_template('task_add.html',
                                   title='Добавление задачи',
                                   form=form,
                                   message='Необходимо выбрать категорию',
                                   date=datetime.datetime.now())
        elif form.date.data is not None and form.date.data < datetime.date.today():
            form.category.default = int(request.form.get('category'))
            return render_template('task_add.html',
                                   title='Добавление задачи',
                                   form=form,
                                   message='Выбрана дата из прошлого',
                                   date=datetime.datetime.now())
        elif form.start_time.data is not None and form.end_time.data is not None and form.start_time.data > form.end_time.data:
            form.category.default = int(request.form.get('category'))
            return render_template('task_add.html',
                                   title='Добавление задачи',
                                   form=form,
                                   message='Время начала позже времени окончания',
                                   date=datetime.datetime.now())
        elif form.start_time.data is not None and form.end_time.data is None:
            form.category.default = int(request.form.get('category'))
            return render_template('task_add.html',
                                   title='Добавление задачи',
                                   form=form,
                                   message='Добавьте время окончания',
                                   date=datetime.datetime.now())
        elif form.start_time.data is None and form.end_time.data is not None:
            form.category.default = int(request.form.get('category'))
            return render_template('task_add.html',
                                   title='Добавление задачи',
                                   form=form,
                                   message='Время начала позже времени окончания',
                                   date=datetime.datetime.now())
        elif len(form.title.data) > 100 or len(form.title.data) < 1:
            form.category.default = int(request.form.get('category'))
            return render_template('task_add.html',
                                   title='Добавление задачи',
                                   form=form,
                                   message='Заголовок задачи должен быть от 1 до 100 символов',
                                   date=datetime.datetime.now())
        task = Task()
        task.title = form.title.data
        task.content = form.content.data
        task.date = form.date.data
        task.start_time = form.start_time.data
        task.end_time = form.end_time.data
        task.category_id = int(request.form.get('category'))
        current_user.tasks.append(task)
        db_sess.merge(current_user)
        db_sess.commit()
        return redirect('/tasks')
    return render_template('task_add.html',
                           title='Добавление задачи',
                           form=form,
                           date=datetime.datetime.now())
   ```
### Several challenges

| Problem                                                                                                        | Solution                                                                    |
|----------------------------------------------------------------------------------------------------------------|-----------------------------------------------------------------------------|
| Registration and authorization take place on one page, and it is impossible to connect 2 functions to one page | Create 2 different forms and perform processing depending on the form sent. | 
| Each task should have a category, but when a user tries to create the first task, it may not have any category | Automatically create a category when a new user is added                    |
| In this project I put into practice the knowledge of the course flask but I wanted to have beautiful design    | I used designs from public sources and YouTube tutorials                    |


### All functions

- login_register
- tasks
- add_task
- edit_task
- task_delete
- tasks_calendar
- categories
- add_category
- edit_category
- category_delete (without deleting tasks in this category)
- category_delete_with_tasks

### Some more gifs
<p align="center">
<img src="https://media.giphy.com/media/lCAyCdjidoJakEvnVt/giphy.gif">
</p>
<p align="center">
<img src="https://media.giphy.com/media/linYZc5q5P4CdPjTVl/giphy.gif">
</p>
<p align="center">
<img src="https://media.giphy.com/media/CgGcH5xi3LN0I58u6d/giphy.gif">
</p>
<p align="center">
<img src="https://media.giphy.com/media/Yz5CpvXB7gmxTbUSai/giphy.gif">
</p>
<p align="center">
<img src="https://media.giphy.com/media/nVLMcseE4MFHzQ8rRV/giphy.gif">
</p>
<p align="center">
<img src="https://media.giphy.com/media/wkrjtoyTgpt2q9p1xT/giphy.gif">
</p>