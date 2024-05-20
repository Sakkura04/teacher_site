import mysql.connector
from . import db_funcs


def create_teacher_table():
    connection =  db_funcs.get_db_connection()

    try:
        cursor = connection.cursor()

        # Перевіряємо, чи існує таблиця teacher
        cursor.execute("SHOW TABLES LIKE 'teacher'")
        result = cursor.fetchone()

        if not result:
            # Якщо таблиця teacher ще не існує, створюємо її
            cursor.execute("""
                CREATE TABLE teacher (
                    id INT AUTO_INCREMENT PRIMARY KEY,
                    user_id INT,
                    education VARCHAR(255),
                    group_count INT,
                    indiv_count INT,
                    level INT,
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



def insert_user_and_teacher(name, surname, midname, email, phone, password, education, group_count, indiv_count, level, start_work):
    print("11")
    user_id = db_funcs.insert_table(name, surname, midname, email, phone, password)
    print("a")
    print(user_id)
    if user_id:
        print("b")
        insert_teacher(user_id, education, group_count, indiv_count, level, start_work)
    else:
        print("Failed to insert user, teacher record not created.")




########ОТРИМАТИ ІНФОРМАЦІЮ З БД
def get_teacher_info(user_id):
    connection = db_funcs.get_db_connection()

    try:
        cursor = connection.cursor(dictionary=True)
        query = """
            SELECT u.*, t.education, t.group_count, t.indiv_count, t.level, t.start_work
            FROM users u
            LEFT JOIN teacher t ON u.id = t.user_id
            WHERE u.id = %s
        """
        cursor.execute(query, (user_id,))
        user_teacher_info = cursor.fetchone()

        return user_teacher_info

    except mysql.connector.Error as error:
        print("Error retrieving user and teacher info:", error)
        return None

    finally:
        if connection.is_connected():
            cursor.close()
            connection.close()
            print("MySQL connection is closed.")