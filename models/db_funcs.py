import mysql.connector
from flask import session


def create_table():
    connection = mysql.connector.connect(
        host="localhost",
        user="root",
        password="Vladasql2004",
        database="teachSiteDb"
    )
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
    connection = mysql.connector.connect(
        host="localhost",
        user="root",
        password="Vladasql2004",
        database="teachSiteDb"
     )
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
def insert_table(name, surname, midname, email, phone, password):
    connection = mysql.connector.connect(
        host="localhost",
        user="root",
        password="Vladasql2004",
        database="teachSiteDb"
    )

    try:
        cursor = connection.cursor()
        cursor.execute(
            "INSERT INTO users (name, surname, midname, email, phone, password) VALUES (%s, %s, %s, %s, %s, %s)",
            (name, surname, midname, email, phone, password))
        connection.commit()
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
        cursor.close()
        connection.close()

        # Якщо користувач знайдений, авторизуємо його
        if user:
            session['logged_in'] = True
            return True

        return False

    except mysql.connector.Error as error:
        print("Error inserting in the table:", error)

    finally:
        if connection.is_connected():
            cursor.close()
            connection.close()
            print("MySQL connection is closed.")



