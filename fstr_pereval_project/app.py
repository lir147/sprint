from flask import Flask, request, jsonify, render_template_string
from database_handler import DatabaseHandler
import logging

app = Flask(__name__)
db_handler = DatabaseHandler()

logging.basicConfig(level=logging.INFO)

@app.route('/submitData', methods=['POST'])
def submit_data():
    try:
        data = request.get_json()
        if not data or 'raw_data' not in data or 'images' not in data:
            return jsonify({"error": "Missing required fields: 'raw_data' and 'images'"}), 400


        pereval_id = db_handler.add_pereval(data['raw_data'], data['images'])

        return jsonify({
            "success": True,
            "message": "Перевал добавлен",
            "pereval_id": pereval_id
        }), 201

    except Exception as e:
        logging.error(f"Ошибка в API: {e}")
        return jsonify({"error": str(e)}), 500

# ===== GET /perevals =====
@app.route('/perevals', methods=['GET'])
def list_perevals():
    try:
        perevals = db_handler.get_all_perevals()  # список словарей
        html = """
        <h1>Список перевалов</h1>
        <table border="1" cellpadding="5">
        <tr>
            <th>ID</th>
            <th>Название</th>
            <th>Высота</th>
            <th>Координаты</th>
            <th>Status</th>
            <th>Date Added</th>
        </tr>
        {% for p in perevals %}
        <tr>
            <td>{{ p['id'] }}</td>
            <td>{{ p['raw_data']['title'] }}</td>
            <td>{{ p['raw_data'].get('height', '') }}</td>
            <td>
                {% if p['raw_data'].get('coordinates') %}
                    {{ p['raw_data']['coordinates'].get('lat', '') }}, {{ p['raw_data']['coordinates'].get('lon', '') }}
                {% endif %}
            </td>
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

# ===== Запуск сервера =====
if __name__ == '__main__':
    app.run(host='127.0.0.1', port=8080, debug=True)
