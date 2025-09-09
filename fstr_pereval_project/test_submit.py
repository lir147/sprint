import requests

url = "http://127.0.0.1:8080/submitData"
data = {
    "raw_data": {
        "title": "Перевал Тестовый",
        "height": 2500,
        "coordinates": {"lat": 42.123, "lon": 44.456}
    },
    "images": []
}

response = requests.post(url, json=data)
print(response.status_code, response.json())
