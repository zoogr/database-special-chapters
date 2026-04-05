import pytest
from datetime import datetime
from models import User
from sqlalchemy.exc import IntegrityError, DataError

class TestUserCreate:
    """Тесты создания пользователя (Create)"""
    
    # === ПОЗИТИВНЫЕ ТЕСТЫ ===
    
    def test_create_user_success(self, db_session, fake):
        """Позитивный тест: создание пользователя с валидными данными"""
        user = User(
            name=fake.name(),
            email=fake.email(),
            age=fake.random_int(min=18, max=80)
        )
        db_session.add(user)
        db_session.commit()
        
        assert user.id is not None
        assert user.created_at is not None
        
    def test_create_multiple_users(self, db_session, fake):
        """Позитивный тест: создание нескольких пользователей"""
        users = [
            User(name=fake.name(), email=fake.email(), age=fake.random_int(18, 60))
            for _ in range(5)
        ]
        db_session.add_all(users)
        db_session.commit()
        
        assert db_session.query(User).count() == 5
    
    # === НЕГАТИВНЫЕ ТЕСТЫ ===
    
    def test_create_user_without_name(self, db_session, fake):
        """Негативный тест: создание пользователя без имени (нарушение NOT NULL)"""
        user = User(name=None, email=fake.email(), age=25)
        db_session.add(user)
        
        with pytest.raises(IntegrityError):
            db_session.commit()
            db_session.rollback()
    
    def test_create_user_without_email(self, db_session, fake):
        """Негативный тест: создание пользователя без email"""
        user = User(name=fake.name(), email=None, age=25)
        db_session.add(user)
        
        with pytest.raises(IntegrityError):
            db_session.commit()
            db_session.rollback()
    
    def test_create_user_duplicate_email(self, db_session, fake):
        """Негативный тест: создание пользователя с дублирующимся email"""
        email = fake.email()
        
        user1 = User(name=fake.name(), email=email, age=25)
        user2 = User(name=fake.name(), email=email, age=30)
        
        db_session.add(user1)
        db_session.commit()
        
        db_session.add(user2)
        with pytest.raises(IntegrityError):
            db_session.commit()
            db_session.rollback()
    
    def test_create_user_invalid_age(self, db_session, fake):
        """Негативный тест: создание пользователя с некорректным возрастом"""
        user = User(name=fake.name(), email=fake.email(), age=-5)
        db_session.add(user)
        db_session.commit()
        
        # Зависит от ограничений БД, может быть негативным тестом
        assert user.age < 0  # Показываем проблему


class TestUserRead:
    """Тесты чтения пользователя (Read)"""
    
    # === ПОЗИТИВНЫЕ ТЕСТЫ ===
    
    @pytest.fixture
    def sample_user(self, db_session, fake):
        """Фикстура для создания тестового пользователя"""
        user = User(
            name=fake.name(),
            email=fake.email(),
            age=fake.random_int(18, 60)
        )
        db_session.add(user)
        db_session.commit()
        return user
    
    def test_get_user_by_id(self, db_session, sample_user):
        """Позитивный тест: получение пользователя по ID"""
        user = db_session.query(User).filter(User.id == sample_user.id).first()
        
        assert user is not None
        assert user.id == sample_user.id
        assert user.name == sample_user.name
        assert user.email == sample_user.email
    
    def test_get_user_by_email(self, db_session, sample_user):
        """Позитивный тест: получение пользователя по email"""
        user = db_session.query(User).filter(User.email == sample_user.email).first()
        
        assert user is not None
        assert user.email == sample_user.email
    
    def test_get_all_users(self, db_session, fake):
        """Позитивный тест: получение всех пользователей"""
        users = [
            User(name=fake.name(), email=fake.email(), age=fake.random_int(18, 60))
            for _ in range(3)
        ]
        db_session.add_all(users)
        db_session.commit()
        
        all_users = db_session.query(User).all()
        assert len(all_users) == 3
    
    # === НЕГАТИВНЫЕ ТЕСТЫ ===
    
    def test_get_nonexistent_user(self, db_session):
        """Негативный тест: получение несуществующего пользователя"""
        user = db_session.query(User).filter(User.id == 9999).first()
        assert user is None
    
    def test_get_user_invalid_email_format(self, db_session):
        """Негативный тест: поиск пользователя с невалидным email"""
        user = db_session.query(User).filter(User.email == "invalid-email").first()
        assert user is None


class TestUserUpdate:
    """Тесты обновления пользователя (Update)"""
    
    @pytest.fixture
    def sample_user(self, db_session, fake):
        """Фикстура для создания тестового пользователя"""
        user = User(name=fake.name(), email=fake.email(), age=25)
        db_session.add(user)
        db_session.commit()
        return user
    
    # === ПОЗИТИВНЫЕ ТЕСТЫ ===
    
    def test_update_user_name(self, db_session, sample_user, fake):
        """Позитивный тест: обновление имени пользователя"""
        sample_user.name = fake.name()
        db_session.commit()
        
        updated_user = db_session.query(User).filter(User.id == sample_user.id).first()
        assert updated_user.name == sample_user.name
    
    def test_update_user_email(self, db_session, sample_user, fake):
        """Позитивный тест: обновление email пользователя"""
        new_email = fake.email()
        sample_user.email = new_email
        db_session.commit()
        
        updated_user = db_session.query(User).filter(User.id == sample_user.id).first()
        assert updated_user.email == new_email
    
    def test_update_multiple_fields(self, db_session, sample_user, fake):
        """Позитивный тест: обновление нескольких полей одновременно"""
        sample_user.name = fake.name()
        sample_user.email = fake.email()
        sample_user.age = fake.random_int(30, 50)
        db_session.commit()
        
        updated_user = db_session.query(User).filter(User.id == sample_user.id).first()
        assert updated_user.name == sample_user.name
        assert updated_user.email == sample_user.email
        assert updated_user.age == sample_user.age
    
    # === НЕГАТИВНЫЕ ТЕСТЫ ===
    
    def test_update_user_duplicate_email(self, db_session, fake):
        """Негативный тест: обновление email на существующий"""
        user1 = User(name=fake.name(), email="user1@test.com", age=25)
        user2 = User(name=fake.name(), email="user2@test.com", age=30)
        
        db_session.add_all([user1, user2])
        db_session.commit()
        
        user2.email = "user1@test.com"
        with pytest.raises(IntegrityError):
            db_session.commit()
            db_session.rollback()
    
    def test_update_nonexistent_user(self, db_session, fake):
        """Негативный тест: обновление несуществующего пользователя"""
        user = db_session.query(User).filter(User.id == 9999).first()
        assert user is None


class TestUserDelete:
    """Тесты удаления пользователя (Delete)"""
    
    @pytest.fixture
    def sample_user(self, db_session, fake):
        """Фикстура для создания тестового пользователя"""
        user = User(name=fake.name(), email=fake.email(), age=25)
        db_session.add(user)
        db_session.commit()
        return user
    
    # === ПОЗИТИВНЫЕ ТЕСТЫ ===
    
    def test_delete_user_by_id(self, db_session, sample_user):
        """Позитивный тест: удаление пользователя по ID"""
        user_id = sample_user.id
        db_session.delete(sample_user)
        db_session.commit()
        
        deleted_user = db_session.query(User).filter(User.id == user_id).first()
        assert deleted_user is None
    
    def test_delete_multiple_users(self, db_session, fake):
        """Позитивный тест: удаление нескольких пользователей"""
        users = [
            User(name=fake.name(), email=fake.email(), age=fake.random_int(18, 60))
            for _ in range(3)
        ]
        db_session.add_all(users)
        db_session.commit()
        
        all_users = db_session.query(User).all()
        for user in all_users:
            db_session.delete(user)
        db_session.commit()
        
        assert db_session.query(User).count() == 0
    
    # === НЕГАТИВНЫЕ ТЕСТЫ ===
    
    def test_delete_nonexistent_user(self, db_session):
        """Негативный тест: попытка удаления несуществующего пользователя"""
        user = db_session.query(User).filter(User.id == 9999).first()
        assert user is None
        # Удаление None не вызовет ошибку, но и ничего не удалит


class TestUserDataValidation:
    """Тесты валидации данных"""
    
    # === НЕГАТИВНЫЕ ТЕСТЫ ===
    
    def test_user_email_unique_constraint(self, db_session, fake):
        """Негативный тест: проверка уникальности email"""
        email = "duplicate@test.com"
        
        user1 = User(name=fake.name(), email=email, age=25)
        user2 = User(name=fake.name(), email=email, age=30)
        
        db_session.add(user1)
        db_session.commit()
        
        db_session.add(user2)
        with pytest.raises(IntegrityError):
            db_session.commit()
            db_session.rollback()
    
    def test_user_name_length(self, db_session, fake):
        """Негативный тест: проверка длины имени"""
        long_name = "A" * 200  # Превышаем лимит в 100 символов
        
        user = User(name=long_name, email=fake.email(), age=25)
        db_session.add(user)
        
        with pytest.raises((DataError, IntegrityError)):
            db_session.commit()
            db_session.rollback()


# Запуск тестов:
# pytest test_crud.py -v  # подробный вывод
# pytest test_crud.py -v -s  # с выводом print
# pytest test_crud.py::TestUserCreate -v  # только тесты создания
# pytest test_crud.py -k "positive"  # только позитивные тесты