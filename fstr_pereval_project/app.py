from flask import Flask, request, jsonify, render_template
from database_handler import DatabaseHandler
import logging

app = Flask(__name__)
db_handler = DatabaseHandler()


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
    if request.method == 'GET':
        return render_template("submit.html")

    try:
        if request.is_json:
            data = request.get_json()
            raw_data = data.get("raw_data")
            images = data.get("images", [])
        else:
            raw_data = {
                "name": request.form.get("name"),
                "height": request.form.get("height"),
                "region": request.form.get("region"),
            }
            images = []
            if request.form.get("images"):
                images = [{"url": url.strip()} for url in request.form.get("images").split(",")]

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
        logging.error(f"Ошибка в API: {e}")
        return jsonify({"error": str(e)}), 500


# ===================== ДОБАВЛЕННЫЕ МЕТОДЫ =====================

@app.route('/submitData/<int:pereval_id>', methods=['GET'])
def get_pereval(pereval_id):
    """
    Получить одну запись по ID (включая статус модерации).
    """
    try:
        pereval = db_handler.get_pereval_by_id(pereval_id)
        if not pereval:
            return jsonify({"error": "Перевал не найден"}), 404
        return jsonify(pereval), 200
    except Exception as e:
        logging.error(f"Ошибка при получении перевала: {e}")
        return jsonify({"error": str(e)}), 500


@app.route('/submitData/<int:pereval_id>', methods=['PATCH'])
def update_pereval(pereval_id):
    """
    Обновить существующую запись, если статус 'new'.
    Нельзя менять user.fio, user.email, user.phone.
    """
    try:
        data = request.get_json()
        if not data:
            return jsonify({"state": 0, "message": "Нет данных для обновления"}), 400

        success, message = db_handler.update_pereval(pereval_id, data)

        return jsonify({"state": 1 if success else 0, "message": message}), (200 if success else 400)
    except Exception as e:
        logging.error(f"Ошибка при обновлении перевала: {e}")
        return jsonify({"state": 0, "message": str(e)}), 500


@app.route('/submitData/', methods=['GET'])
def get_perevals_by_email():
    """
    Получить список всех объектов пользователя по email.
    """
    email = request.args.get("user__email")
    if not email:
        return jsonify({"error": "Укажите параметр user__email"}), 400
    try:
        perevals = db_handler.get_perevals_by_email(email)
        return jsonify(perevals), 200
    except Exception as e:
        logging.error(f"Ошибка при получении перевалов по email: {e}")
        return jsonify({"error": str(e)}), 500


if __name__ == '__main__':
    app.run(host='127.0.0.1', port=8080, debug=True)
