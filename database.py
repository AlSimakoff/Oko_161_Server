import sqlite3

import settings

def create_connection(db_file):
    """Создает соединение с базой данных SQLite."""
    conn = sqlite3.connect(db_file)
    return conn

def initiate_db():
    with create_connection(settings.database_path) as conn:
        cursor = conn.cursor()
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS JournalBLog (
            id INTEGER PRIMARY KEY,
            time TEXT NOT NULL,
            color TEXT NOT NULL,
            license_number TEXT NOT NULL,
            type_auto TEXT NOT NULL
            )''')

def select_all(table):
    with create_connection(settings.database_path) as conn:
        cursor = conn.cursor()
        cursor.execute(f"SELECT * FROM {table}")
        results = cursor.fetchall()
        return results

def add_entry(table, values):
    if table=="JournalBLog":
        with create_connection(settings.database_path) as conn:
            cursor = conn.cursor()
            cursor.execute("INSERT INTO JournalBLog (time, color, license_number, type_auto) VALUES (?, ?, ?, ?)",
                           values)
            conn.commit()