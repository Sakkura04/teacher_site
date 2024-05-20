import mysql.connector
from flask import session

def get_db_connection():
    return mysql.connector.connect(
        host="localhost",
        user="root",
        password="Vladasql2004",
        database="teachSiteDb"
    )

def create_user_table():
    connection = get_db_connection()
    try:
        cursor = connection.cursor()

        # Перевіряємо, чи існує таблиця users
        cursor.execute("SHOW TABLES LIKE 'users'")
        result = cursor.fetchone()

        if not result:
            # Якщо таблиця users ще не існує, створюємо її
            cursor.execute("""
                CREATE TABLE users (
                    id INT AUTO_INCREMENT PRIMARY KEY,
                    name VARCHAR(255),
                    surname VARCHAR(255),
                    midname VARCHAR(255),
                    email VARCHAR(255),
                    phone VARCHAR(255),
                    password VARCHAR(255)
                )
            """)
            print("Table 'users' created successfully.")
        else:
            print("Table 'users' already exists.")

    except mysql.connector.Error as error:
        print("Error creating table:", error)

    finally:
        if connection.is_connected():
            cursor.close()
            connection.close()
            print("MySQL connection is closed.")


def table_exists(table_name):
    # Підключення до бази даних
    connection = get_db_connection()

    try:
        cursor = connection.cursor()

        # Виконання запиту для перевірки існування таблиці
        cursor.execute("SHOW TABLES LIKE %s", (table_name,))

        # Перевірка результату запиту
        result = cursor.fetchone()

        # Закриття курсора та з'єднання
        cursor.close()
        connection.close()

        # Повернення True, якщо таблиця існує, і False - якщо ні
        return bool(result)
        print("Помилка: {}".format(error))
    except mysql.connector.Error as error:
        print("Помилка: {}".format(error))
        return False


# ///////////////////
#to put users data in a users table
# def insert_table(name, surname, midname, email, phone, password):
#     connection = get_db_connection()
#
#     try:
#         cursor = connection.cursor()
#         cursor.execute(
#             "INSERT INTO users (name, surname, midname, email, phone, password) VALUES (%s, %s, %s, %s, %s, %s)",
#             (name, surname, midname, email, phone, password))
#         connection.commit()
#     except mysql.connector.Error as error:
#         print("Error inserting in the table:", error)
#
#     finally:
#         if connection.is_connected():
#             cursor.close()
#             connection.close()
#             print("MySQL connection is closed.")

def insert_table(name, surname, midname, email, phone, password):
    connection = get_db_connection()
    user_id = None
    print("120")
    try:
        cursor = connection.cursor()
        cursor.execute(
            "INSERT INTO users (name, surname, midname, email, phone, password) VALUES (%s, %s, %s, %s, %s, %s)",
            (name, surname, midname, email, phone, password))
        connection.commit()

        # Отримання user_id вставленого запису
        user_id = cursor.lastrowid
        return user_id
    except mysql.connector.Error as error:
        print("Error inserting in the table:", error)
    finally:
        if connection.is_connected():
            cursor.close()
            connection.close()
            print("MySQL connection is closed.")






# ///////////////////
#to get data from users table
def get_from_table(email, password):
    connection = mysql.connector.connect(
        host="localhost",
        user="root",
        password="Vladasql2004",
        database="teachSiteDb"
    )
    try:
        cursor = connection.cursor()
        cursor.execute("SELECT * FROM users WHERE email = %s AND password = %s", (email, password))
        user = cursor.fetchone()

        if user:
            user_id = user[0]  # Припускаємо, що user_id є першим полем в таблиці `users`
            print(user_id, type(str(user_id)))

            # Перевіряємо, чи є запис в таблиці `teacher` для цього користувача
            cursor.execute("SELECT id FROM teacher WHERE user_id = %s", (user_id,))
            teacher = cursor.fetchone()
            print(teacher)

            # Якщо є запис у таблиці `teacher`, встановлюємо роль як 'teacher'
            if teacher:
                role = 'teacher'
            else:
                role = 'student'

            # Закриваємо курсор і з'єднання
            cursor.close()
            connection.close()

            return {'logged_in': True, 'user_id': user_id, 'role': role}

        # Якщо користувача не знайдено, повертаємо відповідний результат
        cursor.close()
        connection.close()
        return {'logged_in': False}

    except mysql.connector.Error as error:
        print("Error querying the database:", error)
        return {'logged_in': False}

    finally:
        if connection.is_connected():
            cursor.close()
            connection.close()
            print("MySQL connection is closed.")


