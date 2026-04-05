"""
Модуль тестов для CRUD операций с задачами.
Покрывает тестами весь функционал взаимодействия с БД.
"""

import pytest
from datetime import datetime, timedelta
from app.models.task import Task, TaskStatus, User
from app.schemas.task import TaskCreate, TaskUpdate


class TestTaskCRUD:
    """Тесты CRUD операций для задач."""
    
    def test_create_task_success(self, client, test_user, db_session):
        """Тест успешного создания задачи."""
        # Авторизация
        login_data = {"username": "test@example.com", "password": "password123"}
        response = client.post("/auth/login", data=login_data)
        token = response.json()["access_token"]
        
        # Данные задачи
        task_data = {
            "title": "Тестовая задача",
            "description": "Описание тестовой задачи",
            "status": "new",
            "assignee_id": test_user.id,
            "due_date": (datetime.now() + timedelta(days=7)).isoformat()
        }
        
        # Создание задачи
        response = client.post(
            "/tasks/",
            json=task_data,
            headers={"Authorization": f"Bearer {token}"}
        )
        
        # Проверка результата
        assert response.status_code == 201
        data = response.json()
        assert data["title"] == "Тестовая задача"
        assert data["status"] == "new"
        assert data["assignee_id"] == test_user.id
        
        # Проверка в БД
        db_task = db_session.query(Task).filter(Task.id == data["id"]).first()
        assert db_task is not None
        assert db_task.title == "Тестовая задача"
    
    def test_get_task_by_id(self, client, test_user, db_session):
        """Тест получения задачи по идентификатору."""
        # Создание тестовой задачи
        task = Task(
            title="Задача для получения",
            description="Описание",
            status=TaskStatus.NEW,
            assignee_id=test_user.id
        )
        db_session.add(task)
        db_session.commit()
        db_session.refresh(task)
        
        # Авторизация
        login_data = {"username": "test@example.com", "password": "password123"}
        response = client.post("/auth/login", data=login_data)
        token = response.json()["access_token"]
        
        # Получение задачи
        response = client.get(
            f"/tasks/{task.id}",
            headers={"Authorization": f"Bearer {token}"}
        )
        
        # Проверка
        assert response.status_code == 200
        data = response.json()
        assert data["id"] == task.id
        assert data["title"] == "Задача для получения"
    
    def test_get_task_not_found(self, client, test_user):
        """Тест получения несуществующей задачи."""
        login_data = {"username": "test@example.com", "password": "password123"}
        response = client.post("/auth/login", data=login_data)
        token = response.json()["access_token"]
        
        response = client.get(
            "/tasks/99999",
            headers={"Authorization": f"Bearer {token}"}
        )
        
        assert response.status_code == 404
    
    def test_get_tasks_with_filters(self, client, test_user, db_session):
        """Тест получения списка задач с фильтрацией."""
        # Создание нескольких задач
        tasks = [
            Task(title="Задача 1", status=TaskStatus.NEW, assignee_id=test_user.id),
            Task(title="Задача 2", status=TaskStatus.IN_PROGRESS, assignee_id=test_user.id),
            Task(title="Задача 3", status=TaskStatus.DONE, assignee_id=test_user.id),
        ]
        db_session.add_all(tasks)
        db_session.commit()
        
        # Авторизация
        login_data = {"username": "test@example.com", "password": "password123"}
        response = client.post("/auth/login", data=login_data)
        token = response.json()["access_token"]
        
        # Получение всех задач
        response = client.get(
            "/tasks/",
            headers={"Authorization": f"Bearer {token}"}
        )
        assert response.status_code == 200
        assert len(response.json()) == 3
        
        # Фильтрация по статусу
        response = client.get(
            "/tasks/?status=new",
            headers={"Authorization": f"Bearer {token}"}
        )
        assert response.status_code == 200
        assert len(response.json()) == 1
        assert response.json()[0]["status"] == "new"
    
    def test_update_task(self, client, test_user, db_session):
        """Тест обновления задачи."""
        # Создание задачи
        task = Task(
            title="Старый заголовок",
            status=TaskStatus.NEW,
            assignee_id=test_user.id
        )
        db_session.add(task)
        db_session.commit()
        db_session.refresh(task)
        
        # Авторизация
        login_data = {"username": "test@example.com", "password": "password123"}
        response = client.post("/auth/login", data=login_data)
        token = response.json()["access_token"]
        
        # Обновление
        update_data = {
            "title": "Новый заголовок",
            "status": "in_progress"
        }
        
        response = client.put(
            f"/tasks/{task.id}",
            json=update_data,
            headers={"Authorization": f"Bearer {token}"}
        )
        
        # Проверка
        assert response.status_code == 200
        data = response.json()
        assert data["title"] == "Новый заголовок"
        assert data["status"] == "in_progress"
        
        # Проверка в БД
        db_session.refresh(task)
        assert task.title == "Новый заголовок"
        assert task.status == TaskStatus.IN_PROGRESS
    
    def test_update_task_partial(self, client, test_user, db_session):
        """Тест частичного обновления задачи."""
        task = Task(
            title="Заголовок",
            description="Описание",
            status=TaskStatus.NEW,
            assignee_id=test_user.id
        )
        db_session.add(task)
        db_session.commit()
        
        login_data = {"username": "test@example.com", "password": "password123"}
        response = client.post("/auth/login", data=login_data)
        token = response.json()["access_token"]
        
        # Обновление только статуса
        response = client.put(
            f"/tasks/{task.id}",
            json={"status": "done"},
            headers={"Authorization": f"Bearer {token}"}
        )
        
        assert response.status_code == 200
        assert response.json()["status"] == "done"
        assert response.json()["title"] == "Заголовок"  # Не изменился
    
    def test_delete_task(self, client, test_user, db_session):
        """Тест удаления задачи."""
        task = Task(
            title="Задача для удаления",
            status=TaskStatus.NEW,
            assignee_id=test_user.id
        )
        db_session.add(task)
        db_session.commit()
        task_id = task.id
        
        login_data = {"username": "test@example.com", "password": "password123"}
        response = client.post("/auth/login", data=login_data)
        token = response.json()["access_token"]
        
        response = client.delete(
            f"/tasks/{task_id}",
            headers={"Authorization": f"Bearer {token}"}
        )
        
        assert response.status_code == 204
        
        # Проверка что задача удалена из БД
        deleted_task = db_session.query(Task).filter(Task.id == task_id).first()
        assert deleted_task is None
    
    def test_delete_task_not_found(self, client, test_user):
        """Тест удаления несуществующей задачи."""
        login_data = {"username": "test@example.com", "password": "password123"}
        response = client.post("/auth/login", data=login_data)
        token = response.json()["access_token"]
        
        response = client.delete(
            "/tasks/99999",
            headers={"Authorization": f"Bearer {token}"}
        )
        
        assert response.status_code == 404


class TestTaskValidation:
    """Тесты валидации задач."""
    
    def test_create_task_without_title(self, client, test_user):
        """Тест создания задачи без заголовка."""
        login_data = {"username": "test@example.com", "password": "password123"}
        response = client.post("/auth/login", data=login_data)
        token = response.json()["access_token"]
        
        response = client.post(
            "/tasks/",
            json={"description": "Без заголовка"},
            headers={"Authorization": f"Bearer {token}"}
        )
        
        assert response.status_code == 422  # Validation error
    
    def test_create_task_with_invalid_status(self, client, test_user):
        """Тест создания задачи с невалидным статусом."""
        login_data = {"username": "test@example.com", "password": "password123"}
        response = client.post("/auth/login", data=login_data)
        token = response.json()["access_token"]
        
        response = client.post(
            "/tasks/",
            json={
                "title": "Задача",
                "status": "invalid_status"
            },
            headers={"Authorization": f"Bearer {token}"}
        )
        
        assert response.status_code == 422


class TestTaskDatabaseInteraction:
    """Тесты взаимодействия с базой данных."""
    
    def test_task_cascade_delete(self, client, test_user, db_session):
        """Тест каскадного удаления задач при удалении пользователя."""
        # Создание задач
        tasks = [
            Task(title="Задача 1", status=TaskStatus.NEW, assignee_id=test_user.id),
            Task(title="Задача 2", status=TaskStatus.NEW, assignee_id=test_user.id),
        ]
        db_session.add_all(tasks)
        db_session.commit()
        
        # Удаление пользователя
        db_session.delete(test_user)
        db_session.commit()
        
        # Проверка что задачи удалены
        remaining_tasks = db_session.query(Task).filter(
            Task.assignee_id == test_user.id
        ).all()
        assert len(remaining_tasks) == 0
    
    def test_task_timestamps(self, client, test_user, db_session):
        """Тест автоматического проставления временных меток."""
        before_create = datetime.now()
        
        task = Task(
            title="Задача с временными метками",
            status=TaskStatus.NEW,
            assignee_id=test_user.id
        )
        db_session.add(task)
        db_session.commit()
        db_session.refresh(task)
        
        after_create = datetime.now()
        
        assert task.created_at is not None
        assert before_create <= task.created_at <= after_create
        assert task.updated_at is None  # Еще не обновлялась