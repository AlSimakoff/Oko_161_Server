from flask import Flask, request, jsonify
import sqlite3

import settings

app = Flask(__name__)


def create_connection(db_file):
    """Создает соединение с базой данных SQLite."""
    conn = sqlite3.connect(db_file)
    return conn


@app.route('/journalblog', methods=['POST'])
def add_entry_blog():
    """Добавляет новой записи в базу данных."""
    data = request.get_json()  # Получаем данные из запроса
    time = data.get('time')
    color = data.get('color')
    license_number = data.get('license_number')
    type_auto = data.get('type_auto')

    if not time or not color or not license_number or not type_auto:
        return jsonify({"error": "one of fields are required"}), 400

    with create_connection(settings.database_path) as conn:
        cursor = conn.cursor()
        cursor.execute("INSERT INTO JournalBLog (time, color, license_number, type_auto) VALUES (?, ?, ?, ?)", (time, color, license_number, type_auto))
        conn.commit()

    return jsonify({"message": "Entry added successfully"}), 201


@app.route('/journalblog', methods=['GET'])
def get_blog():
    """Возвращает список записей из базы данных."""
    with create_connection(settings.database_path) as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM JournalBLog")
        results = cursor.fetchall()
        return jsonify(results)  # Возвращаем данные в формате JSON

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

if __name__ == "__main__":

    initiate_db()
    app.run(host=settings.host, port=settings.port)