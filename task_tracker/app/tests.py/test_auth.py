"""
Модуль тестов для аутентификации и авторизации.
"""

import pytest
from app.models.task import User
from app.utils.security import verify_password, get_password_hash


class TestAuthentication:
    """Тесты аутентификации."""
    
    def test_user_registration(self, client, db_session):
        """Тест регистрации нового пользователя."""
        user_data = {
            "email": "newuser@example.com",
            "password": "newpassword123",
            "full_name": "New User"
        }
        
        response = client.post("/auth/register", json=user_data)
        
        assert response.status_code == 200
        data = response.json()
        assert data["email"] == "newuser@example.com"
        assert data["full_name"] == "New User"
        assert "id" in data
        assert "hashed_password" not in data
        
        # Проверка в БД
        db_user = db_session.query(User).filter(
            User.email == "newuser@example.com"
        ).first()
        assert db_user is not None
        assert verify_password("newpassword123", db_user.hashed_password)
    
    def test_user_login_success(self, client, test_user):
        """Тест успешного входа."""
        login_data = {
            "username": "test@example.com",
            "password": "password123"
        }
        
        response = client.post("/auth/login", data=login_data)
        
        assert response.status_code == 200
        data = response.json()
        assert "access_token" in data
        assert data["token_type"] == "bearer"
    
    def test_user_login_wrong_password(self, client, test_user):
        """Тест входа с неправильным паролем."""
        login_data = {
            "username": "test@example.com",
            "password": "wrongpassword"
        }
        
        response = client.post("/auth/login", data=login_data)
        
        assert response.status_code == 401
    
    def test_user_login_nonexistent_user(self, client):
        """Тест входа несуществующего пользователя."""
        login_data = {
            "username": "nonexistent@example.com",
            "password": "password123"
        }
        
        response = client.post("/auth/login", data=login_data)
        
        assert response.status_code == 401
    
    def test_duplicate_email_registration(self, client, test_user):
        """Тест регистрации с уже существующим email."""
        user_data = {
            "email": "test@example.com",
            "password": "anotherpassword",
            "full_name": "Another User"
        }
        
        response = client.post("/auth/register", json=user_data)
        
        assert response.status_code == 400


class TestAuthorization:
    """Тесты авторизации."""
    
    def test_access_protected_endpoint_without_token(self, client):
        """Тест доступа к защищенному endpoint без токена."""
        response = client.get("/tasks/")
        assert response.status_code == 401
    
    def test_access_protected_endpoint_with_invalid_token(self, client):
        """Тест доступа с невалидным токеном."""
        headers = {"Authorization": "Bearer invalid_token"}
        response = client.get("/tasks/", headers=headers)
        assert response.status_code == 401


class TestPasswordSecurity:
    """Тесты безопасности паролей."""
    
    def test_password_hashing(self):
        """Тест хэширования пароля."""
        password = "testpassword123"
        hashed = get_password_hash(password)
        
        assert hashed != password
        assert verify_password(password, hashed)
        assert not verify_password("wrongpassword", hashed)
    
    def test_password_hash_uniqueness(self):
        """Тест уникальности хэшей."""
        password = "samepassword"
        hash1 = get_password_hash(password)
        hash2 = get_password_hash(password)
        
        assert hash1 != hash2  # Соль делает хэши разными
        assert verify_password(password, hash1)
        assert verify_password(password, hash2)