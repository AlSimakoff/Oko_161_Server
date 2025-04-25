from flask import Flask, request, jsonify, url_for, render_template
from flask_sqlalchemy import SQLAlchemy
from admin_panel import init_admin

import databaseMySQL
import settings
from models import db
import base64
import os
from flask import Flask, request, jsonify
from datetime import datetime

app = Flask(__name__, template_folder="templates")

IMAGE_SAVE_PATH='/static/uploads'

def create_app():
    """Create and configure the Flask application."""


    # Configure database connection
    app.config[
        'SQLALCHEMY_DATABASE_URI'] = f'mysql+mysqlconnector://{settings.db_user}:{settings.db_pass}@{settings.hostMySQL}/{settings.database_name}'
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

    # Initialize database with app context
    db.init_app(app)

    # Initialize admin panel
    init_admin(app)

    return app

@app.route('/')
def dashboard():
    selected_table = request.args.get('table', 'bolshoilog_img')
    allowed_tables = databaseMySQL.get_allowed_tables()

    if selected_table not in allowed_tables:
        selected_table = allowed_tables[0] if allowed_tables else None

    rows = databaseMySQL.select_all(selected_table) if selected_table else []

    return render_template(
        'dashboard.html',
        rows=rows,
        tables=allowed_tables,
        selected_table=selected_table
    )

@app.route("/api/data")
def get_table_data():
    table = request.args.get("table")
    try:
        rows = databaseMySQL.select_all(table)
        return jsonify({
            "success": True,
            "data": rows
        })
    except Exception as e:
        return jsonify({
            "success": False,
            "error": str(e)
        })

@app.route("/api/tables")
def get_tables():
    try:
        tables = databaseMySQL.get_allowed_tables()
        return jsonify({"success": True, "tables": tables})
    except Exception as e:
        return jsonify({"success": False, "error": str(e)})

@app.route("/api/data/<table>")
def get_table_data_api(table):  # другое имя функции!
    try:
        rows = databaseMySQL.select_all(table)
        return jsonify({"success": True, "data": rows})
    except Exception as e:
        return jsonify({"success": False, "error": str(e)})

'''@app.route('/oko161', methods=['POST'])
def add_entry():
    """Добавляет новой записи в базу данных."""
    data = request.get_json()  # Получаем данные из запроса
    time = data.get('time')
    color = data.get('color')
    license_number = data.get('license_number')
    type_auto = data.get('type_auto')
    table_name = data.get('table_name')
    if not time or not color or not license_number or not type_auto:
        return jsonify({"error": "one of fields are required"}), 400
    databaseMySQL.add_entry(table_name, (time, color, license_number, type_auto)) #Добавление записи в бд
    return jsonify({"message": "Entry added successfully"}), 201'''




@app.route('/oko161', methods=['POST'])
def add_entry():
    """Добавляет новую запись в базу данных и сохраняет изображения."""
    data = request.get_json()

    time = data.get('time')
    color = data.get('color')
    license_number = data.get('license_number')
    type_auto = data.get('type_auto')
    table_name = data.get('table_name')
    img_plate_b64 = data.get('img_plate')
    img_car_b64 = data.get('img_car')

    if not time or not color or not license_number or not type_auto:
        return jsonify({"error": "one of fields is missing"}), 400

    # Генерация уникальных имён файлов
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    plate_filename = f"{license_number}_{timestamp}_plate.jpg"
    car_filename = f"{license_number}_{timestamp}_car.jpg"
    plate_path = os.path.join(IMAGE_SAVE_PATH, plate_filename)
    car_path = os.path.join(IMAGE_SAVE_PATH, car_filename)

    try:
        # Сохраняем изображения на диск
        if img_plate_b64:
            plate_data = base64.b64decode(img_plate_b64)
            with open(plate_path, 'wb') as f:
                f.write(plate_data)

        if img_car_b64:
            car_data = base64.b64decode(img_car_b64)
            with open(car_path, 'wb') as f:
                f.write(car_data)

        # Добавляем в базу только имена файлов
        databaseMySQL.add_entry(
            table_name,
            (time, color, license_number, type_auto, plate_filename, car_filename)
        )

        return jsonify({"message": "Entry added successfully"}), 201

    except Exception as e:
        return jsonify({"error": f"Ошибка при обработке данных: {str(e)}"}), 500




@app.route('/oko161', methods=['GET'])
def get_entry():
    """Возвращает список записей из базы данных."""
    table = request.args.get('table', 'None')
    results=databaseMySQL.select_all(table)

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




@app.route('/table/<table_name>')
def full_table_view(table_name):
    if table_name not in databaseMySQL.get_allowed_tables():
        return "Таблица не найдена", 404

    data = databaseMySQL.select_all(table_name)
    return render_template("table_view.html", table_name=table_name, data=data)



@app.route('/api/entries/<table_name>')
def get_entries(table_name):
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



if __name__ == "__main__":
    app = create_app()

    # Create tables in the database (if they don't exist)
    with app.app_context():
        db.create_all()
    #databaseMySQL.initiate_db()
    app.run(host=settings.host, port=settings.port)