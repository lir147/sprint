import requests
import json

url = "http://127.0.0.1:8080/submitData"

# Данные перевала
raw_data = {
    "title": "Перевал Тестовый",
    "height": 2500,
    "coordinates": {"lat": 42.123, "lon": 44.456},
    "description": "Описание тестового перевала",
    "difficulty": "средний",
    "other_field": "тестовое значение"
}


images = []


data = {
    "raw_data": raw_data,
    "images": images
}

# Отправляем POST-запрос
response = requests.post(url, json=data)

print("Status code:", response.status_code)
try:
    print("Response JSON:", response.json())
except:
    print("Response text:", response.text)
