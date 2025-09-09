import requests
import json

url = "http://127.0.0.1:8080/submitData"

data = {
    "raw_data": {
        "name": "Перевал Тестовый",
        "height": 3000,
        "region": "Кавказ"
    },
    "images": [
        {"url": "http://example.com/test1.jpg"},
        {"url": "http://example.com/test2.jpg"}
    ]
}

response = requests.post(url, json=data)
print("Status code:", response.status_code)
print("Response JSON:", response.json())
