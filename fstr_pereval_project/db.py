# db.py
import os
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

db_host = os.getenv("FSTR_DB_HOST")
db_port = os.getenv("FSTR_DB_PORT")
db_user = os.getenv("FSTR_LOGIN")
db_pass = os.getenv("FSTR_PASS")
db_name = os.getenv("FSTR_DB_NAME", "pereval_db_re10_user")

DATABASE_URL = f"postgresql://pereval_db_re10_user:SF5vJNAwNQroDywpRf8Rg6yQtdZMleWY@dpg-d35tsm3e5dus73eamtqg-a.oregon-postgres.render.com/pereval_db_re10"

engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
