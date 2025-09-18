import os
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

# ----------------- Настройка из переменных окружения -----------------
db_host = os.getenv("FSTR_DB_HOST")
db_port = os.getenv("FSTR_DB_PORT", "5432")
db_user = os.getenv("FSTR_LOGIN")
db_pass = os.getenv("FSTR_PASS")
db_name = os.getenv("FSTR_DB_NAME", "pereval_db_re10_user")

# ----------------- Строка подключения с SSL -----------------
DATABASE_URL = f"postgresql://{db_user}:{db_pass}@{db_host}:{db_port}/{db_name}?sslmode=require"

# ----------------- SQLAlchemy engine -----------------
engine = create_engine(DATABASE_URL)

# ----------------- Сессии -----------------
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# ----------------- Функция для получения сессии -----------------
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
