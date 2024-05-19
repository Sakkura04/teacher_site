import mysql.connector
from . import db_funcs


def create_teacher_table():
    connection = mysql.connector.connect(
        host="localhost",
        user="root",
        password="Vladasql2004",
        database="teachSiteDb"
    )
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
    connection = mysql.connector.connect(
        host="localhost",
        user="root",
        password="Vladasql2004",
        database="teachSiteDb"
    )

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
    user_id = db_funcs.insert_table(name, surname, midname, email, phone, password)
    if user_id:
        insert_teacher(user_id, education, group_count, indiv_count, level, start_work)
    else:
        print("Failed to insert user, teacher record not created.")