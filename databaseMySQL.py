from datetime import datetime, timedelta, date
from mysql.connector import connect, Error
from sqlalchemy.cyextension.processors import str_to_time

import settings

def create_connection():
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
            time DATETIME,
            color TEXT,
            license_number TEXT,
            type_auto TEXT,
            img_plate_url VARCHAR(255),
            img_car_url VARCHAR(255)
            )''')


def get_allowed_tables():
    """Получает список всех таблиц в базе данных."""
    return settings.allowed_tables

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
        cursor.execute(f"INSERT INTO {table} (time, color, license_number, type_auto, img_plate_url, img_car_url ) VALUES (%s, %s, %s, %s, %s, %s)",
                        values)
        conn.commit()

def select_by_time_range(table, start_time, end_time):
    """
    Извлекает все записи из указанной таблицы за заданный промежуток времени.
    Аргументы:
    - table: имя таблицы.
    - start_time: начало временного диапазона (datetime).
    - end_time: конец временного диапазона (datetime).
    """
    allowed_tables = get_allowed_tables()
    if table not in allowed_tables:
        raise ValueError(f"Invalid table name: {table}")

    # Преобразуем даты в строковый формат MySQL DATETIME
    start_time_str = start_time.strftime('%Y-%m-%d %H:%M:%S')
    end_time_str = end_time.strftime('%Y-%m-%d %H:%M:%S')
    #start_time_str = start_time
    #end_time_str = end_time

    query = f"""
        SELECT `id`, `time`, `color`, `license_number`, `type_auto`, `img_plate_url`, `img_car_url`
        FROM `{table}`
        WHERE `time` BETWEEN %s AND %s
    """

    with create_connection() as conn:
        cursor = conn.cursor()
        cursor.execute(query, (start_time_str, end_time_str))  # Используем безопасную подстановку значений
        results = cursor.fetchall()
        return results



def select_last_n_days(table, n):
    """Получает все записи за последние N дней."""
    end_time = datetime.now()
    start_time = end_time - timedelta(days=n)
    return select_by_time_range(table, start_time, end_time)

def get_table_name_mappings():
    # Возвращает словарь {table_base: assigment}
    with create_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT table_base, assigment FROM table_names")
        result = cursor.fetchall()
        return {row[0]: row[1] for row in result}

def search_plate_in_table(table, plate_fragment):
    query = f"SELECT * FROM {table} WHERE license_number LIKE %s"
    like_expr = f"%{plate_fragment}%"
    with create_connection() as conn:
        cursor = conn.cursor()
        cursor.execute(query, (like_expr,))
        result = cursor.fetchall()
        return result
