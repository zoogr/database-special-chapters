import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from faker import Faker
from models import Base, User

# Создаем фикстуру Faker
@pytest.fixture
def fake():
    """Фикстура для генерации фейковых данных"""
    return Faker('ru_RU')  # Русская локаль

# Фикстура для подключения к тестовой БД
@pytest.fixture(scope="session")
def db_engine():
    """Создание движка БД для тестов"""
    engine = create_engine('postgresql://postgres:postgres@localhost:5432/test_db')
    Base.metadata.create_all(engine)
    yield engine
    Base.metadata.drop_all(engine)

# Фикстура для сессии БД
@pytest.fixture
def db_session(db_engine):
    """Создание сессии БД для каждого теста"""
    Session = sessionmaker(bind=db_engine)
    session = Session()
    yield session
    session.rollback()
    session.close()

# Фикстура для очистки данных после каждого теста
@pytest.fixture(autouse=True)
def clean_db(db_session):
    """Автоматическая очистка БД после каждого теста"""
    yield
    db_session.query(User).delete()
    db_session.commit()