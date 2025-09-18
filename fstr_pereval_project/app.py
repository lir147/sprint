import os
import logging
from flask import Flask, request, jsonify, render_template, send_file
from flasgger import Swagger
from dotenv import load_dotenv
from io import BytesIO
from database_handler import DatabaseHandler

# ----------------- Настройка -----------------
load_dotenv()
logging.basicConfig(level=logging.INFO)

DB_HOST = os.getenv("FSTR_DB_HOST")
DB_PORT = os.getenv("FSTR_DB_PORT")
DB_USER = os.getenv("FSTR_LOGIN")
DB_PASS = os.getenv("FSTR_PASS")
DB_NAME = os.getenv("FSTR_DB_NAME", "pereval")

app = Flask(__name__)
swagger = Swagger(app)

db_handler = DatabaseHandler()

# ----------------- Вспомогательные функции -----------------
def parse_input(req):
    """Универсальная обработка данных из JSON или формы"""
    if req.is_json:
        data = req.get_json()
        return data.get("raw_data"), data.get("images", [])
    else:
        raw_data = {
            "name": req.form.get("name"),
            "height": req.form.get("height"),
            "region": req.form.get("region"),
        }
        images = [{"url": url.strip()} for url in req.form.get("images", "").split(",") if url.strip()]
        return raw_data, images

# ----------------- Эндпоинты -----------------
@app.route('/')
def index():
    return render_template("index.html")

@app.route('/perevals', methods=['GET'])
def get_perevals():
    """Получить список всех перевалов
    ---
    tags:
      - Perevals
    responses:
      200:
        description: Список перевалов
    """
    try:
        perevals = db_handler.get_all_perevals()
        return render_template("perevals.html", perevals=perevals)
    except Exception as e:
        logging.error(f"Ошибка при выводе перевалов: {e}")
        return jsonify({"error": str(e)}), 500

@app.route('/submitData', methods=['GET', 'POST'])
def submit_data():
    """Добавление нового перевала
    ---
    tags:
      - Perevals
    parameters:
      - in: body
        name: body
        required: false
        schema:
          type: object
          properties:
            raw_data:
              type: object
            images:
              type: array
              items:
                type: object
                properties:
                  url:
                    type: string
    responses:
      201:
        description: Перевал добавлен
    """
    if request.method == 'GET':
        return render_template("submit.html")

    try:
        raw_data, images = parse_input(request)
        if not raw_data:
            return jsonify({"error": "Missing required raw_data"}), 400

        pereval_id = db_handler.add_pereval(raw_data, images)

        if request.is_json:
            return jsonify({"success": True, "message": "Перевал добавлен", "pereval_id": pereval_id}), 201
        else:
            return render_template("success.html", pereval_id=pereval_id)
    except Exception as e:
        logging.error(f"Ошибка в submit_data: {e}")
        return jsonify({"error": str(e)}), 500

@app.route('/submitData/<int:pereval_id>', methods=['GET'])
def get_pereval(pereval_id):
    """Получить перевал по ID
    ---
    tags:
      - Perevals
    parameters:
      - in: path
        name: pereval_id
        required: true
        type: integer
    responses:
      200:
        description: Информация о перевале
    """
    try:
        pereval = db_handler.get_pereval_by_id(pereval_id)
        if not pereval:
            return jsonify({"error": "Перевал не найден"}), 404
        return jsonify(pereval), 200
    except Exception as e:
        logging.error(f"Ошибка при получении перевала {pereval_id}: {e}")
        return jsonify({"error": str(e)}), 500

@app.route('/submitData/<int:pereval_id>', methods=['PATCH'])
def update_pereval(pereval_id):
    """Обновить перевал, если статус 'new'
    ---
    tags:
      - Perevals
    parameters:
      - in: path
        name: pereval_id
        required: true
        type: integer
      - in: body
        name: body
        required: true
        schema:
          type: object
          properties:
            raw_data:
              type: object
            images:
              type: array
              items:
                type: object
    responses:
      200:
        description: Успешное обновление
    """
    try:
        data = request.get_json()
        if not data:
            return jsonify({"state": 0, "message": "Нет данных для обновления"}), 400

        success, message = db_handler.update_pereval(pereval_id, data)
        return jsonify({"state": 1 if success else 0, "message": message}), (200 if success else 400)
    except Exception as e:
        logging.error(f"Ошибка при обновлении перевала {pereval_id}: {e}")
        return jsonify({"state": 0, "message": str(e)}), 500

@app.route('/userPerevals', methods=['GET'])
def get_perevals_by_email():
    """Получить перевалы пользователя по email
    ---
    tags:
      - Perevals
    parameters:
      - in: query
        name: user__email
        required: true
        type: string
    responses:
      200:
        description: Список перевалов пользователя
    """
    email = request.args.get("user__email")
    if not email:
        return jsonify({"error": "Укажите параметр user__email"}), 400
    try:
        perevals = db_handler.get_perevals_by_email(email)
        return jsonify(perevals), 200
    except Exception as e:
        logging.error(f"Ошибка при получении перевалов по email {email}: {e}")
        return jsonify({"error": str(e)}), 500

@app.route('/areas', methods=['GET'])
def get_areas():
    """Получить все области
    ---
    tags:
      - Areas
    responses:
      200:
        description: Список областей
    """
    try:
        areas = db_handler.get_all_areas()
        return jsonify(areas), 200
    except Exception as e:
        logging.error(f"Ошибка получения областей: {e}")
        return jsonify({"error": str(e)}), 500

@app.route('/activities', methods=['GET'])
def get_activities():
    """Получить все типы активности
    ---
    tags:
      - Activities
    responses:
      200:
        description: Список активностей
    """
    try:
        activities = db_handler.get_activities_types()
        return jsonify(activities), 200
    except Exception as e:
        logging.error(f"Ошибка получения активностей: {e}")
        return jsonify({"error": str(e)}), 500

@app.route('/uploadImage', methods=['POST'])
def upload_image():
    """Загрузить изображение
    ---
    tags:
      - Images
    parameters:
      - in: formData
        name: image
        type: file
        required: true
    responses:
      200:
        description: ID загруженного изображения
    """
    if 'image' not in request.files:
        return jsonify({"error": "Нет файла в запросе"}), 400
    file = request.files['image']
    img_bytes = file.read()
    try:
        image_id = db_handler.add_image(img_bytes)
        return jsonify({"image_id": image_id}), 200
    except Exception as e:
        logging.error(f"Ошибка загрузки изображения: {e}")
        return jsonify({"error": str(e)}), 500

@app.route('/images/<int:image_id>', methods=['GET'])
def get_image(image_id):
    """Получить изображение по ID
    ---
    tags:
      - Images
    parameters:
      - in: path
        name: image_id
        required: true
        type: integer
    responses:
      200:
        description: Изображение
    """
    try:
        img = db_handler.get_image_by_id(image_id)
        if not img:
            return jsonify({"error": "Изображение не найдено"}), 404
        return send_file(BytesIO(img), mimetype='image/jpeg')
    except Exception as e:
        logging.error(f"Ошибка получения изображения {image_id}: {e}")
        return jsonify({"error": str(e)}), 500

# ----------------- Запуск -----------------
if __name__ == '__main__':
    app.run(host='127.0.0.1', port=8080, debug=True)
