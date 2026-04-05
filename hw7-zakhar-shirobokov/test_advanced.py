import pytest
from models import User
from faker import Faker

class TestDataGeneration:
    """Примеры продвинутой генерации тестовых данных"""
    
    def test_generate_users_with_faker(self, db_session, fake):
        """Генерация пользователей с разными типами данных"""
        users = []
        
        for _ in range(10):
            user = User(
                name=fake.name(),
                email=fake.email(),
                age=fake.random_int(min=18, max=80),
            )
            users.append(user)
        
        db_session.add_all(users)
        db_session.commit()
        
        assert db_session.query(User).count() == 10
    
    def test_generate_specific_locale_data(self, db_session):
        """Генерация данных для конкретной локали"""
        fake_ru = Faker('ru_RU')
        fake_en = Faker('en_US')
        
        user_ru = User(name=fake_ru.name(), email=fake_ru.email(), age=25)
        user_en = User(name=fake_en.name(), email=fake_en.email(), age=30)
        
        db_session.add_all([user_ru, user_en])
        db_session.commit()
        
        assert db_session.query(User).count() == 2
    
    def test_generate_bulk_data_performance(self, db_session, fake):
        """Тест производительности при массовой вставке"""
        import time
        
        start_time = time.time()
        
        users = [
            User(
                name=fake.name(),
                email=fake.unique.email(),
                age=fake.random_int(18, 80)
            )
            for _ in range(1000)
        ]
        
        db_session.add_all(users)
        db_session.commit()
        
        end_time = time.time()
        
        assert db_session.query(User).count() == 1000
        assert (end_time - start_time) < 5  # Должно выполниться быстрее 5 секунд