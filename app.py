import os

from flask import Flask, render_template, url_for, request, redirect, session
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
from fileinput import filename

from werkzeug.utils import secure_filename

from models import db_teacher, db_funcs
from keyy import secret_key
from flask_login import UserMixin, login_user, LoginManager, login_required, logout_user, current_user
# Секретний код для реєстрації вчителя
from teacher_secret_code import TEACHER_SECRET_CODE

app = Flask(__name__)
app.secret_key = secret_key
# app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///blog.db'

app.config['UPLOAD_FOLDER'] = 'static/uploads/'
# app.config['MAX_CONTENT_PATH'] = 16 * 1024 * 1024  # Максимальний розмір файлу - 16 MB
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif'}
if not os.path.exists(app.config['UPLOAD_FOLDER']):
    os.makedirs(app.config['UPLOAD_FOLDER'])

def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


# db = SQLAlchemy(app)


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

        if 'file' not in request.files:
            return "No photo part"
        file = request.files['file']
        if file.filename == '':
            return "No selected photo"
        if file and allowed_file(file.filename):
            filename = secure_filename(file.filename)
            file_path = filename
            file_path_save = os.path.join(app.config['UPLOAD_FOLDER'], filename)
            file.save(file_path_save)

            # Зберігаємо дані користувача у базі даних
            user_id = db_funcs.insert_table(name, surname, midname, email, phone, password, file_path)

            session['logged'] = True
            session['role'] = 'student'
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

        if 'file' not in request.files:
            return "No photo part"
        file = request.files['file']
        if file.filename == '':
            return "No selected photo"
        if file and allowed_file(file.filename):
            filename = secure_filename(file.filename)
            file_path = filename
            file_path_save = os.path.join(app.config['UPLOAD_FOLDER'], filename)
            file.save(file_path_save)
            file.save(file_path)

            # Зберігаємо дані користувача у базі даних
            user_id = db_teacher.insert_user_and_teacher(name, surname, midname, email, phone, password, file_path,
                                    education, 0, 0, level, start_work)
            session['logged'] = True
            session['role'] = 'teacher'
            session['user_id'] = user_id
            return redirect(url_for('index'))
    return render_template('register_teacher.html')


@app.route('/log_in', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']
        user_data = db_funcs.is_in_table(email, password)

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
    user_id = session['user_id']
    user_teacher_info = db_teacher.get_teacher_info(user_id)
    return render_template('/profiles/teacher.html', user=user_teacher_info)

@app.route('/profiles/student')
def student_profile():
    user_id = session['user_id']
    user_teacher_info = db_teacher.get_teacher_info(user_id)
    return render_template('/profiles/student.html', user=user_teacher_info)


@app.route('/teachers')
def show_teachers():
    teachers = db_teacher.get_all_teachers()
    return render_template('teachers.html', teachers=teachers)


@app.route('/update_teacher_info', methods=['POST'])
def update_teacher_info():
    user_id = session.get('user_id')  # Assuming you store the user's ID in the session
    if not user_id:
        return redirect(url_for('login'))  # Redirect to login if user not logged in

    name = request.form['name']
    surname = request.form['surname']
    midname = request.form['midname']
    email = request.form['email']
    phone = request.form['phone']

    photo = request.files['photo']
    photo_filename = None
    if photo:
        print("photo")
        print(photo)
        photo_filename = secure_filename(photo.filename)
        photo.save(os.path.join('static/uploads', photo_filename))

    db_teacher.update_teacher_info(name, surname, midname, email, phone, user_id, photo_filename)
    return redirect(url_for('teacher_profile'))



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