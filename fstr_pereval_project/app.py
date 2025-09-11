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



if __name__ == '__main__':
    app.run(host='127.0.0.1', port=8080, debug=True)
