from flask import Flask, request, jsonify
from database_handler import DatabaseHandler
import logging

app = Flask(__name__)
db_handler = DatabaseHandler()


@app.route('/submitData', methods=['POST'])
def submit_data():
    try:
        data = request.get_json()
        if not data or 'raw_data' not in data or 'images' not in data:
            return jsonify({"error": "Missing required fields: 'raw_data' and 'images'"}), 400

        pereval_id = db_handler.add_pereval(data['raw_data'], data['images'])

        return jsonify({"success": True, "message": "Перевал добавлен", "pereval_id": pereval_id}), 201
    except Exception as e:
        logging.error(f"Ошибка в API: {e}")
        return jsonify({"error": str(e)}), 500


if __name__ == '__main__':
    app.run(host='127.0.0.1', port=8080, debug=True)