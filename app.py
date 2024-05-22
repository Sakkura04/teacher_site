import os
from flask import Flask, render_template, url_for, redirect, session
from fileinput import filename
from werkzeug.utils import secure_filename
from models import db_teacher, db_student, db_funcs, db_lesson, db_articles
from keyy import secret_key
from flask_login import UserMixin
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
        if user_id:
            session['logged'] = True
            session['role'] = 'teacher'
            session['user_id'] = user_id
            return redirect(url_for('index'))
        else:
            return render_template('register_teacher.html', error="Користувач з такими даними вже був введений.")

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
        file_path = ''
        if 'file' in request.files:
            file = request.files['file']
            # if file.filename == '':
            #     return "No selected photo"
            if file and allowed_file(file.filename):
                filename = secure_filename(file.filename)
                file_path = filename
                file_path_save = os.path.join(app.config['UPLOAD_FOLDER'], filename)
                file.save(file_path_save)
                file.save(file_path)

        user_id = db_student.insert_user_and_student(name, surname, midname, email, phone, password, file_path,
                                                         lesson_id, grade, level, start_educ)
        if user_id:
            session['logged'] = True
            session['role'] = 'teacher'
            session['user_id'] = user_id
            return redirect(url_for('index'))
        else:
            return render_template('register_student.html', error="Користувач з такими даними вже був введений.")

    return render_template('register_student.html')

@app.route('/add_lesson', methods=['GET', 'POST'])
def add_lesson():
    db_lesson.create_lesson_table()
    if 'logged' not in session:
        return redirect(url_for('index'))
    else:
        if session['role'] != 'teacher':
            return redirect(url_for('index'))

    if request.method == 'POST':
        teacher_id = session['user_id']
        less_name = request.form['less_name']
        stud_amount = 0
        stud_max = request.form['stud_max']
        level = request.form['level']
        avg_grade = 0
        schedule = request.form['schedule']
        days_of_week = request.form.getlist('days_of_week')  # Отримуємо список днів тижня
        days_of_week_str = ",".join(days_of_week)  # Перетворюємо список у строку

        success = db_lesson.insert_lesson(teacher_id, less_name, stud_amount, stud_max, level, avg_grade, schedule, days_of_week_str)
        if not success:
            error = "Error during lesson creation. There might be a schedule conflict."
            return render_template('add_lesson.html', error=error)
        return redirect(url_for('teacher_profile'))

    return render_template('add_lesson.html')


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
    if 'logged' not in session:
        return redirect(url_for('index'))
    if request.method == 'POST':
        session.pop('logged', None)  # Видаляємо ідентифікатор користувача з сесії
        session.pop('user', None)
        return redirect(url_for('index'))
    return render_template('sign_out.html')


@app.route('/profiles/teacher')
def teacher_profile():
    if 'logged' not in session:
        return redirect(url_for('index'))
    else:
        if session['role'] != 'teacher':
            return redirect(url_for('index'))
    user_id = session['user_id']
    user_teacher_info = db_teacher.get_teacher_info(user_id)
    return render_template('/profiles/teacher.html', user=user_teacher_info)


@app.route('/profiles/student')
def student_profile():
    if 'logged' not in session:
        return redirect(url_for('index'))
    else:
        if session['role'] != 'student':
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
    if 'logged' in session:
        if session['role'] == 'teacher':
            enrolled = db_student.get_students_by_teacher(session['user_id'])
            print(enrolled)
    return render_template('students.html', students=students, enrolled=enrolled, session=session)


@app.route('/students/<int:less_id>')
def show_students_lesson(less_id):
    students = db_student.get_students_by_lesson(less_id)
    enrolled = None
    if 'logged' in session:
        if session['role'] == 'teacher':
            enrolled = db_student.get_students_by_teacher(session['user_id'])
            print(enrolled)
    return render_template('students.html', students=students, enrolled=enrolled, session=session)


@app.route('/lessons')
def show_lessons():
    sort = request.args.get('sort')
    level = request.args.get('level')

    lessons = db_lesson.get_all_lessons()

    created = None
    boolean = False
    personal_list = False
    if 'logged' in session:
        if session['role'] == 'teacher':
            created = db_lesson.get_lessons_by_teacher(session['user_id'])

    if 'logged' in session:
        if session['role'] == 'student':
            boolean = True

    if level:
        lessons = [lesson for lesson in lessons if lesson['level'] == level]
        if created:
            created = [create for create in created if create['level'] == level]

    if sort == 'places':
        lessons.sort(key=lambda x: x['stud_max'] - x['stud_amount'], reverse=True)
        if created:
            created.sort(key=lambda x: x['stud_max'] - x['stud_amount'], reverse=True)
    elif sort == 'schedule':
        lessons.sort(key=lambda x: x['schedule'])
        if created:
            created.sort(key=lambda x: x['schedule'])

    return render_template('lessons.html', lessons=lessons, created=created, boolean=boolean, personal_list=personal_list, session=session)


@app.route('/lessons/<int:teach_id>')
def show_lessons_teacher(teach_id):
    sort = request.args.get('sort')
    level = request.args.get('level')

    lessons = db_lesson.get_lessons_by_teacher(teach_id)

    created = None
    boolean = False
    personal_list = True
    if 'logged' in session:
        if session['role'] == 'student':
            boolean = True
        if session['role'] == 'teacher':
            created = created = db_lesson.get_lessons_by_teacher(session['user_id'])

    if level:
        lessons = [lesson for lesson in lessons if lesson['level'] == level]
        if created:
            created = [create for create in created if create['level'] == level]

    if sort == 'places':
        lessons.sort(key=lambda x: x['stud_max'] - x['stud_amount'], reverse=True)
        if created:
            created.sort(key=lambda x: x['stud_max'] - x['stud_amount'], reverse=True)
    elif sort == 'schedule':
        lessons.sort(key=lambda x: x['schedule'])
        if created:
            created.sort(key=lambda x: x['schedule'])

    return render_template('lessons.html', lessons=lessons, created=created, boolean=boolean, personal_list=personal_list, session=session)




@app.route('/remove/<int:lesson_id>', methods=['POST'])
def remove_lesson_route(lesson_id):
    if 'logged' not in session:
        return redirect(url_for('index'))
    else:
        if session['role'] != 'teacher':
            return redirect(url_for('index'))

    success = db_lesson.remove_lesson(lesson_id)
    if not success:
        error = "Error during lesson removal."
        return render_template('lessons.html', error=error)

    # Після успішного видалення перенаправлення на сторінку вчителя
    return redirect(url_for('teacher_profile'))


@app.route('/update_teacher_info', methods=['POST'])
def update_teacher_info():
    if 'logged' not in session:
        return redirect(url_for('index'))
    else:
        if session['role'] != 'teacher':
            return redirect(url_for('index'))
    user_id = session.get('user_id')
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
    if 'logged' not in session:
        return redirect(url_for('index'))
    else:
        if session['role'] != 'student':
            return redirect(url_for('index'))
    user_id = session.get('user_id')
    stats = db_student.get_student_info(user_id)
    name = request.form['name']
    surname = request.form['surname']
    midname = request.form['midname']
    email = request.form['email']
    print(stats)
    level = stats["level"]
    if not stats["less_id"]:
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
    if 'logged' not in session:
        return redirect(url_for('index'))
    else:
        if session['role'] != 'teacher':
            return redirect(url_for('index'))
    grade = request.form['grade']
    less_id = db_student.evaluate_grade(user_id, grade)
    print(less_id)
    print(type(less_id))
    db_lesson.calculate_avg(less_id)
    return redirect(url_for('show_students_lesson', less_id=less_id))


@app.route('/enroll/<int:less_id>', methods=['GET', 'POST'])
def enroll(less_id):
    if 'logged' not in session:
        return redirect(url_for('index'))
    else:
        if session['role'] != 'student':
            return redirect(url_for('index'))
    user_id = session['user_id']
    res = db_student.enroll(user_id, less_id)
    if res != "Success.":
        error = res
        lessons = db_lesson.get_all_lessons()
        return render_template('lessons.html', lessons=lessons, boolean=True, error=error)
    print(less_id)
    print(type(less_id))
    db_lesson.calculate_avg(less_id)
    return redirect(url_for('student_profile'))



@app.route('/retire')
def retire():
    if 'logged' not in session:
        return redirect(url_for('index'))
    else:
        if session['role'] != 'student':
            return redirect(url_for('index'))
    user_id = session['user_id']
    lesson_id = db_student.retire(user_id)
    if lesson_id != -1:
        db_lesson.calculate_avg(lesson_id)
    return redirect(url_for('student_profile'))


from flask import request

@app.route('/articles', methods=['GET', 'POST'])
def articles():
    if not db_funcs.table_exists('articles'):
        db_articles.create_articles_table()
        db_articles.create_likes_table()

    if request.method == 'POST':
        if 'logged' in session:
            if session['role'] == 'teacher':
                title = request.form['title']
                level = request.form['level']
                content = request.form['content']
                teacher_id = session['user_id']
                db_articles.add_article(title, level, content, teacher_id)
                return redirect(url_for('articles'))  # Перенаправлення на сторінку зі статтями після успішного додавання

    articles = db_articles.get_all_articles()
    return render_template('articles.html', articles=articles)



@app.route('/like_article/<int:article_id>', methods=['POST'])
def like_article_route(article_id):
    if 'logged' in session:
        db_articles.create_likes_table()
        user_id = session['user_id']
        db_articles.like_article(article_id, user_id)
    return redirect(url_for('articles'))


@app.route('/delete_article/<int:article_id>', methods=['POST'])
def delete_article_route(article_id):
    if 'logged' in session:
        if session['role'] == 'teacher':
            teacher_id = session['user_id']
            db_articles.delete_article(article_id, teacher_id)
    return redirect(url_for('articles'))


@app.route('/update_article/<int:article_id>', methods=['GET', 'POST'])
def update_article_route(article_id):
    if request.method == 'GET':
        # Відображення форми оновлення статті з наявними даними
        article = db_articles.get_article_by_id(article_id)
        return render_template('update_article.html', article=article)
    elif request.method == 'POST':
        # Оновлення статті за допомогою даних з форми
        title = request.form['title']
        level = request.form['level']
        content = request.form['content']
        db_articles.update_article(article_id, title, level, content)
        return redirect(url_for('articles'))


@app.route('/filtered_articles', methods=['POST'])
def filtered_articles():
    selected_levels = []
    for level in ['A0', 'A1', 'A1+', 'A2', 'A2+', 'B1', 'B1+', 'B2', 'C1', 'C2', 'Всі']:
        if request.form.get('Всі'):
            articles = db_articles.get_all_articles()
            return render_template('articles.html', articles=articles)

        elif request.form.get(f'level_{level.lower()}'):
            selected_levels.append(level)

    filtered_articles = db_articles.get_articles_by_level(selected_levels)
    return render_template('articles.html', articles=filtered_articles)


@app.route('/schedule/<int:user_id>')
def schedule(user_id):
    # Отримання розкладу з бази даних
    schedule = db_teacher.get_schedule(user_id)
    days = []
    # Групування розкладу по днях
    grouped_schedule = {}
    for lesson in schedule:
        days = lesson['days_of_week'].split(",")
        for day in days:
            if day not in grouped_schedule:
                grouped_schedule[day] = []
            grouped_schedule[day].append(lesson)

    # Сортування розкладу в кожному дні за часом
    for day in grouped_schedule:
        grouped_schedule[day] = sorted(grouped_schedule[day], key=lambda x: x['schedule'])

    print(grouped_schedule.keys())
    return render_template('schedule.html', grouped_schedule=grouped_schedule, days=grouped_schedule.keys())


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
