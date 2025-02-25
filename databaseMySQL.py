from mysql.connector import connect, Error

import settings

def create_connection():
    """Создает соединение с базой данных MySQL."""
    try:
        conn = connect(
                host=settings.hostMySQL,
                user=settings.db_user,
                password=settings.db_pass,
                database=settings.database_name
        )
        return conn
    except Error as e:
        print(e)
        return None


def initiate_db():
    with create_connection() as conn:
        cursor = conn.cursor()
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS JournalBLog (
            id INT AUTO_INCREMENT PRIMARY KEY,
            time TEXT NOT NULL,
            color TEXT NOT NULL,
            license_number TEXT NOT NULL,
            type_auto TEXT NOT NULL
            )''')

def check_table(table):
    with create_connection() as conn:
        cursor = conn.cursor()

        cursor.execute(f'''
            CREATE TABLE IF NOT EXISTS {table} (
            id INT AUTO_INCREMENT PRIMARY KEY,
            time TEXT NOT NULL,
            color TEXT NOT NULL,
            license_number TEXT NOT NULL,
            type_auto TEXT NOT NULL
            )''')


def get_allowed_tables():
    """Получает список всех таблиц в базе данных."""
    with create_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("SHOW TABLES;")  # Запрос для получения всех таблиц
        tables = cursor.fetchall()  # Получаем все имена таблиц
        return [table[0] for table in tables]  # Возвращаем только имена таблиц

def select_all(table):
    """Извлекает все записи из указанной таблицы."""
    allowed_tables = get_allowed_tables()
    if table not in allowed_tables:
        raise ValueError(f"Invalid table name: {table}")

    with create_connection() as conn:
        cursor = conn.cursor()
        cursor.execute(f"SELECT * FROM {table}")  # Используйте безопасный способ для имен таблиц
        results = cursor.fetchall()
        return results

def add_entry(table, values):
    """Добавляет запись в указанную таблицу."""
    check_table(table)
    with create_connection() as conn:
        cursor = conn.cursor()
        cursor.execute(f"INSERT INTO {table} (time, color, license_number, type_auto) VALUES (%s, %s, %s, %s)",
                        values)
        conn.commit()