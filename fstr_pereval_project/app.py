from flask import Flask, request, jsonify, render_template_string
from database_handler import DatabaseHandler
import logging

app = Flask(__name__)
db_handler = DatabaseHandler()


@app.route('/')
def index():
    return render_template_string("""
    <!DOCTYPE html>
    <html lang="ru">
    <head>
        <meta charset="UTF-8">
        <title>FSTR Pereval API</title>
        <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/css/bootstrap.min.css" rel="stylesheet">
        <style>
            body { padding: 30px; background-color: #f8f9fa; }
            h1 { color: #0d6efd; }
            pre { background: #212529; color: #f8f9fa; padding: 15px; border-radius: 10px; }
            .card { margin-top: 20px; }
        </style>
    </head>
    <body>
        <div class="container">
            <h1>FSTR Pereval API</h1>
            <p class="lead">Добро пожаловать! 🚀</p>

            <div class="card">
                <div class="card-body">
                    <h5>Доступные методы:</h5>
                    <ul>
                        <li><b>POST</b> <a href="/submitDataForm" class="btn btn-sm btn-primary">/submitData</a> — добавить новый перевал</li>
                        <li><b>GET</b> <a href="/perevals" class="btn btn-sm btn-success">/perevals</a> — посмотреть список перевалов</li>
                    </ul>
                </div>
            </div>

            <div class="card">
                <div class="card-body">
                    <h5>Пример POST-запроса:</h5>
                    <pre>
POST http://127.0.0.1:8080/submitData
Content-Type: application/json

{
  "raw_data": {"name": "Перевал X", "height": 3000},
  "images": [{"url": "http://example.com/img1.jpg"}]
}
                    </pre>
                </div>
            </div>
        </div>
    </body>
    </html>
    """)


@app.route('/submitDataForm')
def submit_data_form():
    """HTML-форма для отправки перевала"""
    return render_template_string("""
    <!DOCTYPE html>
    <html lang="ru">
    <head>
        <meta charset="UTF-8">
        <title>Добавить перевал</title>
        <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/css/bootstrap.min.css" rel="stylesheet">
        <style>
            body { padding: 30px; background-color: #f8f9fa; }
            h1 { color: #198754; }
        </style>
    </head>
    <body>
        <div class="container">
            <h1>Добавить новый перевал</h1>
            <form id="perevalForm">
                <div class="mb-3">
                    <label class="form-label">Название перевала</label>
                    <input type="text" class="form-control" id="name" placeholder="Перевал X" required>
                </div>
                <div class="mb-3">
                    <label class="form-label">Высота</label>
                    <input type="number" class="form-control" id="height" placeholder="3000" required>
                </div>
                <div class="mb-3">
                    <label class="form-label">URL изображения</label>
                    <input type="url" class="form-control" id="imageUrl" placeholder="http://example.com/img.jpg" required>
                </div>
                <button type="submit" class="btn btn-success">Отправить</button>
            </form>

            <div id="result" class="alert mt-3" style="display:none;"></div>
        </div>

        <script>
            document.getElementById("perevalForm").addEventListener("submit", async function(event) {
                event.preventDefault();
                let data = {
                    raw_data: {
                        name: document.getElementById("name").value,
                        height: parseInt(document.getElementById("height").value)
                    },
                    images: [
                        { url: document.getElementById("imageUrl").value }
                    ]
                };

                let response = await fetch("/submitData", {
                    method: "POST",
                    headers: { "Content-Type": "application/json" },
                    body: JSON.stringify(data)
                });

                let result = await response.json();
                let resultDiv = document.getElementById("result");
                resultDiv.style.display = "block";
                if(response.ok){
                    resultDiv.className = "alert alert-success";
                    resultDiv.innerText = "✅ " + result.message + " (ID: " + result.pereval_id + ")";
                } else {
                    resultDiv.className = "alert alert-danger";
                    resultDiv.innerText = "❌ Ошибка: " + result.error;
                }
            });
        </script>
    </body>
    </html>
    """)


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


@app.route('/perevals', methods=['GET'])
def get_perevals():
    try:
        perevals = db_handler.get_all_perevals()
        return jsonify(perevals), 200
    except Exception as e:
        logging.error(f"Ошибка при выводе перевалов: {e}")
        return jsonify({"error": str(e)}), 500


if __name__ == '__main__':
    app.run(host='127.0.0.1', port=8080, debug=True)
