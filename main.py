# Импорты необходимых библиотек и модулей
from flask import Flask, request, jsonify, url_for, render_template
from flask_sqlalchemy import SQLAlchemy
from admin_panel import init_admin

import databaseMySQL
import settings
from models import db
import base64
import os
from datetime import datetime, timedelta
from utils import (
    get_today_entry_count,
    get_average_time,
    get_recognition_errors,
    get_monthly_count,
    get_hourly_data,
    get_weekly_data
)

# Создание экземпляра Flask-приложения
app = Flask(__name__, template_folder="templates")

# Путь для сохранения изображений
IMAGE_SAVE_PATH = '/static/uploads'

def create_app():
    """Создаёт и настраивает Flask-приложение."""

    # Конфигурация подключения к базе данных
    app.config[
        'SQLALCHEMY_DATABASE_URI'
    ] = f'mysql+mysqlconnector://{settings.db_user}:{settings.db_pass}@{settings.hostMySQL}/{settings.database_name}'
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

    # Инициализация SQLAlchemy с контекстом приложения
    db.init_app(app)

    # Инициализация административной панели
    init_admin(app)

    return app

@app.route('/')
def dashboard():
    """Главная страница: отображает статистику по выбранной таблице."""
    selected_table = request.args.get('table', 'bolshoilog_img')
    allowed_tables = databaseMySQL.get_allowed_tables()

    if selected_table not in allowed_tables:
        selected_table = allowed_tables[0] if allowed_tables else None

    today = datetime.now().date()

    # Получение статистических данных
    today_count = get_today_entry_count(selected_table)
    avg_minutes = get_average_time(selected_table)
    errors = get_recognition_errors(selected_table)
    monthly = get_monthly_count(selected_table)
    hourly_data = get_hourly_data(selected_table)
    weekly_data = get_weekly_data(selected_table)

    # Отображение данных на dashboard.html
    return render_template(
        'dashboard.html',
        today=today.strftime('%d.%m.%Y'),
        today_count=today_count,
        avg_minutes=avg_minutes,
        errors=errors,
        monthly=monthly,
        hourly_data=hourly_data,
        weekly_data=weekly_data
    )

@app.route('/api/stats/<table_name>')
def get_stats(table_name):
    """API для получения статистики по таблице."""
    if table_name not in databaseMySQL.get_allowed_tables():
        return jsonify({"success": False, "error": "Invalid table name"}), 400

    try:
        # Получение и возврат статистики
        today_count = get_today_entry_count(table_name)
        avg_minutes = get_average_time(table_name)
        errors = get_recognition_errors(table_name)
        monthly = get_monthly_count(table_name)
        hourly = get_hourly_data(table_name)
        weekly = get_weekly_data(table_name)

        return jsonify({
            "success": True,
            "today_count": today_count,
            "avg_minutes": avg_minutes,
            "errors": errors,
            "monthly": monthly,
            "hourly_data": hourly,
            "weekly_data": weekly
        })

    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500

@app.route("/api/data")
def get_table_data():
    """API: получить все строки из таблицы."""
    table = request.args.get("table")
    try:
        rows = databaseMySQL.select_all(table)
        return jsonify({"success": True, "data": rows})
    except Exception as e:
        return jsonify({"success": False, "error": str(e)})

@app.route("/api/tables")
def get_tables():
    """API: получить список разрешённых таблиц."""
    try:
        tables = databaseMySQL.get_allowed_tables()
        return jsonify({"success": True, "tables": tables})
    except Exception as e:
        return jsonify({"success": False, "error": str(e)})

@app.route("/api/data/<table>")
def get_table_data_api(table):
    """API: альтернатива получения данных таблицы."""
    try:
        rows = databaseMySQL.select_all(table)
        return jsonify({"success": True, "data": rows})
    except Exception as e:
        return jsonify({"success": False, "error": str(e)})

@app.route('/oko161', methods=['POST'])
def add_entry():
    """Добавляет новую запись и сохраняет изображения."""
    data = request.get_json()

    # Получение данных из запроса
    time = data.get('time')
    color = data.get('color')
    license_number = data.get('license_number')
    type_auto = data.get('type_auto')
    table_name = data.get('table_name')
    img_plate_b64 = data.get('img_plate')
    img_car_b64 = data.get('img_car')

    if not time:
        return jsonify({"error": "time is missing"}), 400

    # Генерация имён файлов
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    plate_filename = f"{license_number}_{timestamp}_plate.jpg"
    car_filename = f"{license_number}_{timestamp}_car.jpg"
    plate_path = os.path.join(IMAGE_SAVE_PATH, plate_filename)
    car_path = os.path.join(IMAGE_SAVE_PATH, car_filename)

    try:
        # Сохраняем изображения
        if img_plate_b64:
            plate_data = base64.b64decode(img_plate_b64)
            with open(plate_path, 'wb') as f:
                f.write(plate_data)

        if img_car_b64:
            car_data = base64.b64decode(img_car_b64)
            with open(car_path, 'wb') as f:
                f.write(car_data)

        # Сохраняем запись в базу
        databaseMySQL.add_entry(
            table_name,
            (time, color, license_number, type_auto, plate_filename, car_filename)
        )

        return jsonify({"message": "Entry added successfully"}), 201

    except Exception as e:
        return jsonify({"error": f"Ошибка при обработке данных: {str(e)}"}), 500

@app.route('/table/journals')
def show_journals():
    """Отображает список таблиц в виде карточек."""
    allowed_tables = databaseMySQL.get_allowed_tables()
    name_map = databaseMySQL.get_table_name_mappings()

    cards = []
    for table in allowed_tables:
        readable_name = name_map.get(table, table)
        cards.append({'table': table, 'name': readable_name})

    return render_template('journals.html', cards=cards)

@app.route('/oko161', methods=['GET'])
def get_entry():
    """Получает список записей с изображениями."""
    table = request.args.get('table', 'None')
    results = databaseMySQL.select_all(table)

    output = []
    for row in results:
        row_dict = {
            "id": row[0],
            "time": row[1],
            "color": row[2],
            "license_number": row[3],
            "type_auto": row[4],
            "img_plate_url": url_for('static', filename=f"uploads/{row[5]}", _external=True) if row[5] else None,
            "img_car_url": url_for('static', filename=f"uploads/{row[6]}", _external=True) if row[6] else None,
        }
        output.append(row_dict)

    return jsonify(output)

@app.route('/search', methods=['GET', 'POST'])
def search_by_plate():
    """Поиск по номеру автомобиля по всем таблицам."""
    query = request.form.get('plate') if request.method == 'POST' else None
    results = []

    if query:
        allowed_tables = databaseMySQL.get_allowed_tables()
        table_names = databaseMySQL.get_table_name_mappings()

        for table in allowed_tables:
            matches = databaseMySQL.search_plate_in_table(table, query)
            for row in matches:
                try:
                    timestamp = row[1] if isinstance(row[1], datetime) else datetime.strptime(row[1], '%Y-%m-%d %H:%M:%S')
                except:
                    timestamp = datetime.min

                results.append({
                    'time': timestamp,
                    'number': row[3],
                    'table': table,
                    'table_name': table_names.get(table, table),
                    'image_path': row[6]
                })

        # Сортировка по дате (новые — сверху)
        results.sort(key=lambda x: x['time'], reverse=True)

    return render_template('search.html', results=results, query=query or '')

@app.route('/table/<table_name>')
def full_table_view(table_name):
    """Отображает полную таблицу по названию."""
    if table_name not in databaseMySQL.get_allowed_tables():
        return "Таблица не найдена", 404

    data = databaseMySQL.select_all(table_name)
    return render_template("table_view.html", table_name=table_name, data=data)

@app.route('/api/entries/<table_name>')
def get_entries(table_name):
    """Фильтрация записей по номеру и дате."""
    if table_name not in databaseMySQL.get_allowed_tables():
        return jsonify({"success": False, "error": "Invalid table"})

    query = f"SELECT * FROM {table_name} WHERE 1=1"
    filters = []

    license_number = request.args.get("license_number")
    date_from = request.args.get("from")
    date_to = request.args.get("to")

    if license_number:
        query += " AND license_number LIKE %s"
        filters.append(f"%{license_number}%")

    if date_from:
        query += " AND time >= %s"
        filters.append(date_from)
    if date_to:
        query += " AND time <= %s"
        filters.append(date_to)

    with databaseMySQL.create_connection() as conn:
        cursor = conn.cursor()
        cursor.execute(query, filters)
        data = cursor.fetchall()

    return jsonify({"success": True, "data": data})

@app.route('/api/entry/<table_name>/<int:entry_id>', methods=['PUT', 'DELETE'])
def update_or_delete_entry(table_name, entry_id):
    """Обновление или удаление записи по ID."""
    if table_name not in databaseMySQL.get_allowed_tables():
        return jsonify({"success": False, "error": "Invalid table"})

    with databaseMySQL.create_connection() as conn:
        cursor = conn.cursor()
        if request.method == "DELETE":
            cursor.execute(f"DELETE FROM {table_name} WHERE id = %s", (entry_id,))
            conn.commit()
            return jsonify({"success": True, "message": "Deleted"})
        elif request.method == "PUT":
            data = request.json
            cursor.execute(f'''
                UPDATE {table_name}
                SET time=%s, color=%s, license_number=%s, type_auto=%s
                WHERE id = %s
            ''', (data["time"], data["color"], data["license_number"], data["type_auto"], entry_id))
            conn.commit()
            return jsonify({"success": True, "message": "Updated"})

# Точка входа
if __name__ == "__main__":
    app = create_app()

    # Создание таблиц в БД, если не существуют
    with app.app_context():
        db.create_all()

    # Запуск приложения
    app.run(host=settings.host, port=settings.port)
