from flask import Flask, request, jsonify, render_template_string
from database_handler import DatabaseHandler
import logging
import json

app = Flask(__name__)
db_handler = DatabaseHandler()

logging.basicConfig(level=logging.INFO)

# POST /submitData
@app.route('/submitData', methods=['POST'])
def submit_data():
    try:
        data = request.get_json()
        if not data or 'raw_data' not in data or 'images' not in data:
            return jsonify({"error": "Missing required fields: 'raw_data' and 'images'"}), 400


        raw_data_json = json.dumps(data['raw_data'])
        images_json = json.dumps(data['images'])

        pereval_id = db_handler.add_pereval(raw_data_json, images_json)
        return jsonify({"success": True, "message": "Перевал добавлен", "pereval_id": pereval_id}), 201
    except Exception as e:
        logging.error(f"Ошибка в API: {e}")
        return jsonify({"error": str(e)}), 500


@app.route('/perevals', methods=['GET'])
def list_perevals():
    try:
        perevals = db_handler.get_all_perevals()
        html = """
        <h1>Список перевалов</h1>
        <table border="1" cellpadding="5">
        <tr><th>ID</th><th>Data</th><th>Status</th><th>Date Added</th></tr>
        {% for p in perevals %}
        <tr>
            <td>{{ p['id'] }}</td>
            <td>{{ p['raw_data'] }}</td>
            <td>{{ p['status'] }}</td>
            <td>{{ p['date_added'] }}</td>
        </tr>
        {% endfor %}
        </table>
        """
        return render_template_string(html, perevals=perevals)
    except Exception as e:
        logging.error(f"Ошибка при выводе перевалов: {e}")
        return f"Ошибка: {str(e)}", 500

if __name__ == '__main__':
    app.run(host='127.0.0.1', port=8080, debug=True)
