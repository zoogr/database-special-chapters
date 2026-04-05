"""
Подключение к базе данных PostgreSQL.
"""

from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
import os
from dotenv import load_dotenv

# Загрузка переменных окружения
load_dotenv()

# Получение URL базы данных
DATABASE_URL = os.getenv("DATABASE_URL")

# Создание движка
engine = create_engine(DATABASE_URL, echo=True)

# Создание сессии
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Базовый класс для моделей
Base = declarative_base()


def get_db():
    """
    Фабрика сессий базы данных.
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()