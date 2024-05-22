from decimal import Decimal

import mysql.connector
from . import db_funcs


def create_lesson_table():
    connection = db_funcs.get_db_connection()

    try:
        cursor = connection.cursor()

        # Перевіряємо, чи існує таблиця lesson
        cursor.execute("SHOW TABLES LIKE 'lesson'")
        result = cursor.fetchone()

        if not result:
            # Якщо таблиця lesson ще не існує, створюємо її
            cursor.execute("""
                CREATE TABLE lesson (
                    less_id INT AUTO_INCREMENT PRIMARY KEY,
                    teacher_id INT,
                    less_name VARCHAR(255),
                    stud_amount INT,
                    stud_max INT,
                    level VARCHAR(255),
                    avg_grade DECIMAL(5,2),
                    schedule DECIMAL(4,2),
                    days_of_week VARCHAR(255), 
                    FOREIGN KEY (teacher_id) REFERENCES users(id)
                )
            """)
            print("Table 'lesson' created successfully.")
        else:
            # Якщо таблиця вже існує, додаємо нове поле, якщо його ще немає
            cursor.execute("SHOW COLUMNS FROM lesson LIKE 'days_of_week'")
            result = cursor.fetchone()
            if not result:
                cursor.execute("ALTER TABLE lesson ADD days_of_week VARCHAR(255)")
                print("Column 'days_of_week' added to 'lesson' table.")

    except mysql.connector.Error as error:
        print("Error creating or altering table:", error)

    finally:
        if connection.is_connected():
            cursor.close()
            connection.close()
            print("MySQL connection is closed.")




def insert_lesson(user_id, less_name, stud_amount, stud_max, level, avg_grade, schedule, days_of_week):
    connection = db_funcs.get_db_connection()
    try:
        cursor = connection.cursor(dictionary=True)

        # Перевірка конфлікту розкладу по дням тижня та часу
        query = """
            SELECT l.schedule, l.days_of_week
            FROM lesson l
            INNER JOIN teacher t ON l.teacher_id = t.user_id
            WHERE l.teacher_id = %s
        """
        cursor.execute(query, (user_id,))
        lessons = cursor.fetchall()

        for lesson in lessons:
            lesson_days = lesson['days_of_week'].split(',')
            input_days = days_of_week.split(',')
            if any(day in lesson_days for day in input_days) and lesson['schedule'] == Decimal(schedule):
                return False

        # Оновлення кількості індивідуальних або групових занять
        if int(stud_max) == 1:
            query = """
                UPDATE teacher
                SET indiv_count = indiv_count + 1
                WHERE user_id = %s
            """
            cursor.execute(query, (user_id,))
        elif int(stud_max) > 1:
            query = """
                UPDATE teacher
                SET group_count = group_count + 1
                WHERE user_id = %s
            """
            cursor.execute(query, (user_id,))
        else:
            cursor.close()
            connection.close()
            return False

        connection.commit()

        # Вставка нового уроку
        cursor.execute(
            "INSERT INTO lesson (teacher_id, less_name, stud_amount, stud_max, level, avg_grade, schedule, days_of_week) VALUES (%s, %s, %s, %s, %s, %s, %s, %s)",
            (user_id, less_name, stud_amount, stud_max, level, avg_grade, schedule, days_of_week)
        )
        connection.commit()
        cursor.close()
        connection.close()
        return True
    except mysql.connector.Error as error:
        print("Error inserting in the lesson table:", error)
    except Exception as e:
        print("Unexpected error:", e)
    finally:
        if connection.is_connected():
            cursor.close()
            connection.close()
            return False



def get_all_lessons():
    connection = db_funcs.get_db_connection()
    lessons = []
    try:
        cursor = connection.cursor(dictionary=True)
        query = """
            SELECT l.less_id, l.teacher_id, l.less_name, l.stud_amount, l.stud_max, l.level, l.avg_grade, l.schedule, l.days_of_week, u.name, u.midname, u.surname, u.id
            FROM lesson l
            INNER JOIN users u ON l.teacher_id = u.id
            INNER JOIN teacher t ON u.id = t.user_id
         """
        cursor.execute(query)
        lessons = cursor.fetchall()
        print(f"Fetched {len(lessons)} lessons.")
        print(lessons)
    except mysql.connector.Error as error:
        print("Error fetching lessons:", error)
    finally:
        if connection.is_connected():
            cursor.close()
            connection.close()
            print("MySQL connection is closed.")
    return lessons





def get_lessons_by_teacher(user_id):
    connection = db_funcs.get_db_connection()
    lessons = []
    try:
        cursor = connection.cursor(dictionary=True)
        query = """
            SELECT l.less_id, l.teacher_id, l.less_name, l.stud_amount, l.stud_max, l.level, l.avg_grade, l.schedule, l.days_of_week, u.name, u.midname, u.surname, u.id
            FROM lesson l
            INNER JOIN teacher t ON l.teacher_id = t.user_id
            INNER JOIN users u ON t.user_id = u.id
            WHERE l.teacher_id = %s
         """
        cursor.execute(query, (user_id,))
        lessons = cursor.fetchall()
    except mysql.connector.Error as error:
        print("Error fetching lessons:", error)
    finally:
        if connection.is_connected():
            cursor.close()
            connection.close()
            print("MySQL connection is closed.")
    return lessons


def calculate_avg(less_id):
    connection = db_funcs.get_db_connection()
    try:
        cursor = connection.cursor()
        query = """
            SELECT AVG(s.grade)
            FROM lesson l
            INNER JOIN student s ON l.less_id = s.lesson_id
            WHERE l.less_id = %s
            GROUP BY l.less_id
        """
        cursor.execute(query, (less_id,))
        temp = cursor.fetchone()
        if temp is not None:
            avg = cursor.fetchone()[0]
        else:
            avg = 0
        print(avg)# Отримання першого елемента кортежу
        query = """
            UPDATE lesson
            SET avg_grade = %s
            WHERE less_id = %s
        """
        cursor.execute(query, (avg, less_id))
        connection.commit()
    except mysql.connector.Error as error:
        print("Error calculating average lesson grade:", error)
    finally:
        if connection.is_connected():
            cursor.close()
            connection.close()
            print("MySQL connection is closed.")




def remove_lesson(lesson_id):
    connection = db_funcs.get_db_connection()
    try:
        cursor = connection.cursor()
        # Отримуємо інформацію про урок для оновлення кількості занять вчителя
        cursor.execute("SELECT teacher_id, stud_max, stud_amount FROM lesson WHERE less_id = %s", (lesson_id,))
        lesson_info = cursor.fetchone()

        if not lesson_info:
            print("Lesson not found.")
            return False

        teacher_id = lesson_info[0]
        stud_max = lesson_info[1]
        stud_amount = lesson_info[2]

        # Оновлення кількості занять вчителя
        if stud_max == 1:
            cursor.execute("UPDATE teacher SET indiv_count = indiv_count - 1 WHERE user_id = %s", (teacher_id,))
        else:
            cursor.execute("UPDATE teacher SET group_count = group_count - 1 WHERE user_id = %s", (teacher_id,))

        # Видалення уроку
        cursor.execute("DELETE FROM lesson WHERE less_id = %s", (lesson_id,))
        connection.commit()
        cursor.close()
        connection.close()
        return True
    except mysql.connector.Error as error:
        print("Error removing lesson:", error)
        return False