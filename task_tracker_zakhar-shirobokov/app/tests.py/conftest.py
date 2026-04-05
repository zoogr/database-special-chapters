"""
Конфигурация и фикстуры для тестов.
"""

import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from app.database import Base, get_db
from app.main import app
from app.models.task import User
from app.utils.security import get_password_hash
from fastapi.testclient import TestClient

# URL тестовой базы данных (SQLite для скорости)
SQLALCHEMY_DATABASE_URL = "sqlite:///./test.db"

# Создание движка БД
engine = create_engine(
    SQLALCHEMY_DATABASE_URL, 
    connect_args={"check_same_thread": False}
)

# Создание сессий
TestingSessionLocal = sessionmaker(
    autocommit=False, 
    autoflush=False, 
    bind=engine
)


def override_get_db():
    """
    Переопределение зависимости get_db для тестов.
    Использует тестовую базу данных.
    """
    try:
        db = TestingSessionLocal()
        yield db
    finally:
        db.close()


# Переопределение зависимости в приложении
app.dependency_overrides[get_db] = override_get_db


@pytest.fixture(scope="function")
def db_session():
    """
    Фикстура для создания сессии БД.
    
    Создает таблицы перед каждым тестом и удаляет после.
    """
    # Создание всех таблиц
    Base.metadata.create_all(bind=engine)
    
    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()
        # Удаление всех таблиц
        Base.metadata.drop_all(bind=engine)


@pytest.fixture(scope="function")
def client(db_session):
    """
    Фикстура тестового клиента.
    
    Предоставляет HTTP клиент для тестирования API.
    """
    with TestClient(app) as test_client:
        yield test_client


@pytest.fixture
def test_user(db_session):
    """
    Фикстура тестового пользователя.
    
    Создает пользователя для использования в тестах.
    """
    user = User(
        email="test@example.com",
        hashed_password=get_password_hash("password123"),
        full_name="Test User"
    )
    db_session.add(user)
    db_session.commit()
    db_session.refresh(user)
    return user


@pytest.fixture
def authenticated_client(client, test_user):
    """
    Фикстура авторизованного клиента.
    
    Возвращает клиента с токеном авторизации.
    """
    login_data = {"username": "test@example.com", "password": "password123"}
    response = client.post("/auth/login", data=login_data)
    token = response.json()["access_token"]
    
    client.headers["Authorization"] = f"Bearer {token}"
    return client