from flask import Flask, request, jsonify
from flask_sqlalchemy import SQLAlchemy
from admin_panel import init_admin

import databaseMySQL
import settings
from models import db

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


@app.route('/oko161', methods=['POST'])
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
    return jsonify({"message": "Entry added successfully"}), 201


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