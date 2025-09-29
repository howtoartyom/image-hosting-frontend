import psycopg2
import os
import logging

# Параметры подключения из переменных окружения
DB_CONFIG = {
    'host': os.getenv('DB_HOST', 'localhost'),
    'database': os.getenv('DB_NAME', 'images_db'),
    'user': os.getenv('DB_USER', 'postgres'),
    'password': os.getenv('DB_PASSWORD', 'password'),
    'port': os.getenv('DB_PORT', '5432')
}


def get_connection():
    """Создает подключение к базе данных"""
    try:
        conn = psycopg2.connect(**DB_CONFIG)
        return conn
    except Exception as e:
        # Если подключение не удалось, записываем ошибку в лог
        logging.error(f"Ошибка подключения к базе данных: {e}")
        return None


def test_connection():
    """Проверяет подключение к базе данных"""
    conn = get_connection()
    if conn:
        try:
            cursor = conn.cursor()
            cursor.execute("SELECT version();")
            version = cursor.fetchone()
            logging.info(f"Подключение к PostgreSQL успешно. Версия: {version[0]}")
            cursor.close()
            conn.close()
            return True
        except Exception as e:
            logging.error(f"Ошибка тестирования подключения: {e}")
            return False
    return False


def init_database():
    conn = get_connection()
    if not conn:
        return False

    try:
        cursor = conn.cursor()
        create_table_query = """
        CREATE TABLE IF NOT EXISTS images (
            id SERIAL PRIMARY KEY,
            filename TEXT NOT NULL,          -- Уникальное имя файла на диске (UUID.ext)
            original_name TEXT NOT NULL,     -- Имя файла, которое загрузил пользователь
            size INTEGER NOT NULL,           -- Размер файла в байтах
            upload_time TIMESTAMP DEFAULT CURRENT_TIMESTAMP, -- Время загрузки
            file_type TEXT NOT NULL          -- MIME-тип или расширение
        );
        """

        cursor.execute(create_table_query)
        conn.commit()
        logging.info("Таблица images создана успешно")

        cursor.close()
        conn.close()

        return True

    except Exception as e:
        logging.error(f"Ошибка инициализации базы данных: {e}")
        return False
