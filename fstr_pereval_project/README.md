# FSTR Pereval Project ✨

Полный проект для управления данными о перевалах в PostgreSQL с REST API и Swagger-документацией.

---

## Установка и настройка

1. **PostgreSQL**

   * Установите PostgreSQL, если он ещё не установлен.
   * Создайте базу данных `pereval`.
   * Выполните скрипт `pereval.sql` для создания таблиц и начальных данных.

2. **Python и зависимости**

   * Убедитесь, что установлен Python 3.8+.
   * Установите зависимости:

     ```bash
     pip install -r requirements.txt
     ```

3. **Переменные окружения**

   * Скопируйте `.env.example` в `.env`:

     ```bash
     cp .env.example .env
     ```
   * Заполните параметры подключения к вашей БД.

4. **Запуск сервера**

   ```bash
   python app.py
   ```

   * Сервер будет доступен по адресу: [http://localhost:8080](http://localhost:8080)
   * Swagger-документация: [http://localhost:8080/apidocs](http://localhost:8080/apidocs)

---

## Эндпоинты API

| Метод     | URL                                | Описание                                | Пример запроса                                                 | Пример ответа                                                              |
| --------- | ---------------------------------- | --------------------------------------- | -------------------------------------------------------------- | -------------------------------------------------------------------------- |
| **POST**  | `/submitData`                      | Добавить новый перевал                  | `json {"raw_data": {...}, "images": [{"url": "image1.jpg"}]} ` | `json {"success": true, "message": "Перевал добавлен", "pereval_id": 42} ` |
| **GET**   | `/submitData/<pereval_id>`         | Получить перевал по ID                  | `/submitData/42`                                               | `json {"id":42,"raw_data":{...},"images":[...],"status":"new"} `           |
| **PATCH** | `/submitData/<pereval_id>`         | Обновить перевал (только статус 'new')  | `json {"raw_data": {...}, "images": [...]}`                    | `json {"state":1,"message":"Запись успешно обновлена"} `                   |
| **GET**   | `/submitData/?user__email=<email>` | Получить перевалы пользователя по email | `/submitData/?user__email=user@email.tld`                      | `json [{"id":42,"raw_data":{...},"images":[...],"status":"new"}] `         |
| **GET**   | `/perevals`                        | Получить все перевалы                   | —                                                              | HTML-страница со списком перевалов                                         |
| **GET**   | `/`                                | Главная страница                        | —                                                              | HTML-страница с формой добавления перевала                                 |

---

## Пример структуры `raw_data` для перевала

```json
{
  "beautyTitle": "пер. ",
  "title": "Пхия",
  "other_titles": "Триев",
  "connect": "",
  "add_time": "2021-09-22 13:18:13",
  "user": {
    "email": "user@email.tld",
    "phone": "79031234567",
    "fam": "Пупкин",
    "name": "Василий",
    "otc": "Иванович"
  },
  "coords": {
    "latitude": "45.3842",
    "longitude": "7.1525",
    "height": "1200"
  },
  "level": {
    "winter": "",
    "summer": "1А",
    "autumn": "1А",
    "spring": ""
  }
}
```

Пример `images`:

```json
[
  {"url": "image1.jpg", "title": "Седловина"},
  {"url": "image2.jpg", "title": "Подъём"}
]
```

---

## Работа с Git

* Создайте репозиторий:

  ```bash
  git init
  ```
* Создайте отдельную ветку для новой фичи:

  ```bash
  git checkout -b submitData
  ```
* Коммиты должны быть понятными и регулярными.
* После реализации фичи слейте ветку в `master`:

  ```bash
  git merge submitData
  ```

---

## Тестирование

1. Добавьте новый перевал через `/submitData`.

   * Статус перевала должен быть `'new'`.
2. Для изображений используйте метод `db_handler.add_image()`.
3. Проверьте Swagger-документацию для всех эндпоинтов: [http://localhost:8080/apidocs](http://localhost:8080/apidocs).
4. Логи ошибок выводятся в консоль. Проверяйте подключение к БД при возникновении проблем.
