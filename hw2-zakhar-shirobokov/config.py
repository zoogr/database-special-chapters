"""
Файл конфигурации для подключения к PostgreSQL.
"""

from sqlalchemy import create_engine
from sqlalchemy.pool import StaticPool
import os

# Параметры подключения
DB_CONFIG = {
    "user": "postgres",           # Ваше имя пользователя PostgreSQL
    "password": "postgres",       # Ваш пароль
    "host": "localhost",
    "port": "5432",
    "database": "task_tracker"    # Или создайте новую БД
}

# Формирование URL подключения
DATABASE_URL = (
    f"postgresql://{DB_CONFIG['user']}:{DB_CONFIG['password']}"
    f"@{DB_CONFIG['host']}:{DB_CONFIG['port']}/{DB_CONFIG['database']}"
)

# Создание движка (engine) для SQLAlchemy Core
engine = create_engine(
    DATABASE_URL,
    echo=True,           # Вывод SQL-запросов в консоль (для отладки)
    poolclass=StaticPool,  # Для простоты используем StaticPool
    future=True          # Используем 2.0 стиль
)