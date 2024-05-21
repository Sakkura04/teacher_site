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
                    FOREIGN KEY (teacher_id) REFERENCES teacher(teach_id)
                )
            """)
            print("Table 'lesson' created successfully.")
        else:
            print("Table 'lesson' already exists.")

    except mysql.connector.Error as error:
        print("Error creating table:", error)

    finally:
        if connection.is_connected():
            cursor.close()
            connection.close()
            print("MySQL connection is closed.")


def insert_lesson(teacher_id, less_name, stud_amount, stud_max, level, avg_grade, schedule):
    connection = db_funcs.get_db_connection()
    try:
        cursor = connection.cursor()
        query = """
            SELECT l.schedule
            FROM lesson l
            INNER JOIN teacher t ON l.teacher_id = t.teach_id
            WHERE l.teacher_id = %s
        """
        cursor.execute(query, (teacher_id,))
        times = cursor.fetchall()
        for hour in times:
            if hour.schedule == schedule:
                return False
        if stud_max == 1:
            query = """
                UPDATE teacher
                SET indiv_count = indiv_count + 1,
                WHERE teach_id = %s
            """
            cursor.execute(query, (teacher_id,))
        elif stud_max > 1:
            query = """
                UPDATE teacher
                SET group_count = group_count + 1,
                WHERE teach_id = %s
            """
            cursor.execute(query, (teacher_id,))
        else:
            cursor.close()
            connection.close()
            print("MySQL connection is closed.")
            return False
        connection.commit()
        cursor.execute(
            "INSERT INTO lesson (teacher_id, less_name, stud_amount, stud_max, level, avg_grade, schedule) VALUES (%s, %s, %s, %s, %s, %s, %s)",
            (teacher_id, less_name, stud_amount, stud_max, level, avg_grade, schedule))
        connection.commit()
        cursor.close()
        connection.close()
        return True
    except mysql.connector.Error as error:
        print("Error inserting in the lesson table:", error)
    finally:
        if connection.is_connected():
            cursor.close()
            connection.close()
            print("MySQL connection is closed.")
            return False


def get_all_lessons():
    connection = db_funcs.get_db_connection()
    lessons = []
    try:
        cursor = connection.cursor(dictionary=True)
        query = """
            SELECT l.less_id, l.less_name, l.stud_amount, l.stud_max, l.level, l.avg_grade, l.schedule, u.name, u.midname, u.surname, u.id
            FROM lesson l
            INNER JOIN teacher t ON l.teacher_id = t.teach_id
            INNER JOIN users u ON t.user_id = u.id
         """
        cursor.execute(query)
        lessons = cursor.fetchall()
    except mysql.connector.Error as error:
        print("Error fetching lessons:", error)
    finally:
        if connection.is_connected():
            cursor.close()
            connection.close()
            print("MySQL connection is closed.")
    return lessons


def get_lessons_by_teacher(teach_id):
    connection = db_funcs.get_db_connection()
    lessons = []
    try:
        cursor = connection.cursor(dictionary=True)
        query = """
            SELECT l.less_id, l.less_name, l.stud_amount, l.stud_max, l.level, l.avg_grade, l.schedule, u.name, u.midname, u.surname, u.id
            FROM lesson l
            INNER JOIN teacher t ON l.teacher_id = t.teach_id
            INNER JOIN users u ON t.user_id = u.id
            WHERE l.teacher_id = %s
         """
        cursor.execute(query, (teach_id,))
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
        avg = cursor.fetchone()
        query = """
            UPDATE lesson
            SET avg_grade = %s,
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

def remove(user_id, less_id):
    connection = db_funcs.get_db_connection()
    try:
        cursor = connection.cursor()
        query = """
            SELECT stud_max
            FROM lesson
            WHERE less_id = %s
        """
        cursor.execute(query, (less_id,))
        stud_max = cursor.fetchone()
        if (stud_max == 1):
            query = """
                UPDATE teacher
                SET indiv_count = indiv_count - 1,
                WHERE user_id = %s
            """
            cursor.execute(query, (user_id,))
        else:
            query = """
                UPDATE teacher
                SET group_count = group_count - 1,
                WHERE user_id = %s
            """
            cursor.execute(query, (user_id,))
        connection.commit()
        query = """
            UPDATE student
            SET lesson_id = Nono, grade = 0
            WHERE lesson_id = %s
        """
        cursor.execute(query, (less_id,))
        query = """
            DELETE FROM lesson
            WHERE lesson_id = %s
        """
        cursor.execute(query, (less_id,))
        connection.commit()
    except mysql.connector.Error as error:
        print("Error calculating average lesson grade:", error)
    finally:
        if connection.is_connected():
            cursor.close()
            connection.close()
            print("MySQL connection is closed.")
