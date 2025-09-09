import os
import logging
import psycopg2
from psycopg2.extras import RealDictCursor
import json

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
        return psycopg2.connect(
            host=self.host,
            port=self.port,
            user=self.user,
            password=self.password,
            dbname=self.database,
            sslmode='disable',
            cursor_factory=RealDictCursor
        )

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
                raw_data_json = json.dumps(raw_data)
                images_json = json.dumps(images)

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

    def get_all_perevals(self):
        query = "SELECT id, raw_data, status, date_added FROM pereval_added ORDER BY date_added DESC"
        conn = None
        try:
            conn = self.get_connection()
            with conn.cursor() as cur:
                cur.execute(query)
                results = cur.fetchall()
                # Преобразуем JSON-строку обратно в Python dict
                for r in results:
                    r['raw_data'] = json.loads(r['raw_data'])
                return results
        except Exception as e:
            logger.error(f"Ошибка получения перевалов: {e}")
            raise
        finally:
            if conn:
                conn.close()
