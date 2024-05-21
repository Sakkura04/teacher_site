import mysql.connector
from . import db_funcs


def create_student_table():
    connection = db_funcs.get_db_connection()

    try:
        cursor = connection.cursor()

        # Перевіряємо, чи існує таблиця student
        cursor.execute("SHOW TABLES LIKE 'student'")
        result = cursor.fetchone()

        if not result:
            # Якщо таблиця student ще не існує, створюємо її
            cursor.execute("""
                CREATE TABLE student (
                    stud_id INT AUTO_INCREMENT PRIMARY KEY,
                    user_id INT,
                    lesson_id INT,
                    grade INT,
                    level VARCHAR(255),
                    start_educ DATE,
                    FOREIGN KEY (user_id) REFERENCES users(id),
                    FOREIGN KEY (lesson_id) REFERENCES lesson(less_id)
                )
            """)
            print("Table 'student' created successfully.")
        else:
            print("Table 'student' already exists.")

    except mysql.connector.Error as error:
        print("Error creating table:", error)

    finally:
        if connection.is_connected():
            cursor.close()
            connection.close()
            print("MySQL connection is closed.")


def insert_student(user_id, lesson_id, grade, level, start_educ):
    connection = db_funcs.get_db_connection()

    try:
        cursor = connection.cursor()
        cursor.execute(
            "INSERT INTO student (user_id, lesson_id, grade, level, start_educ) VALUES (%s, %s, %s, %s, %s)",
            (user_id, lesson_id, grade, level, start_educ))
        connection.commit()

    except mysql.connector.Error as error:
        print("Error inserting in the student table:", error)

    finally:
        if connection.is_connected():
            cursor.close()
            connection.close()
            print("MySQL connection is closed.")


def insert_user_and_student(name, surname, midname, email, phone, password, photo, lesson_id, grade, level, start_educ):
    user_id = db_funcs.insert_table(name, surname, midname, email, phone, password, photo)
    if user_id:
        insert_student(user_id, lesson_id, grade, level, start_educ)
        return user_id
    else:
        print("Failed to insert user, student record not created.")


########ОТРИМАТИ ІНФОРМАЦІЮ З БД
def get_student_info(user_id):
    connection = db_funcs.get_db_connection()
    user_student_info = None
    try:
        cursor = connection.cursor(dictionary=True)
        query = """
            SELECT u.*, s.stud_id, s.grade, s.level, s.start_educ, l.less_id, l.less_name
            FROM users u
            INNER JOIN student s ON u.id = s.user_id
            LEFT JOIN lesson l ON s.lesson_id = l.less_id
            WHERE u.id = %s
        """
        cursor.execute(query, (user_id,))
        user_student_info = cursor.fetchone()
    except mysql.connector.Error as error:
        print("Error retrieving user and student info:", error)
        return None
    finally:
        if connection.is_connected():
            cursor.close()
            connection.close()
            print("MySQL connection is closed.")
    return user_student_info


########      ALL THE STUDENTS
def get_all_students():
    connection = db_funcs.get_db_connection()
    students = []
    try:
        cursor = connection.cursor(dictionary=True)
        query = """
            SELECT u.id, u.name, u.surname, u.photo, s.grade, l.less_id, l.less_name
            FROM users u
            INNER JOIN student s ON u.id = s.user_id
            LEFT JOIN lesson l ON s.lesson_id = l.less_id
         """
        cursor.execute(query)
        students = cursor.fetchall()
    except mysql.connector.Error as error:
        print("Error fetching students:", error)
    finally:
        if connection.is_connected():
            cursor.close()
            connection.close()
            print("MySQL connection is closed.")
    return students


def get_students_by_lesson(less_id):
    connection = db_funcs.get_db_connection()
    students = []
    try:
        cursor = connection.cursor(dictionary=True)
        query = """
            SELECT u.id, u.name, u.surname, u.photo, s.grade, l.less_id, l.less_name
            FROM users u
            INNER JOIN student s ON u.id = s.user_id
            INNER JOIN lesson l ON s.lesson_id = l.less_id
            WHERE l.less_id = %s
         """
        cursor.execute(query, (less_id,))
        students = cursor.fetchall()
    except mysql.connector.Error as error:
        print("Error fetching students:", error)
    finally:
        if connection.is_connected():
            cursor.close()
            connection.close()
            print("MySQL connection is closed.")
    return students


def get_students_by_teacher(teach_id):
    connection = db_funcs.get_db_connection()
    students = []
    try:
        cursor = connection.cursor(dictionary=True)
        query = """
            SELECT u.id
            FROM users u
            INNER JOIN student s ON u.id = s.user_id
            INNER JOIN lesson l ON s.lesson_id = l.less_id
            INNER JOIN teacher t ON l.teacher_id = t.teach_id
            WHERE t.teach_id = %s
         """
        cursor.execute(query, (teach_id,))
        students = cursor.fetchall()
    except mysql.connector.Error as error:
        print("Error fetching students:", error)
    finally:
        if connection.is_connected():
            cursor.close()
            connection.close()
            print("MySQL connection is closed.")
    return students


def update_student_info(name, surname, midname, email, level, start_educ, phone, user_id, photo_filename):
    # Update the database
    connection = db_funcs.get_db_connection()
    try:
        cursor = connection.cursor()
        if photo_filename:
            query = """
                UPDATE users
                SET name = %s, surname = %s, midname = %s, email = %s, phone = %s, photo = %s
                WHERE id = %s
            """
            cursor.execute(query, (name, surname, midname, email, phone, photo_filename, user_id))
        else:
            query = """
                UPDATE users
                SET name = %s, surname = %s, midname = %s, email = %s, phone = %s
                WHERE id = %s
            """
            cursor.execute(query, (name, surname, midname, email, phone, user_id))
        query = """
            UPDATE student
            SET level = %s, start_educ = %s
            WHERE user_id = %s
        """
        cursor.execute(query, (level, start_educ, user_id))
        connection.commit()
    except mysql.connector.Error as error:
        print("Error updating student information:", error)
    finally:
        if connection.is_connected():
            cursor.close()
            connection.close()
            print("MySQL connection is closed.")


def evaluate_grade(user_id, grade):
    connection = db_funcs.get_db_connection()
    less_id = 0
    try:
        cursor = connection.cursor()
        query = """
            UPDATE student
            SET grade = %s,
            WHERE user_id = %s
        """
        cursor.execute(query, (grade, user_id))
        connection.commit()
        query = """
            SELECT l.less_id
            FROM users u
            INNER JOIN student s ON u.id = s.user_id
            INNER JOIN lesson l ON s.lesson_id = l.less_id
            WHERE s.user_id = %s
        """
        cursor.execute(query, (user_id,))
        less_id = cursor.fetchone()
    except mysql.connector.Error as error:
        print("Error updating student grade:", error)
    finally:
        if connection.is_connected():
            cursor.close()
            connection.close()
            print("MySQL connection is closed.")
    return less_id


def enroll(user_id, less_id):
    connection = db_funcs.get_db_connection()
    try:
        cursor = connection.cursor()
        query = """
            SELECT lesson_id
            FROM student
            WHERE user_id = %s
        """
        cursor.execute(query, (user_id,))
        ident = cursor.fetchone()
        if ident is not None:
            return "Already enrolled."
        query = """
            SELECT level
            FROM lesson
            WHERE less_id = %s
        """
        cursor.execute(query, (less_id,))
        level_less = cursor.fetchone()
        query = """
            SELECT level
            FROM student
            WHERE user_id = %s
        """
        cursor.execute(query, (user_id,))
        level_stud = cursor.fetchone()
        if level_less != level_stud:
            return "English levels don't match."
        query = """
            SELECT (stud_max - stud_amount)
            FROM lesson
            WHERE less_id = %s
        """
        cursor.execute(query, (less_id,))
        free = cursor.fetchone()
        if free <= 0:
            return "No place left."
        query = """
            UPDATE student
            SET lesson_id = %s
            WHERE user_id = %s
        """
        cursor.execute(query, (less_id, user_id))
        connection.commit()
        query = """
            UPDATE lesson
            SET stud_amount = stud_amount + 1
            WHERE less_id = %s
        """
        cursor.execute(query, (less_id,))
        connection.commit()
    except mysql.connector.Error as error:
        print("Error updating student grade:", error)
    finally:
        if connection.is_connected():
            cursor.close()
            connection.close()
            print("MySQL connection is closed.")
    return "Success."


def retire(user_id):
    connection = db_funcs.get_db_connection()
    lesson_id = None
    try:
        cursor = connection.cursor()
        query = """
            SELECT s.lesson_id
            FROM student s
            WHERE s.user_id = %s
        """
        cursor.execute(query, (user_id,))
        lesson_id = cursor.fetchone()
        if lesson_id is None:
            return
        query = """
            UPDATE student
            SET lesson_id = None, grade = 0
            WHERE user_id = %s
        """
        cursor.execute(query, (user_id,))
        connection.commit()
        query = """
            UPDATE lesson
            SET stud_amount = stud_amount - 1
            WHERE less_id = %s
        """
        cursor.execute(query, (lesson_id,))
        connection.commit()
    except mysql.connector.Error as error:
        print("Error updating student grade:", error)
    finally:
        if connection.is_connected():
            cursor.close()
            connection.close()
            print("MySQL connection is closed.")
    return lesson_id
