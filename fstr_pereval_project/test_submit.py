import requests
import json

BASE_URL = "http://127.0.0.1:8080/submitData"

# 1. Создаём новую запись
data = {
    "raw_data": {
        "name": "Перевал Тестовый",
        "height": 3000,
        "region": "Кавказ",
        "fio": "Иванов Иван",
        "email": "test@example.com",
        "phone": "+79991234567"
    },
    "images": [
        {"url": "http://example.com/test1.jpg"},
        {"url": "http://example.com/test2.jpg"}
    ]
}

resp = requests.post(BASE_URL, json=data)
print("POST status:", resp.status_code)
print("POST response:", resp.json())

pereval_id = resp.json().get("pereval_id")


# 2. Получаем запись по ID
if pereval_id:
    resp = requests.get(f"{BASE_URL}/{pereval_id}")
    print("\nGET by ID status:", resp.status_code)
    print("GET by ID response:", resp.json())


# 3. Пробуем PATCH (редактируем разрешённые поля)
patch_data = {
    "raw_data": {
        "name": "Перевал Обновлённый",
        "height": 3200,
        "region": "Кавказ",   # user.fio/email/phone НЕ трогаем
    },
    "images": [
        {"url": "http://example.com/updated.jpg"}
    ]
}

if pereval_id:
    resp = requests.patch(f"{BASE_URL}/{pereval_id}", json=patch_data)
    print("\nPATCH status:", resp.status_code)
    print("PATCH response:", resp.json())


# 4. Проверяем выборку по email
resp = requests.get(f"{BASE_URL}/?user__email=test@example.com")
print("\nGET by email status:", resp.status_code)
print("GET by email response:", resp.json())
