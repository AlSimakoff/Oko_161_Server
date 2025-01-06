from flask import Flask, request, jsonify


import databaseMySQL
import settings

app = Flask(__name__)

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
    databaseMySQL.add_entry("JournalBLog",(time,color,license_number,type_auto)) #Добавление записи в бд
    return jsonify({"message": "Entry added successfully"}), 201


@app.route('/journalblog', methods=['GET'])
def get_blog():
    """Возвращает список записей из базы данных."""
    results=databaseMySQL.select_all("JournalBLog")
    return jsonify(results)  # Возвращаем данные в формате JSON



if __name__ == "__main__":

    databaseMySQL.initiate_db()
    app.run(host=settings.host, port=settings.port)