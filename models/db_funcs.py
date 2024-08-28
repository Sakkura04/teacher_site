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
                    photo VARCHAR(255),
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


def insert_table(name, surname, midname, email, phone, password, photo_path):
    connection = get_db_connection()
    user_id = None
    try:
        cursor = connection.cursor()
        cursor.execute(
            "INSERT INTO users (name, surname, midname, email, phone, photo, password) VALUES (%s, %s, %s, %s, %s, %s, %s)",
            (name, surname, midname, email, phone, photo_path, password))
        connection.commit()

        # Отримання user_id вставленого запису
        user_id = cursor.lastrowid
    except mysql.connector.Error as error:
        print("Error inserting in the table:", error)
    finally:
        if connection.is_connected():
            cursor.close()
            connection.close()
            print("MySQL connection is closed.")
    return user_id


# ///////////////////
#to get data from users table
def is_in_table(email, password):
    connection = get_db_connection()
    try:
        cursor = connection.cursor()
        cursor.execute("SELECT * FROM users WHERE email = %s AND password = %s", (email, password))
        user = cursor.fetchone()

        if user:
            user_id = user[0]  # Припускаємо, що user_id є першим полем в таблиці `users`

            # Перевіряємо, чи є запис в таблиці `teacher` для цього користувача
            cursor.execute("SELECT teach_id FROM teacher WHERE user_id = %s", (user_id,))
            teacher = cursor.fetchone()

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


def db_check():
    # Підключення до бази даних
    connection = mysql.connector.connect(
        host="localhost",
        user="root",
        password="root"
    )
    try:
        cursor = connection.cursor()

        # Перевіряємо, чи існує база даних teachSiteDb
        cursor.execute("SHOW DATABASES LIKE 'teachSiteDb'")
        result = cursor.fetchone()

        if not result:
            # Якщо база даних teachSiteDb ще не існує, створюємо її
            cursor.execute("CREATE DATABASE IF NOT EXISTS teachSiteDb DEFAULT CHARACTER SET 'utf8'")
            print("Database 'teachSiteDb' created successfully.")

    except mysql.connector.Error as error:
        print("Error creating database:", error)

    finally:
        if connection.is_connected():
            cursor.close()
            connection.close()
            print("MySQL connection is closed.")