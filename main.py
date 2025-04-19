from flask import Flask, request, jsonify
from flask_sqlalchemy import SQLAlchemy
from admin_panel import init_admin

import databaseMySQL
import settings
from models import db
import base64
import os
from flask import Flask, request, jsonify
from datetime import datetime

app = Flask(__name__)

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


# Путь для сохранения изображений
IMAGE_SAVE_PATH = "static/uploads"
# Базовый URL к статическим файлам (если нужно отдавать по HTTP)
BASE_IMAGE_URL = f'http://{settings.host}/static/uploads'  # Замени на свой актуальный адрес

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

    plate_url = f"{BASE_IMAGE_URL}/{plate_filename}"
    car_url = f"{BASE_IMAGE_URL}/{car_filename}"

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

        # Добавляем в базу данных все данные, включая ссылки на изображения
        databaseMySQL.add_entry(
            table_name,
            (time, color, license_number, type_auto, plate_url, car_url)
        )

        return jsonify({"message": "Entry added successfully"}), 201

    except Exception as e:
        return jsonify({"error": f"Ошибка при обработке данных: {str(e)}"}), 500



@app.route('/oko161', methods=['GET'])
def get_entry():
    """Возвращает список записей из базы данных."""
    table = request.args.get('table', 'None')
    results=databaseMySQL.select_all(table)
    return jsonify(results)  # Возвращаем данные в формате JSON



if __name__ == "__main__":
    app = create_app()

    # Create tables in the database (if they don't exist)
    with app.app_context():
        db.create_all()
    #databaseMySQL.initiate_db()
    app.run(host=settings.host, port=settings.port)