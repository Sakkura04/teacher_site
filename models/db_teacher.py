import mysql.connector
from . import db_funcs


def create_teacher_table():
    connection = db_funcs.get_db_connection()

    try:
        cursor = connection.cursor()

        # Перевіряємо, чи існує таблиця teacher
        cursor.execute("SHOW TABLES LIKE 'teacher'")
        result = cursor.fetchone()

        if not result:
            # Якщо таблиця teacher ще не існує, створюємо її
            cursor.execute("""
                CREATE TABLE teacher (
                    teach_id INT AUTO_INCREMENT PRIMARY KEY,
                    user_id INT,
                    education VARCHAR(255),
                    group_count INT,
                    indiv_count INT,
                    level VARCHAR(255),
                    start_work DATE,
                    FOREIGN KEY (user_id) REFERENCES users(id)
                )
            """)
            print("Table 'teacher' created successfully.")
        else:
            print("Table 'teacher' already exists.")

    except mysql.connector.Error as error:
        print("Error creating table:", error)

    finally:
        if connection.is_connected():
            cursor.close()
            connection.close()
            print("MySQL connection is closed.")


def insert_teacher(user_id, education, group_count, indiv_count, level, start_work):
    connection = db_funcs.get_db_connection()

    try:
        cursor = connection.cursor()
        cursor.execute(
            "INSERT INTO teacher (user_id, education, group_count, indiv_count, level, start_work) VALUES (%s, %s, %s, %s, %s, %s)",
            (user_id, education, group_count, indiv_count, level, start_work))
        connection.commit()

    except mysql.connector.Error as error:
        print("Error inserting in the teacher table:", error)

    finally:
        if connection.is_connected():
            cursor.close()
            connection.close()
            print("MySQL connection is closed.")


def insert_user_and_teacher(name, surname, midname, email, phone, password, photo, education, group_count, indiv_count,
                            level, start_work):
    user_id = db_funcs.insert_table(name, surname, midname, email, phone, password, photo)
    if user_id:
        insert_teacher(user_id, education, group_count, indiv_count, level, start_work)
        return user_id
    else:
        print("Failed to insert user, teacher record not created.")


########ОТРИМАТИ ІНФОРМАЦІЮ З БД
def get_teacher_info(user_id):
    connection = db_funcs.get_db_connection()
    user_teacher_info = None
    try:
        cursor = connection.cursor(dictionary=True)
        query = """
            SELECT u.*, t.teach_id, t.education, t.group_count, t.indiv_count, t.level, t.start_work
            FROM users u
            LEFT JOIN teacher t ON u.id = t.user_id
            WHERE u.id = %s
        """
        cursor.execute(query, (user_id,))
        user_teacher_info = cursor.fetchone()
    except mysql.connector.Error as error:
        print("Error retrieving user and teacher info:", error)
        return None
    finally:
        if connection.is_connected():
            cursor.close()
            connection.close()
            print("MySQL connection is closed.")
    return user_teacher_info


########      ALL THE TEACHERS
def get_all_teachers():
    connection = db_funcs.get_db_connection()
    teachers = []
    try:
        cursor = connection.cursor(dictionary=True)
        query = """
            SELECT u.id, u.name, u.surname, u.photo, t.education, t.level
            FROM users u
            INNER JOIN teacher t ON u.id = t.user_id
         """
        cursor.execute(query)
        teachers = cursor.fetchall()
    except mysql.connector.Error as error:
        print("Error fetching teachers:", error)
    finally:
        if connection.is_connected():
            cursor.close()
            connection.close()
            print("MySQL connection is closed.")
    return teachers


def update_teacher_info(name, surname, midname, email, education, level, start_work, phone, user_id, photo_filename):
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
        connection.commit()
        query = """
            UPDATE teacher
            SET education = %s, level = %s, start_work = %s
            WHERE user_id = %s
        """
        cursor.execute(query, (education, level, start_work, user_id))
        connection.commit()
    except mysql.connector.Error as error:
        print("Error updating teacher information:", error)
    finally:
        if connection.is_connected():
            cursor.close()
            connection.close()
            print("MySQL connection is closed.")


def get_schedule():
    connection = db_funcs.get_db_connection()
    schedule = []
    try:
        cursor = connection.cursor(dictionary=True)
        query = """
            SELECT l.less_id, l.less_name, l.schedule, t.name AS teacher_name, l.days_of_week
            FROM lesson l
            INNER JOIN teacher te ON l.teacher_id = te.teach_id
            INNER JOIN users t ON te.user_id = t.id
        """
        cursor.execute(query)
        schedule = cursor.fetchall()
    except mysql.connector.Error as error:
        print("Error fetching schedule:", error)
    finally:
        if connection.is_connected():
            cursor.close()
            connection.close()
            print("MySQL connection is closed.")
    return schedule
