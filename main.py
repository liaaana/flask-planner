from flask import Flask, request
from flask import render_template, redirect
from forms.category import CategoryForm
from resources import task_resources, user_resources, category_resources
from forms.login import LoginForm
from data import db_session
from data.users import User
from data.tasks import Task
from forms.register import RegisterForm
from forms.task import TaskForm
from data.categories import Category
import datetime
import calendar
import dateutil.relativedelta
from flask_login import LoginManager, login_user, login_required, logout_user, current_user
from flask_restful import abort, Api
from forms.tasks import TasksForm

app = Flask(__name__)
api = Api(app)
login_manager = LoginManager()
login_manager.init_app(app)
app.config['SECRET_KEY'] = '192Radbc7sjhHGJcej72'


@app.errorhandler(404)  # при ошибке выдает страницу с кнопкой перехода на главную
def not_found(error):
    return render_template('error.html', title='Ошибка', date=datetime.datetime.now(),
                           msg='Упс! Возникла какая-то ошибка')


@app.errorhandler(401)  # при ошибке выдает страницу с кнопкой перехода на главную
def not_found(error):
    return render_template('error.html', title='Ошибка', date=datetime.datetime.now(),
                           msg='Упс! Возникла какая-то ошибка')


@app.route('/')  # ведет на страницу с регистрацией и авторизацией
@app.route('/index')
def index():
    return redirect('/login_register')


@login_manager.user_loader
def load_user(user_id):
    db_sess = db_session.create_session()
    return db_sess.query(User).get(user_id)


@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect("/")


@app.route('/login_register', methods=['GET', 'POST'])  # регистрации и аворизации пользователя
def login_register():
    form_login = LoginForm()
    form_register = RegisterForm()
    if form_login.validate_on_submit():
        db_sess = db_session.create_session()
        user = db_sess.query(User).filter(User.email == form_login.login_email.data).first()
        if user and user.check_password(form_login.login_password.data):
            login_user(user, remember=form_login.login_remember_me.data)
            return redirect("/tasks")
        return render_template('login_register.html',
                               login_message="Неправильный логин или пароль", form_login=form_login,
                               form_register=form_register, login=True, date=datetime.datetime.now())
    elif form_register.validate_on_submit():
        if form_register.register_password.data != form_register.register_password_again.data:
            return render_template('login_register.html', title='Регистрация', form_login=form_login,
                                   form_register=form_register,
                                   register_message="Пароли не совпадают", login=False, date=datetime.datetime.now())
        db_sess = db_session.create_session()
        if db_sess.query(User).filter(User.email == form_register.register_email.data).first():
            return render_template('login_register.html', title='Регистрация', form_login=form_login,
                                   form_register=form_register,
                                   register_message="Такой пользователь уже есть", login=False,
                                   date=datetime.datetime.now())
        user = User(
            name=form_register.register_name.data,
            surname=form_register.register_surname.data,
            email=form_register.register_email.data,
        )
        user.set_password(form_register.register_password.data)
        db_sess.add(user)
        db_sess.commit()
        session = db_session.create_session()  # каждая задача относится к какой-то категории,поэтому по умолчанию создаем категорию "Без категории"
        category = Category(
            color='110,110,110',
            name='Без категории',
            user_id=user.id
        )
        session.add(category)
        session.commit()

        return redirect('/login_register')
    return render_template('login_register.html', title='Авторизация', form_login=form_login,
                           form_register=form_register, login=True, date=datetime.datetime.now())


@app.route("/tasks", methods=['GET', 'POST'])  # показ всех задач
@login_required
def tasks():
    if current_user.is_authenticated:
        form = TasksForm()
        db_sess = db_session.create_session()
        tasks = db_sess.query(Task).filter(Task.user == current_user).all()
        categories = db_sess.query(Category).filter(Category.user_id == current_user.id).all()
        t_c = {}
        for ctg in categories:
            t_c[ctg.name] = [t for t in tasks if t in ctg.tasks]
        if request.method == 'POST':
            done = request.form.getlist('tasks')
            for task in tasks:
                if str(task.id) in done:
                    task.is_done = 1
                else:
                    task.is_done = 0
            db_sess.commit()
        return render_template("tasks.html",
                               title='Задачи',
                               t_c=t_c,
                               date=datetime.datetime.now(),
                               form=form)
    else:
        return render_template("tasks.html",
                               title='Задачи',
                               date=datetime.datetime.now())


@app.route('/task_add', methods=['GET', 'POST'])  # добавление задачи
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


@app.route('/task_edit/<int:id>', methods=['GET', 'POST'])  # изменине задачи
@login_required
def edit_task(id):
    form = TaskForm()
    db_sess = db_session.create_session()
    categories = db_sess.query(Category).filter(Category.user_id == current_user.id).all()
    form.category.choices = [(i.id, i) for i in categories]
    if request.method == "GET":
        db_sess = db_session.create_session()
        task = db_sess.query(Task).filter(Task.id == id,
                                          Task.user == current_user).first()
        if task:
            form.title.data = task.title
            form.content.data = task.content
            form.date.data = task.date
            form.start_time.data = task.start_time
            form.end_time.data = task.end_time
            form.category.default = task.category_id
        else:
            abort(404)
    if form.validate_on_submit():
        if request.form.get('category') is None:
            return render_template('task_add.html',
                                   title='Редактирование задачи',
                                   form=form,
                                   message='Необходимо выбрать категорию',
                                   date=datetime.datetime.now())
        elif form.date.data is not None and form.date.data < datetime.date.today():
            form.category.default = int(request.form.get('category'))
            return render_template('task_add.html',
                                   title='Редактирование задачи',
                                   form=form,
                                   message='Выбрана дата из прошлого',
                                   date=datetime.datetime.now())
        elif form.start_time.data is not None and form.end_time.data is not None and form.start_time.data > form.end_time.data:
            form.category.default = int(request.form.get('category'))
            return render_template('task_add.html',
                                   title='Редактирование задачи',
                                   form=form,
                                   message='Время начала позже времени окончания',
                                   date=datetime.datetime.now())
        elif form.start_time.data is not None and form.end_time.data is None:
            form.category.default = int(request.form.get('category'))
            return render_template('task_add.html',
                                   title='Редактирование задачи',
                                   form=form,
                                   message='Добавьте время окончания',
                                   date=datetime.datetime.now())
        elif form.start_time.data is None and form.end_time.data is not None:
            form.category.default = int(request.form.get('category'))
            return render_template('task_add.html',
                                   title='Редактирование задачи',
                                   form=form,
                                   message='Время начала позже времени окончания',
                                   date=datetime.datetime.now())
        elif len(form.title.data) > 100 or len(form.title.data) < 1:
            form.category.default = int(request.form.get('category'))
            return render_template('task_add.html',
                                   title='Редактирование задачи',
                                   form=form,
                                   message='Заголовок задачи должен быть от 1 до 100 символов',
                                   date=datetime.datetime.now())
        db_sess = db_session.create_session()
        task = db_sess.query(Task).filter(Task.id == id,
                                          Task.user == current_user).first()
        if task:
            task.title = form.title.data
            task.content = form.content.data
            task.date = form.date.data
            task.start_time = form.start_time.data
            task.end_time = form.end_time.data
            task.category_id = int(request.form.get('category'))
            db_sess.commit()
            return redirect('/tasks')
        else:
            abort(404)
    return render_template('task_add.html',
                           title='Редактирование задачи',
                           form=form,
                           date=datetime.datetime.now())


@app.route('/task_delete/<int:id>', methods=['GET', 'POST'])  # удаление задачи
@login_required
def task_delete(id):
    db_sess = db_session.create_session()
    task = db_sess.query(Task).filter(Task.id == id,
                                      Task.user == current_user
                                      ).first()
    if task:
        db_sess.delete(task)
        db_sess.commit()
    else:
        abort(404)
    return redirect('/tasks')


@app.route("/tasks_calendar/<int:year>/<int:month>", methods=['GET', 'POST'])  # показ задач в календаре
@login_required
def tasks_calendar(year, month):
    if current_user.is_authenticated:
        db_sess = db_session.create_session()
        tasks = db_sess.query(Task).filter(Task.user == current_user).all()
        categories = {i.id: i for i in db_sess.query(Category).filter(Category.user_id == current_user.id).all()}
        cal = calendar.Calendar()
        dates = [i for i in cal.itermonthdates(year, month)]
        dates_tasks = {}
        for task in tasks:
            if task.date is not None:
                task_date = datetime.date(task.date.year, task.date.month, task.date.day)
                if task_date in dates:
                    if task_date not in dates_tasks.keys():
                        dates_tasks[task_date] = [task]
                    else:
                        dates_tasks[task_date].append(task)
        pre_date = datetime.date(year, month, 1) - dateutil.relativedelta.relativedelta(months=1)
        next_date = datetime.date(year, month, 1) + dateutil.relativedelta.relativedelta(months=1)
        months = {1: 'Январь', 2: 'Февраль', 3: 'Март', 4: 'Апрель', 5: 'Май', 6: 'Июнь', 7: 'Июль', 8: 'Август',
                  9: 'Сентябрь', 10: 'Октябрь', 11: 'Ноябрь', 12: 'Декабрь'}
        return render_template("tasks_calendar.html", year=year,
                               month=month,
                               title='Календарь',
                               dates_tasks=dates_tasks,
                               categories=categories,
                               dates=dates,
                               date=datetime.datetime.now(),
                               pre_date=pre_date,
                               next_date=next_date,
                               months=months)
    else:
        return render_template("tasks_calendar.html", title='Календарь', date=datetime.datetime.now())


@app.route("/categories", methods=['GET', 'POST'])  # показ категорий
@login_required
def categories():
    if current_user.is_authenticated:
        db_sess = db_session.create_session()
        categories = db_sess.query(Category).filter(Category.user_id == current_user.id).all()
        return render_template("categories.html",
                               title='Категории',
                               tasks=tasks,
                               categories=categories,
                               date=datetime.datetime.now(),
                               )


def hex_to_rgb(value):  # функция для изменения формата цвета категории
    value = value.lstrip('#')
    lv = len(value)
    return [int(value[i:i + lv // 3], 16) for i in range(0, lv, lv // 3)]


@app.route('/category_add', methods=['GET', 'POST'])  # добавление категории
@login_required
def add_category():
    form = CategoryForm()
    db_sess = db_session.create_session()
    categories = db_sess.query(Category).filter(Category.user_id == current_user.id).all()
    colors = [i.color for i in categories]
    names = [i.name for i in categories]
    if form.validate_on_submit():
        color = hex_to_rgb(form.color.data)
        color = f'{color[0]}, {color[1]}, {color[2]}'
        if len(form.name.data) > 100:
            return render_template('category_add.html',
                                   title='Добавление категории',
                                   form=form,
                                   message='Название категории должно быть от 1 до 100 символов',
                                   date=datetime.datetime.now())
        if color in colors:
            return render_template('category_add.html',
                                   title='Добавление категории',
                                   form=form,
                                   message='Категория с таким цветом уже существует',
                                   date=datetime.datetime.now())
        if form.name.data in names:
            return render_template('category_add.html',
                                   title='Добавление категории',
                                   form=form,
                                   message='Категория с таким названием уже существует',
                                   date=datetime.datetime.now())
        category = Category()
        category.name = form.name.data
        category.color = color
        current_user.categories.append(category)
        db_sess.merge(current_user)
        db_sess.commit()
        return redirect('/categories')
    return render_template('category_add.html',
                           title='Добавление категории',
                           form=form,
                           date=datetime.datetime.now())


def rgb_to_hex(rgb):  # функция для изменения формата цвета категории
    return '#%02x%02x%02x' % rgb


@app.route('/category_edit/<int:id>', methods=['GET', 'POST'])  # изменение категории
@login_required
def edit_category(id):
    form = CategoryForm()
    db_sess = db_session.create_session()
    categories = db_sess.query(Category).filter(Category.user_id == current_user.id).all()
    colors = [i.color for i in categories if i.id != id]
    names = [i.name for i in categories if i.id != id]
    if request.method == "GET":
        db_sess = db_session.create_session()
        category = db_sess.query(Category).filter(Category.id == id,
                                                  Category.user == current_user).first()
        if category:
            form.name.data = category.name
            color_to_hex = tuple([int(i) for i in category.color.split(',')])
            form.color.data = rgb_to_hex(color_to_hex)
        else:
            abort(404)
    if form.validate_on_submit():
        color = hex_to_rgb(form.color.data)
        color = f'{color[0]}, {color[1]}, {color[2]}'
        if len(form.name.data) > 100:
            return render_template('category_add.html',
                                   title='Редактирование категории',
                                   form=form,
                                   message='Название категории должно быть от 1 до 100 символов',
                                   date=datetime.datetime.now())
        if color in colors:
            return render_template('category_add.html',
                                   title='Редактирование категории',
                                   form=form,
                                   message='Категория с таким цветом уже существует',
                                   date=datetime.datetime.now())
        if form.name.data in names:
            return render_template('category_add.html',
                                   title='Редактирование категории',
                                   form=form,
                                   message='Категория с таким названием уже существует',
                                   date=datetime.datetime.now())
        db_sess = db_session.create_session()
        category = db_sess.query(Category).filter(Category.id == id,
                                                  Category.user == current_user).first()
        if category:
            category.name = form.name.data
            category.color = color
            db_sess.commit()
            return redirect('/categories')
        else:
            abort(404)
    return render_template('category_add.html',
                           title='Редактирование категории',
                           form=form,
                           date=datetime.datetime.now())


@app.route('/category_delete/<int:id>', methods=['GET', 'POST'])  # удаление категории без удаления всех входящих задач
@login_required
def category_delete(id):
    db_sess = db_session.create_session()
    category = db_sess.query(Category).filter(Category.id == id, Category.user_id == current_user.id).first()
    categories = db_sess.query(Category).filter(Category.user_id == current_user.id).all()
    category_without_category_id = [i for i in categories if i.name == 'Без категории'][
        0].id  # чтобы переместить туда все задачи из удаляемой категории
    if category:
        tasks = db_sess.query(Task).filter(Task.user_id == current_user.id).all()
        for task in tasks:
            if task.category_id == id:
                task.category_id = category_without_category_id
                db_sess.commit()
        db_sess.delete(category)
        db_sess.commit()
    else:
        abort(404)
    return redirect('/categories')


@app.route('/category_delete_with_tasks/<int:id>',
           methods=['GET', 'POST'])  # удаление категории со всеми входящими задачами
@login_required
def category_delete_with_tasks(id):
    db_sess = db_session.create_session()
    category = db_sess.query(Category).filter(Category.id == id, Category.user_id == current_user.id).first()
    if category:
        tasks = db_sess.query(Task).filter(Task.user_id == current_user.id).all()
        for task in tasks:
            if task.category_id == id:
                db_sess.delete(task)
            db_sess.commit()
        db_sess.delete(category)
        db_sess.commit()
    else:
        abort(404)
    return redirect('/categories')


def main():
    db_session.global_init("db/planner.db")  # подключение к бд
    api.add_resource(task_resources.TasksResource, '/api/tasks')
    api.add_resource(task_resources.TaskResource, '/api/tasks/<int:task_id>')
    api.add_resource(user_resources.UsersResource, '/api/users')
    api.add_resource(user_resources.UserResource, '/api/users/<int:user_id>')
    api.add_resource(category_resources.CategoriesResource, '/api/categories')
    api.add_resource(category_resources.CategoryResource, '/api/categories/<int:category_id>')
    app.run(port=5000, host='127.0.0.1', debug=True)


if __name__ == '__main__':
    main()
