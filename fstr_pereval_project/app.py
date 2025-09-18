import os
import logging
from flask import Flask, request, jsonify, render_template
from flasgger import Swagger
from dotenv import load_dotenv
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

db_handler = DatabaseHandler(
    host=DB_HOST,
    port=DB_PORT,
    user=DB_USER,
    password=DB_PASS,
    dbname=DB_NAME
)


# ----------------- Вспомогательные функции -----------------
def parse_input(req):
    """
    Универсальная обработка данных из JSON или формы
    """
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
    try:
        perevals = db_handler.get_all_perevals()
        return render_template("perevals.html", perevals=perevals)
    except Exception as e:
        logging.error(f"Ошибка при выводе перевалов: {e}")
        return jsonify({"error": str(e)}), 500


@app.route('/submitData', methods=['GET', 'POST'])
def submit_data():
    """
    Submit new mountain pass
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
        schema:
          type: object
          properties:
            success:
              type: boolean
            pereval_id:
              type: integer
    """
    if request.method == 'GET':
        return render_template("submit.html")

    try:
        raw_data, images = parse_input(request)
        if not raw_data:
            return jsonify({"error": "Missing required raw_data"}), 400

        pereval_id = db_handler.add_pereval(raw_data, images)

        if request.is_json:
            return jsonify({
                "success": True,
                "message": "Перевал добавлен",
                "pereval_id": pereval_id
            }), 201
        else:
            return render_template("success.html", pereval_id=pereval_id)

    except Exception as e:
        logging.error(f"Ошибка в submit_data: {e}")
        return jsonify({"error": str(e)}), 500


@app.route('/submitData/<int:pereval_id>', methods=['GET'])
def get_pereval(pereval_id):
    """
    Получить одну запись по ID
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
    """
    Обновить существующую запись, если статус 'new'
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


@app.route('/submitData/', methods=['GET'])
def get_perevals_by_email():
    """
    Получить список всех объектов пользователя по email
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


# ----------------- Запуск -----------------
if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8080, debug=True)
