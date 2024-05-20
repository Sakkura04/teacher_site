from flask import Flask, render_template, url_for, request, redirect, session
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
from models import db_teacher, db_student, db_funcs
from keyy import secret_key
from flask_login import UserMixin, login_user, LoginManager, login_required, logout_user, current_user
from flask_session import Session
# Секретний код для реєстрації вчителя
from teacher_secret_code import TEACHER_SECRET_CODE

app = Flask(__name__,
            template_folder='./templates/',
            static_folder='./static/')
app.secret_key = secret_key


@app.route('/')
def index():
    return render_template('index.html')


@app.route('/sign_up', methods=['GET', 'POST'])
def registration():
    if not db_funcs.table_exists('users'):
        db_funcs.create_user_table()

    if request.method == 'POST':
        if 'teacher' in request.form:
            return redirect(url_for('teacher_code'))

        name = request.form['name']
        surname = request.form['surname']
        midname = request.form['midname']
        email = request.form['email']
        phone = request.form['phone']
        password = request.form['password']

        # Зберігаємо дані користувача у базі даних
        db_funcs.insert_table(name, surname, midname, email, phone, password)

        # Перенаправляємо користувача на іншу сторінку
        return redirect(url_for('index'))
    return render_template('sign_up.html')


@app.route('/teacher_code', methods=['GET', 'POST'])
def teacher_code():
    if request.method == 'POST':
        secret_code = request.form['secret_code']
        if secret_code == TEACHER_SECRET_CODE:
            return redirect(url_for('register_teacher'))
        else:
            error = "Incorrect secret code. Please try again."
            return render_template('teacher_code.html', error=error)

    return render_template('teacher_code.html')


@app.route('/register_teacher', methods=['GET', 'POST'])
def register_teacher():
    if not db_funcs.table_exists('users'):
        db_funcs.create_user_table()

    if not db_funcs.table_exists('teacher'):
        db_teacher.create_teacher_table()

    if request.method == 'POST':
        secret_code = request.form['secret_code']
        if not secret_code == TEACHER_SECRET_CODE:
            error = "Incorrect teacher code. Please try again."
            return render_template('register_teacher.html', error=error)
        else:
            name = request.form['name']
            surname = request.form['surname']
            midname = request.form['midname']
            email = request.form['email']
            phone = request.form['phone']
            password = request.form['password']
            education = request.form['education']
            group_count = 0
            indiv_count = 0
            level = request.form['level']
            start_work = request.form['start_work']
            user_id = db_teacher.insert_user_and_teacher(name, surname, midname, email, phone, password, education,
                                                         group_count, indiv_count, level, start_work)
            session['logged'] = True
            session['role'] = 'teacher'
            session['user_id'] = user_id
            return redirect(url_for('index'))

    return render_template('register_teacher.html')


@app.route('/register_student', methods=['GET', 'POST'])
def register_student():
    if not db_funcs.table_exists('users'):
        db_funcs.create_user_table()

    if not db_funcs.table_exists('student'):
        db_student.create_student_table()

    if request.method == 'POST':
        name = request.form['name']
        surname = request.form['surname']
        midname = request.form['midname']
        email = request.form['email']
        phone = request.form['phone']
        password = request.form['password']
        lesson_id = 0
        grade = 0
        level = request.form['level']
        start_educ = request.form['start_educ']
        user_id = db_student.insert_user_and_student(name, surname, midname, email, phone, password, lesson_id, grade,
                                                     level, start_educ)
        session['logged'] = True
        session['role'] = 'student'
        session['user_id'] = user_id
        return redirect(url_for('index'))

    return render_template('register_student.html')


@app.route('/log_in', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']
        user_data = db_funcs.is_in_table(email, password)
        if user_data['logged_in'] == True:
            session['logged'] = True
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
    user_id = session['user_id']
    user_teacher_info = db_teacher.get_teacher_info(user_id)
    return render_template('/profiles/teacher.html', user=user_teacher_info)


@app.route('/profiles/student')
def student_profile():
    user_id = session['user_id']
    user_student_info = db_student.get_student_info(user_id)
    return render_template('/profiles/student.html', user=user_student_info)


@app.context_processor
def inject_is_authenticated():
    if 'logged' in session:
        is_authenticated = True
    else:
        is_authenticated = False

    return dict(is_authenticated=is_authenticated)


class User(UserMixin):
    def __init__(self, id, role):
        self.id = id
        self.role = role

    def get_id(self):
        return self.id

    def is_teacher(self):
        return self.role == 'teacher'

    def is_student(self):
        return self.role == 'student'


if __name__ == '__main__':
    app.run(debug=True)
