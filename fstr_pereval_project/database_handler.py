import os
import logging
import psycopg2
from psycopg2.extras import RealDictCursor
import json

# Логирование
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class DatabaseHandler:
    def __init__(self):
        self.host = os.getenv('FSTR_DB_HOST', 'localhost')
        self.port = os.getenv('FSTR_DB_PORT', '5432')
        self.user = os.getenv('FSTR_DB_LOGIN', 'postgres')
        self.password = os.getenv('FSTR_DB_PASS', '123654')
        self.database = os.getenv('FSTR_DB_NAME', 'postgres')

    def get_connection(self):
        """Подключение к БД"""
        return psycopg2.connect(
            host=self.host,
            port=self.port,
            user=self.user,
            password=self.password,
            dbname=self.database,
            sslmode='disable',
            cursor_factory=RealDictCursor
        )

    # ========== ДОБАВЛЕНИЕ ПЕРЕВАЛА ==========
    def add_pereval(self, raw_data, images):
        query = """
        INSERT INTO pereval_added (raw_data, images, status, date_added)
        VALUES (%s, %s, 'new', NOW())
        RETURNING id
        """
        conn = None
        try:
            conn = self.get_connection()
            with conn.cursor() as cur:
                raw_data_json = json.dumps(raw_data, ensure_ascii=False)
                images_json = json.dumps(images, ensure_ascii=False)

                cur.execute(query, (raw_data_json, images_json))
                pereval_id = cur.fetchone()['id']
                conn.commit()
                logger.info(f"Перевал добавлен, ID: {pereval_id}")
                return pereval_id
        except Exception as e:
            logger.error(f"Ошибка добавления перевала: {e}")
            if conn:
                conn.rollback()
            raise
        finally:
            if conn:
                conn.close()

    # ========== ВСЕ ПЕРЕВАЛЫ ==========
    def get_all_perevals(self):
        query = "SELECT id, raw_data, images, status, date_added FROM pereval_added ORDER BY date_added DESC"
        conn = None
        try:
            conn = self.get_connection()
            with conn.cursor() as cur:
                cur.execute(query)
                results = cur.fetchall()

                for r in results:
                    if isinstance(r['raw_data'], str):
                        r['raw_data'] = json.loads(r['raw_data'])
                    if isinstance(r['images'], str):
                        r['images'] = json.loads(r['images'])
                    elif r['images'] is None:
                        r['images'] = []

                return results
        except Exception as e:
            logger.error(f"Ошибка получения перевалов: {e}")
            raise
        finally:
            if conn:
                conn.close()

    # ========== ПОЛУЧЕНИЕ ОДНОГО ПЕРЕВАЛА ==========
    def get_pereval_by_id(self, pereval_id):
        query = "SELECT id, raw_data, images, status, date_added FROM pereval_added WHERE id = %s"
        conn = None
        try:
            conn = self.get_connection()
            with conn.cursor() as cur:
                cur.execute(query, (pereval_id,))
                pereval = cur.fetchone()
                if not pereval:
                    return None

                if isinstance(pereval['raw_data'], str):
                    pereval['raw_data'] = json.loads(pereval['raw_data'])
                if isinstance(pereval['images'], str):
                    pereval['images'] = json.loads(pereval['images'])
                elif pereval['images'] is None:
                    pereval['images'] = []

                return pereval
        except Exception as e:
            logger.error(f"Ошибка получения перевала {pereval_id}: {e}")
            raise
        finally:
            if conn:
                conn.close()

    # ========== ОБНОВЛЕНИЕ ПЕРЕВАЛА ==========
    def update_pereval(self, pereval_id, data):
        conn = None
        try:
            conn = self.get_connection()
            with conn.cursor() as cur:
                # Проверяем статус
                cur.execute("SELECT status, raw_data, images FROM pereval_added WHERE id = %s", (pereval_id,))
                record = cur.fetchone()
                if not record:
                    return False, "Запись не найдена"

                if record['status'] != 'new':
                    return False, "Редактирование запрещено: статус не 'new'"

                # Защита от изменения ФИО/email/phone
                raw_data = record['raw_data']
                if isinstance(raw_data, str):
                    raw_data = json.loads(raw_data)

                new_raw_data = data.get("raw_data", raw_data)

                for field in ["fio", "email", "phone"]:
                    if field in new_raw_data and new_raw_data[field] != raw_data.get(field):
                        return False, f"Поле '{field}' редактировать нельзя"

                # Обновляем разрешённые поля
                updated_raw = json.dumps(new_raw_data, ensure_ascii=False)
                updated_images = data.get("images", record["images"])
                if isinstance(updated_images, (dict, list)):
                    updated_images = json.dumps(updated_images, ensure_ascii=False)

                cur.execute("""
                    UPDATE pereval_added
                    SET raw_data = %s,
                        images = %s,
                        date_added = NOW()
                    WHERE id = %s
                """, (updated_raw, updated_images, pereval_id))
                conn.commit()
                return True, "Запись успешно обновлена"
        except Exception as e:
            if conn:
                conn.rollback()
            logger.error(f"Ошибка обновления перевала {pereval_id}: {e}")
            return False, str(e)
        finally:
            if conn:
                conn.close()

    # ========== ВСЕ ПЕРЕВАЛЫ ПО EMAIL ==========
    def get_perevals_by_email(self, email):
        query = "SELECT id, raw_data, images, status, date_added FROM pereval_added WHERE (raw_data->>'email') = %s"
        conn = None
        try:
            conn = self.get_connection()
            with conn.cursor() as cur:
                cur.execute(query, (email,))
                results = cur.fetchall()

                for r in results:
                    if isinstance(r['raw_data'], str):
                        r['raw_data'] = json.loads(r['raw_data'])
                    if isinstance(r['images'], str):
                        r['images'] = json.loads(r['images'])
                    elif r['images'] is None:
                        r['images'] = []

                return results
        except Exception as e:
            logger.error(f"Ошибка получения перевалов по email {email}: {e}")
            raise
        finally:
            if conn:
                conn.close()
