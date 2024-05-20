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
                    id INT AUTO_INCREMENT PRIMARY KEY,
                    user_id INT,
                    lesson_id INT,
                    grade INT,
                    level VARCHAR(10),
                    start_educ DATE,
                    FOREIGN KEY (user_id) REFERENCES users(id),
                    FOREIGN KEY (lesson_id) REFERENCES lesson(id)
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
            "INSERT INTO student (user_id, lesson_id, grade, level, start_educ) VALUES (%s, %s, %s, %s, %s, %s)",
            (user_id, lesson_id, grade, level, start_educ))
        connection.commit()

    except mysql.connector.Error as error:
        print("Error inserting in the student table:", error)

    finally:
        if connection.is_connected():
            cursor.close()
            connection.close()
            print("MySQL connection is closed.")


def insert_user_and_student(name, surname, midname, email, phone, password, lesson_id, grade, level, start_educ):
    user_id = db_funcs.insert_table(name, surname, midname, email, phone, password)
    if user_id:
        insert_student(user_id, lesson_id, grade, level, start_educ)
        return user_id
    else:
        print("Failed to insert user, student record not created.")


########ОТРИМАТИ ІНФОРМАЦІЮ З БД
def get_student_info(user_id):
    connection = db_funcs.get_db_connection()

    try:
        cursor = connection.cursor(dictionary=True)
        query = """
            SELECT u.*, s.lesson_id, s.grade, s.level, s.start_educ
            FROM users u
            LEFT JOIN student s ON u.id = s.user_id
            WHERE u.id = %s
        """
        cursor.execute(query, (user_id,))
        user_student_info = cursor.fetchone()

        return user_student_info

    except mysql.connector.Error as error:
        print("Error retrieving user and student info:", error)
        return None

    finally:
        if connection.is_connected():
            cursor.close()
            connection.close()
            print("MySQL connection is closed.")