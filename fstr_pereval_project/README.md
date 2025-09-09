# FSTR Pereval Project ✨

Полный проект для управления данными о перевалах в БД PostgreSQL с REST API.

## Установка и настройка

1. **PostgreSQL**: Установите PostgreSQL (если нет). Создайте БД `pereval` и выполните скрипт `pereval.sql` для создания таблиц.
2. **Python и зависимости**: 
   - Убедитесь, что Python 3.8+ установлен.
   - `pip install -r requirements.txt`.
3. **Переменные окружения**: Скопируйте `.env.example` в `.env` и заполните ваши параметры подключения к БД.
4. **Запуск**: `python app.py`. Сервер запустится на `http://localhost:8080`.

## Использование API

- **POST /submitData**: Добавляет новый перевал.
  - Body (JSON): `{"raw_data": {...}, "images": {...}}` (структура как в примере из pereval.sql).
  - Пример ответа: `{"success": true, "pereval_id": 42}`.

Тестируйте с Postman: `POST http://localhost:8080/submitData` с Content-Type `application/json`.

## Git
- Создайте репозиторий: `git init`.
- Ветка: `git checkout -b submitData`.
- Коммиты: После создания файлов, настройки БД и т.д.
- После тестов: `git merge master`.

## Тестирование
- Проверьте добавление данных — статус должен быть 'new'.
- Для изображений вызовите `db_handler.add_image()` напрямую в коде.

Если ошибки — проверьте логи и подключение к БД. 🚀