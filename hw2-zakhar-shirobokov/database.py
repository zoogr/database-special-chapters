"""
Определение таблицы User и функции для её создания.
Используем SQLAlchemy Core (не ORM).
"""

from sqlalchemy import Table, Column, Integer, String, MetaData
from database import engine

# Метаданные для хранения информации о таблицах
metadata = MetaData()

# Определение таблицы "users"
users_table = Table(
    'users',              # Имя таблицы в БД
    metadata,
    Column('id', Integer, primary_key=True, autoincrement=True),
    Column('name', String(100), nullable=False),
    Column('email', String(255), nullable=False, unique=True),
    Column('age', Integer, nullable=True),
)


def create_tables():
    """
    Создание всех таблиц, определённых в metadata.
    """
    print("📦 Создание таблиц...")
    metadata.create_all(engine)
    print("✅ Таблицы созданы успешно!")


def drop_tables():
    """
    Удаление всех таблиц (для очистки).
    """
    print("🗑️  Удаление таблиц...")
    metadata.drop_all(engine)
    print("✅ Таблицы удалены!")