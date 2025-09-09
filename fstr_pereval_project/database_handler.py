import os
import logging
import psycopg2
from psycopg2.extras import DictCursor

# Настройка логирования
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class DatabaseHandler:
    def __init__(self):
        self.host = os.getenv('FSTR_DB_HOST', 'localhost')
        self.port = os.getenv('FSTR_DB_PORT', '5432')
        self.user = os.getenv('FSTR_DB_LOGIN', 'postgres')
        self.password = os.getenv('FSTR_DB_PASS', '123654')
        self.database = 'postgres'

    def get_connection(self):
        """Устанавливает соединение с БД."""
        try:
            conn = psycopg2.connect(
                host=self.host,
                port=self.port,
                user=self.user,
                password=self.password,
                database=self.database,
                sslmode='require'
            )
            return conn
        except Exception as e:
            logger.error(f"Ошибка подключения к БД: {e}")
            raise

    def add_pereval(self, raw_data, images):
        """Добавляет перевал в pereval_added с status='new'. Возвращает ID."""
        query = """
        INSERT INTO pereval_added (raw_data, images, status, date_added)
        VALUES (%s, %s, 'new', NOW())
        RETURNING id
        """
        conn = None
        try:
            conn = self.get_connection()
            with conn.cursor() as cur:
                cur.execute(query, (raw_data, images))
                pereval_id = cur.fetchone()[0]
                conn.commit()
                logger.info(f"Перевал добавлен успешно, ID: {pereval_id}")
                return pereval_id
        except Exception as e:
            logger.error(f"Ошибка добавления перевала: {e}")
            if conn:
                conn.rollback()
            raise
        finally:
            if conn:
                conn.close()

    def add_image(self, img_data):
        """Добавляет изображение в pereval_images. Возвращает ID."""
        query = """
        INSERT INTO pereval_images (img, date_added)
        VALUES (%s, NOW())
        RETURNING id
        """
        conn = None
        try:
            conn = self.get_connection()
            with conn.cursor() as cur:
                cur.execute(query, (img_data,))
                image_id = cur.fetchone()[0]
                conn.commit()
                logger.info(f"Изображение добавлено, ID: {image_id}")
                return image_id
        except Exception as e:
            logger.error(f"Ошибка добавления изображения: {e}")
            if conn:
                conn.rollback()
            raise
        finally:
            if conn:
                conn.close()