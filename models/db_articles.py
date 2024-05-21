import mysql.connector
from . import db_funcs


def create_articles_table():
    connection =  db_funcs.get_db_connection()
    try:
        cursor = connection.cursor()

        # Перевіряємо, чи існує таблиця teacher
        cursor.execute("SHOW TABLES LIKE 'articles'")
        result = cursor.fetchone()

        if not result:
            # Якщо таблиця teacher ще не існує, створюємо її
            cursor.execute("""
                CREATE TABLE articles (
                    id INT AUTO_INCREMENT PRIMARY KEY,
                    title VARCHAR(255),
                    level VARCHAR(255),
                    content TEXT,
                    likes INT DEFAULT 0,
                    author_id INT,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
                    FOREIGN KEY (author_id) REFERENCES users(id)
                )
            """)
            print("Table 'articles' created successfully.")
        else:
            print("Table 'articles' already exists.")

    except mysql.connector.Error as error:
        print("Error creating table:", error)

    finally:
        if connection.is_connected():
            cursor.close()
            connection.close()
            print("MySQL connection is closed.")



def create_likes_table():
    connection = db_funcs.get_db_connection()
    try:
        cursor = connection.cursor()

        cursor.execute("SHOW TABLES LIKE 'article_likes'")
        result = cursor.fetchone()

        if not result:
            # Якщо таблиця teacher ще не існує, створюємо її
            cursor.execute("""
                    CREATE TABLE article_likes (
                        id INT AUTO_INCREMENT PRIMARY KEY,
                        article_id INT NOT NULL,
                        user_id INT NOT NULL,
                        FOREIGN KEY (article_id) REFERENCES articles(id),
                        FOREIGN KEY (user_id) REFERENCES users(id),
                        UNIQUE (article_id, user_id)
                    )
                """)
            print("Table 'articles' created successfully.")
        else:
            print("Table 'articles' already exists.")

    except mysql.connector.Error as error:
        print("Error creating table:", error)

    finally:
        if connection.is_connected():
            cursor.close()
            connection.close()
            print("MySQL connection is closed.")



def get_article_by_id(article_id):
    connection = db_funcs.get_db_connection()
    try:
        cursor = connection.cursor(dictionary=True)
        cursor.execute(
            "SELECT * FROM articles WHERE id = %s", (article_id,)
        )
        return cursor.fetchone()
    
    except mysql.connector.Error as error:
        print("Error fetching article:", error)
    finally:
        if connection.is_connected():
            cursor.close()
            connection.close()



def get_articles_by_level(levels):
    connection = db_funcs.get_db_connection()
    try:
        cursor = connection.cursor(dictionary=True)
        query = "SELECT * FROM articles WHERE level IN (%s)"
        # Генеруємо рядок з %s для кожного рівня у списку levels
        placeholders = ', '.join(['%s'] * len(levels))
        query = query % placeholders
        cursor.execute(query, levels)
        articles = cursor.fetchall()
    except mysql.connector.Error as error:
        print("Error fetching article:", error)
    finally:
        if connection.is_connected():
            cursor.close()
            connection.close()
    return articles



def get_all_articles():
    connection = db_funcs.get_db_connection()
    articles = []
    try:
        cursor = connection.cursor(dictionary=True)
        cursor.execute("SELECT a.*, u.name, u.surname FROM articles a JOIN users u ON a.author_id = u.id")
        articles = cursor.fetchall()
    except mysql.connector.Error as error:
        print("Error fetching articles:", error)
    finally:
        if connection.is_connected():
            cursor.close()
            connection.close()
    return articles


def add_article(title, level, content, author_id):
    connection = db_funcs.get_db_connection()
    try:
        cursor = connection.cursor()
        cursor.execute("INSERT INTO articles (title, level, content, author_id) VALUES (%s, %s, %s, %s)",
                       (title, level, content, author_id))
        connection.commit()
    except mysql.connector.Error as error:
        print("Error adding article:", error)
    finally:
        if connection.is_connected():
            cursor.close()
            connection.close()


def like_article(article_id, user_id):
    connection = db_funcs.get_db_connection()
    try:
        cursor = connection.cursor()
        # Check if the user has already liked the article
        cursor.execute("SELECT * FROM article_likes WHERE article_id = %s AND user_id = %s", (article_id, user_id))
        like = cursor.fetchone()

        if like:
            # User has already liked the article, so unlike it
            cursor.execute("DELETE FROM article_likes WHERE article_id = %s AND user_id = %s", (article_id, user_id))
            cursor.execute("UPDATE articles SET likes = likes - 1 WHERE id = %s", (article_id,))
        else:
            # User has not liked the article yet, so like it
            cursor.execute("INSERT INTO article_likes (article_id, user_id) VALUES (%s, %s)", (article_id, user_id))
            cursor.execute("UPDATE articles SET likes = likes + 1 WHERE id = %s", (article_id,))

        connection.commit()
    except mysql.connector.Error as error:
        print("Error liking/unliking article:", error)
    finally:
        if connection.is_connected():
            cursor.close()
            connection.close()


def delete_article(article_id, author_id):
    connection = db_funcs.get_db_connection()
    try:
        cursor = connection.cursor()
        cursor.execute("DELETE FROM articles WHERE id = %s AND author_id = %s", (article_id, author_id))
        connection.commit()
    except mysql.connector.Error as error:
        print("Error deleting article:", error)
    finally:
        if connection.is_connected():
            cursor.close()
            connection.close()


def update_article(article_id, title, level, content):
    connection = db_funcs.get_db_connection()
    try:
        cursor = connection.cursor()
        cursor.execute(
            "UPDATE articles SET title = %s, level = %s, content = %s WHERE id = %s",
            (title, level, content, article_id)
        )
        connection.commit()
    except mysql.connector.Error as error:
        print("Error updating article:", error)
    finally:
        if connection.is_connected():
            cursor.close()
            connection.close()