import os
import logging
import psycopg2
from psycopg2.extras import RealDictCursor
import json

# ----------------- Логирование -----------------
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# ----------------- DatabaseHandler -----------------
class DatabaseHandler:
    def __init__(self, host=None, port=None, user=None, password=None, database=None):
        self.host = host or os.getenv('FSTR_DB_HOST', 'dpg-d35ti4hr0fns73bf88h0-a.oregon-postgres.render.com')
        self.port = port or os.getenv('FSTR_DB_PORT', '5432')
        self.user = user or os.getenv('FSTR_DB_LOGIN', os.getenv('FSTR_LOGIN', 'pereval_db_re10'))
        self.password = password or os.getenv('FSTR_DB_PASS', 'SF5vJNAwNQroDywpRf8Rg6yQtdZMleWY')
        self.database = database or os.getenv('FSTR_DB_NAME', 'pereval_db_re10_user')

    def get_connection(self):
        """Создать подключение к БД (Render-friendly)"""
        ssl_mode = "disable" if self.host in ("localhost", "127.0.0.1") else "disable"

        return psycopg2.connect(
            host=self.host,
            port=self.port,
            user=self.user,
            password=self.password,
            dbname=self.database,
            sslmode='require',
            connect_timeout=10,
            cursor_factory=RealDictCursor
        )

    # ----------------- Вспомогательные методы -----------------
    def parse_json_field(self, field):
        """Унификация обработки JSON-поля"""
        if isinstance(field, str):
            return json.loads(field)
        elif field is None:
            return []
        return field

    # ----------------- Добавление перевала -----------------
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

    # ----------------- Получение всех перевалов -----------------
    def get_all_perevals(self):
        query = "SELECT id, raw_data, images, status, date_added, date_updated FROM pereval_added ORDER BY date_added DESC"
        conn = None
        try:
            conn = self.get_connection()
            with conn.cursor() as cur:
                cur.execute(query)
                results = cur.fetchall()
                for r in results:
                    r['raw_data'] = self.parse_json_field(r['raw_data'])
                    r['images'] = self.parse_json_field(r['images'])
                return results
        except Exception as e:
            logger.error(f"Ошибка получения всех перевалов: {e}")
            raise
        finally:
            if conn:
                conn.close()

    # ----------------- Получение перевала по ID -----------------
    def get_pereval_by_id(self, pereval_id):
        query = "SELECT id, raw_data, images, status, date_added, date_updated FROM pereval_added WHERE id = %s"
        conn = None
        try:
            conn = self.get_connection()
            with conn.cursor() as cur:
                cur.execute(query, (pereval_id,))
                pereval = cur.fetchone()
                if not pereval:
                    return None
                pereval['raw_data'] = self.parse_json_field(pereval['raw_data'])
                pereval['images'] = self.parse_json_field(pereval['images'])
                return pereval
        except Exception as e:
            logger.error(f"Ошибка получения перевала {pereval_id}: {e}")
            raise
        finally:
            if conn:
                conn.close()

    # ----------------- Обновление перевала -----------------
    def update_pereval(self, pereval_id, data):
        conn = None
        try:
            conn = self.get_connection()
            with conn.cursor() as cur:
                cur.execute("SELECT status, raw_data, images FROM pereval_added WHERE id = %s", (pereval_id,))
                record = cur.fetchone()
                if not record:
                    return False, "Запись не найдена"

                if record['status'] != 'new':
                    return False, "Редактирование запрещено: статус не 'new'"

                raw_data = self.parse_json_field(record['raw_data'])
                new_raw_data = data.get("raw_data", raw_data)

                # Защита от изменения ФИО/email/phone
                for field in ["fio", "email", "phone"]:
                    if field in new_raw_data and new_raw_data[field] != raw_data.get(field):
                        return False, f"Поле '{field}' редактировать нельзя"

                updated_raw = json.dumps(new_raw_data, ensure_ascii=False)
                updated_images = data.get("images", self.parse_json_field(record['images']))
                if isinstance(updated_images, (dict, list)):
                    updated_images = json.dumps(updated_images, ensure_ascii=False)

                cur.execute("""
                    UPDATE pereval_added
                    SET raw_data = %s,
                        images = %s,
                        date_updated = NOW()
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

    # ----------------- Получение перевалов по email -----------------
    def get_perevals_by_email(self, email):
        query = "SELECT id, raw_data, images, status, date_added, date_updated FROM pereval_added WHERE (raw_data->'user'->>'email') = %s"
        conn = None
        try:
            conn = self.get_connection()
            with conn.cursor() as cur:
                cur.execute(query, (email,))
                results = cur.fetchall()
                for r in results:
                    r['raw_data'] = self.parse_json_field(r['raw_data'])
                    r['images'] = self.parse_json_field(r['images'])
                return results
        except Exception as e:
            logger.error(f"Ошибка получения перевалов по email {email}: {e}")
            raise
        finally:
            if conn:
                conn.close()

    # ----------------- Получение всех областей -----------------
    def get_all_areas(self):
        query = "SELECT id, id_parent, title FROM pereval_areas ORDER BY id"
        conn = None
        try:
            conn = self.get_connection()
            with conn.cursor() as cur:
                cur.execute(query)
                return cur.fetchall()
        except Exception as e:
            logger.error(f"Ошибка получения областей: {e}")
            raise
        finally:
            if conn:
                conn.close()

    # ----------------- Получение всех типов активности -----------------
    def get_activities_types(self):
        query = "SELECT id, title FROM spr_activities_types ORDER BY id"
        conn = None
        try:
            conn = self.get_connection()
            with conn.cursor() as cur:
                cur.execute(query)
                return cur.fetchall()
        except Exception as e:
            logger.error(f"Ошибка получения типов активностей: {e}")
            raise
        finally:
            if conn:
                conn.close()

    # ----------------- Добавление изображения -----------------
    def add_image(self, img_bytes):
        query = "INSERT INTO pereval_images (img, date_added) VALUES (%s, NOW()) RETURNING id"
        conn = None
        try:
            conn = self.get_connection()
            with conn.cursor() as cur:
                cur.execute(query, (psycopg2.Binary(img_bytes),))
                image_id = cur.fetchone()['id']
                conn.commit()
                return image_id
        except Exception as e:
            if conn:
                conn.rollback()
            logger.error(f"Ошибка добавления изображения: {e}")
            raise
        finally:
            if conn:
                conn.close()

    # ----------------- Получение изображения по ID -----------------
    def get_image_by_id(self, image_id):
        query = "SELECT img FROM pereval_images WHERE id = %s"
        conn = None
        try:
            conn = self.get_connection()
            with conn.cursor() as cur:
                cur.execute(query, (image_id,))
                record = cur.fetchone()
                return record['img'] if record else None
        except Exception as e:
            logger.error(f"Ошибка получения изображения {image_id}: {e}")
            raise
        finally:
            if conn:
                conn.close()

 # ----------------- Удаление перевала -----------------
    def delete_pereval(self, pereval_id):
        query = "DELETE FROM pereval_added WHERE id = %s"
        conn = None
        try:
            conn = self.get_connection()
            with conn.cursor() as cur:
                cur.execute(query, (pereval_id,))
                conn.commit()
                logger.info(f"Перевал {pereval_id} удалён")
                return True
        except Exception as e:
            if conn:
                conn.rollback()
            logger.error(f"Ошибка удаления перевала {pereval_id}: {e}")
            return False
        finally:
            if conn:
                conn.close()