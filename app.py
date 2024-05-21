import os
from flask import Flask, render_template, url_for, request, redirect, session
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
from fileinput import filename
from werkzeug.utils import secure_filename
from models import db_teacher, db_student, db_funcs, db_lesson
from keyy import secret_key
from flask_login import UserMixin, login_user, LoginManager, login_required, logout_user, current_user
from flask_session import Session
# Секретний код для реєстрації вчителя
from teacher_secret_code import TEACHER_SECRET_CODE

app = Flask(__name__,
            template_folder='./templates/',
            static_folder='./static/')
app.secret_key = secret_key
app.config['UPLOAD_FOLDER'] = 'static/uploads/'

# app.config['MAX_CONTENT_PATH'] = 16 * 1024 * 1024  # Максимальний розмір файлу - 16 MB
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif'}
if not os.path.exists(app.config['UPLOAD_FOLDER']):
    os.makedirs(app.config['UPLOAD_FOLDER'])


def allowed_file(filename):
    return '.' in filename and \
        filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


@app.route('/')
def index():
    return render_template('index.html')


@app.route('/sign_up', methods=['GET', 'POST'])
def registration():
    if 'logged' in session:
        redirect(url_for('index'))

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
    if 'logged' in session:
        redirect(url_for('index'))
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
    if 'logged' in session:
        return redirect(url_for('index'))

    if not db_funcs.table_exists('users'):
        db_funcs.create_user_table()

    if not db_funcs.table_exists('teacher'):
        db_teacher.create_teacher_table()

    if not db_funcs.table_exists('lesson'):
        db_lesson.create_lesson_table()

    if not db_funcs.table_exists('student'):
        db_student.create_student_table()

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
                                                             education, group_count, indiv_count, level, start_work)
            session['logged'] = True
            session['role'] = 'teacher'
            session['user_id'] = user_id
            return redirect(url_for('index'))

    return render_template('register_teacher.html')


@app.route('/register_student', methods=['GET', 'POST'])
def register_student():
    if 'logged' in session:
        return redirect(url_for('index'))

    if not db_funcs.table_exists('users'):
        db_funcs.create_user_table()

    if not db_funcs.table_exists('teacher'):
        db_teacher.create_teacher_table()

    if not db_funcs.table_exists('lesson'):
        db_lesson.create_lesson_table()

    if not db_funcs.table_exists('student'):
        db_student.create_student_table()

    if request.method == 'POST':
        name = request.form['name']
        surname = request.form['surname']
        midname = request.form['midname']
        email = request.form['email']
        phone = request.form['phone']
        password = request.form['password']
        lesson_id = None
        grade = 0
        level = request.form['level']
        start_educ = request.form['start_educ']

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
            user_id = db_student.insert_user_and_student(name, surname, midname, email, phone, password, file_path,
                                                         lesson_id, grade, level, start_educ)
        session['logged'] = True
        session['role'] = 'student'
        session['user_id'] = user_id
        return redirect(url_for('index'))

    return render_template('register_student.html')


@app.route('/add_lesson', methods=['GET', 'POST'])
def add_lesson():
    if 'logged' not in session or session['role'] != 'teacher':
        return redirect(url_for('index'))

    if request.method == 'POST':
        teacher_id = session['user_id']
        less_name = request.form['less_name']
        stud_amount = 0
        stud_max = request.form['stud_max']
        level = request.form['level']
        avg_grade = 0
        schedule = request.form['schedule']
        boolean = db_lesson.insert_lesson(teacher_id, less_name, stud_amount, stud_max, level, avg_grade, schedule)
        if not boolean:
            error = "Error during lesson creation."
            return render_template('add_lesson.html', error=error)
        return redirect(url_for('teacher_profile'))

    return render_template('add_lesson.html')


@app.route('/log_in', methods=['GET', 'POST'])
def login():
    if 'logged' in session:
        return redirect(url_for('index'))
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
    if 'logged' not in session:
        return redirect(url_for('index'))
    if request.method == 'POST':
        session.pop('logged', None)  # Видаляємо ідентифікатор користувача з сесії
        session.pop('user', None)
        return redirect(url_for('index'))
    return render_template('sign_out.html')


@app.route('/profiles/teacher')
def teacher_profile():
    if 'logged' not in session or session['role'] != 'teacher':
        return redirect(url_for('index'))
    user_id = session['user_id']
    user_teacher_info = db_teacher.get_teacher_info(user_id)
    return render_template('/profiles/teacher.html', user=user_teacher_info)


@app.route('/profiles/student')
def student_profile():
    if 'logged' not in session or session['role'] != 'student':
        return redirect(url_for('index'))
    user_id = session['user_id']
    user_student_info = db_student.get_student_info(user_id)
    return render_template('/profiles/student.html', user=user_student_info)


@app.route('/teachers')
def show_teachers():
    teachers = db_teacher.get_all_teachers()
    return render_template('teachers.html', teachers=teachers)


@app.route('/students')
def show_students():
    students = db_student.get_all_students()
    enrolled = None
    if 'logged' in session and session['role'] == 'teacher':
        enrolled = db_student.get_students_by_teacher(session['user_id'])
    return render_template('students.html', students=students, enrolled=enrolled)


@app.route('/students/<int:less_id>')
def show_students_lesson(less_id):
    students = db_student.get_students_by_lesson(less_id)
    enrolled = None
    if 'logged' in session and session['role'] == 'teacher':
        enrolled = db_student.get_students_by_teacher(session['user_id'])
    return render_template('students.html', students=students, enrolled=enrolled)


@app.route('/lessons')
def show_lessons():
    lessons = db_lesson.get_all_lessons()
    created = None
    if 'logged' in session and session['role'] == 'teacher':
        created = db_lesson.get_lessons_by_teacher(session['user_id'])
    boolean = False
    if 'logged' in session and session['role'] == 'student':
        boolean = True
    return render_template('lessons.html', lessons=lessons, created=created, boolean=boolean)


@app.route('/lessons/<int:teach_id>')
def show_lessons_teacher(teach_id):
    lessons = db_lesson.get_lessons_by_teacher(teach_id)
    boolean = False
    if 'logged' in session and session['role'] == 'student':
        boolean = True
    return render_template('lessons.html', lessons=lessons, created=lessons, boolean=boolean)


@app.route('/update_teacher_info', methods=['POST'])
def update_teacher_info():
    if 'logged' not in session or session['role'] != 'teacher':
        return redirect(url_for('index'))  # Redirect to index if user not logged in
    user_id = session.get('user_id')  # Assuming you store the user's ID in the session
    name = request.form['name']
    surname = request.form['surname']
    midname = request.form['midname']
    email = request.form['email']
    education = request.form['education']
    level = request.form['level']
    start_work = request.form['start_work']
    phone = request.form['phone']
    photo = request.files['photo']
    photo_filename = None
    if photo:
        print("photo")
        print(photo)
        photo_filename = secure_filename(photo.filename)
        photo.save(os.path.join('static/uploads', photo_filename))

    db_teacher.update_teacher_info(name, surname, midname, email, education, level, start_work, phone, user_id,
                                   photo_filename)
    return redirect(url_for('teacher_profile'))


@app.route('/update_student_info', methods=['POST'])
def update_student_info():
    if 'logged' not in session or session['role'] != 'student':
        return redirect(url_for('index'))  # Redirect to index if user not logged in
    user_id = session.get('user_id')  # Assuming you store the user's ID in the session
    name = request.form['name']
    surname = request.form['surname']
    midname = request.form['midname']
    email = request.form['email']
    level = request.form['level']
    start_educ = request.form['start_educ']
    phone = request.form['phone']
    photo = request.files['photo']
    photo_filename = None
    if photo:
        print("photo")
        print(photo)
        photo_filename = secure_filename(photo.filename)
        photo.save(os.path.join('static/uploads', photo_filename))

    db_student.update_student_info(name, surname, midname, email, level, start_educ, phone, user_id, photo_filename)
    return redirect(url_for('student_profile'))


@app.route('/evaluate/<int:user_id>', methods=['POST'])
def evaluate(user_id):
    if 'logged' not in session or session['role'] != 'teacher':
        return redirect(url_for('index'))  # Redirect to index if user not logged in
    grade = request.form['grade']
    less_id = db_student.evaluate_grade(user_id, grade)
    db_lesson.calculate_avg(less_id)


@app.route('/enroll/<int:less_id>')
def enroll(less_id):
    if 'logged' not in session or session['role'] != 'student':
        return redirect(url_for('index'))
    user_id = session['user_id']
    res = db_student.enroll(user_id, less_id)
    if res != "Success.":
        error = res
        lessons = db_lesson.get_all_lessons()
        return render_template('lessons.html', lessons=lessons, boolean=True, error=error)
    db_lesson.calculate_avg(less_id)
    return redirect(url_for('student_profile'))


@app.route('/retire')
def retire():
    if 'logged' not in session or session['role'] != 'student':
        return redirect(url_for('index'))
    user_id = session['user_id']
    lesson_id = db_student.retire(user_id)
    db_lesson.calculate_avg(lesson_id)
    return redirect(url_for('student_profile'))


@app.route('/remove/<int:less_id>')
def remove(less_id):
    if 'logged' not in session or session['role'] != 'teacher':
        return redirect(url_for('index'))
    user_id = session['user_id']
    db_lesson.remove(user_id, less_id)
    lessons = db_lesson.get_all_lessons()
    created = db_lesson.get_lessons_by_teacher(user_id)
    return render_template('lessons.html', lessons=lessons, created=created, boolean=False)


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
