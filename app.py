from flask import Flask, render_template, url_for, request, redirect, session
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
from models import db_teacher, db_funcs
from keyy import secret_key
from flask_login import UserMixin, login_user, LoginManager, login_required, logout_user, current_user
# Секретний код для реєстрації вчителя
from teacher_secret_code import TEACHER_SECRET_CODE

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///blog.db'
db = SQLAlchemy(app)
app.secret_key = secret_key


@app.route('/')
def index():
    return render_template('index.html')


@app.route('/sign_up', methods=['GET', 'POST'])
def registration():
    if not db_funcs.table_exists('users'):
        db_funcs.create_user_table()
    if not db_funcs.table_exists('teacher'):
        db_teacher.create_teacher_table()

    if request.method == 'POST':
        if 'teacher' in request.form:
            return redirect(url_for('teacher_code'))

        name = request.form['name']
        surname = request.form['surname']
        midname = request.form['midname']
        email = request.form['email']
        phone = request.form['phone']
        password = request.form['password']
        print("222222")

        # Зберігаємо дані користувача у базі даних
        db_funcs.insert_table(name, surname, midname, email, phone, password)

        session['logged'] = True
        session['role'] = 'student'
        # Перенаправляємо користувача на іншу сторінку
        return redirect(url_for('index'))
    return render_template('sign_up.html')


@app.route('/teacher_code', methods=['GET', 'POST'])
def teacher_code():
    print("333333")
    if request.method == 'POST':
        secret_code = request.form['secret_code']
        if secret_code == TEACHER_SECRET_CODE:
            print("4444444444")
            return redirect(url_for('register_teacher'))
        else:
            error = "Incorrect secret code. Please try again."
            return render_template('teacher_code.html', error=error)

    return render_template('teacher_code.html')


@app.route('/register_teacher', methods=['GET', 'POST'])
def register_teacher():
    if request.method == 'POST':
        name = request.form['name']
        surname = request.form['surname']
        midname = request.form['midname']
        email = request.form['email']
        phone = request.form['phone']
        password = request.form['password']
        education = request.form['education']
        level = request.form['level']
        start_work = request.form['start_work']
        db_teacher.insert_user_and_teacher(name, surname, midname, email, phone, password, education, 0, 0,
                                level, start_work)
        session['logged'] = True
        session['role'] = 'teacher'
        return redirect(url_for('index'))
    return render_template('register_teacher.html')


@app.route('/log_in', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']
        user_data = db_funcs.get_from_table(email, password)

        if user_data['logged_in'] == True:
            session['logged'] = True
            print(user_data['user_id'])
            session['user_id'] = user_data['user_id']
            session['role'] = user_data['role']
            return redirect(url_for('index'))
        else:
            error = "Invalid credentials"
            return render_template('log_in.html', error=error)

    return render_template('log_in.html')


@app.route('/sign_out', methods=['GET', 'POST'])
def sign_out():
    if request.method == 'POST':
        session.pop('logged', None)  # Видаляємо ідентифікатор користувача з сесії
        session.pop('user', None)
        return redirect(url_for('index'))
    return render_template('sign_out.html')

@app.route('/profiles/teacher')
def teacher_profile():
    # Витягнемо інформацію про користувача та вчителя
    user_id = 123  # Замініть це на реальний ID користувача
    user_teacher_info = db_teacher.get_teacher_info(user_id)
    return render_template('/profiles/teacher.html', user=user_teacher_info)


@app.context_processor
def inject_is_authenticated():
    if 'logged' in session:
        is_authenticated = True
    else :
        is_authenticated = False

    return dict(is_authenticated=is_authenticated)





# щоб витягнути з юрл інфу робимо <Type: name>
@app.route('/user/<string:name>/<int:id>')
def user(name, id):
    return 'babe, ur name\'s ' + name + ' ' + str (id)

#щоб за різними адресами був однаковий вивід прописуємо:
@app.route('/hay_peach')
@app.route('/peach')
def Sassy():
    return 'Sassy'


class User(UserMixin):
    def __init__(self, id, role):
        self.id = id
        self.role = role

    def get_id(self):
        return self.id

    def is_teacher(self):
        return self.role == 'teacher'



if __name__ == '__main__':
    # with app.app_context():
    #     db.create_all()
    app.run(debug = True)