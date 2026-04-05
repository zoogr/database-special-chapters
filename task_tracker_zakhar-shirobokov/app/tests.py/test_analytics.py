"""
Модуль тестов для аналитики и отчетности.
"""

import pytest
from datetime import datetime, timedelta
from app.models.task import Task, TaskStatus
from app.services.analytics import AnalyticsService


class TestAnalyticsService:
    """Тесты сервиса аналитики."""
    
    def test_get_statistics(self, client, test_user, db_session):
        """Тест получения статистики."""
        # Создание задач с разными статусами
        tasks = [
            Task(title="Task 1", status=TaskStatus.NEW, assignee_id=test_user.id),
            Task(title="Task 2", status=TaskStatus.NEW, assignee_id=test_user.id),
            Task(title="Task 3", status=TaskStatus.IN_PROGRESS, assignee_id=test_user.id),
            Task(title="Task 4", status=TaskStatus.DONE, assignee_id=test_user.id),
        ]
        db_session.add_all(tasks)
        db_session.commit()
        
        # Авторизация
        login_data = {"username": "test@example.com", "password": "password123"}
        response = client.post("/auth/login", data=login_data)
        token = response.json()["access_token"]
        
        # Получение статистики
        response = client.get(
            "/tasks/analytics/statistics",
            headers={"Authorization": f"Bearer {token}"}
        )
        
        assert response.status_code == 200
        data = response.json()
        
        assert data["total_tasks"] == 4
        assert data["by_status"]["new"] == 2
        assert data["by_status"]["in_progress"] == 1
        assert data["by_status"]["done"] == 1
        assert data["completion_rate"] == 25.0  # 1 из 4
    
    def test_get_statistics_empty(self, client, test_user):
        """Тест статистики при отсутствии задач."""
        login_data = {"username": "test@example.com", "password": "password123"}
        response = client.post("/auth/login", data=login_data)
        token = response.json()["access_token"]
        
        response = client.get(
            "/tasks/analytics/statistics",
            headers={"Authorization": f"Bearer {token}"}
        )
        
        assert response.status_code == 200
        data = response.json()
        assert data["total_tasks"] == 0
        assert data["completion_rate"] == 0
    
    def test_export_to_csv(self, client, test_user, db_session):
        """Тест экспорта в CSV."""
        # Создание задач
        tasks = [
            Task(title="CSV Task 1", status=TaskStatus.NEW, assignee_id=test_user.id),
            Task(title="CSV Task 2", status=TaskStatus.DONE, assignee_id=test_user.id),
        ]
        db_session.add_all(tasks)
        db_session.commit()
        
        login_data = {"username": "test@example.com", "password": "password123"}
        response = client.post("/auth/login", data=login_data)
        token = response.json()["access_token"]
        
        response = client.get(
            "/tasks/analytics/export",
            headers={"Authorization": f"Bearer {token}"}
        )
        
        assert response.status_code == 200
        assert response.headers["content-type"] == "text/csv; charset=utf-8"
        
        # Проверка содержимого CSV
        csv_content = response.content.decode('utf-8')
        assert "CSV Task 1" in csv_content
        assert "CSV Task 2" in csv_content
    
    def test_analytics_service_direct(self, db_session, test_user):
        """Прямой тест сервиса аналитики."""
        # Создание данных
        tasks = [
            Task(title="Direct Test 1", status=TaskStatus.NEW, assignee_id=test_user.id),
            Task(title="Direct Test 2", status=TaskStatus.DONE, assignee_id=test_user.id),
        ]
        db_session.add_all(tasks)
        db_session.commit()
        
        # Использование сервиса напрямую
        analytics = AnalyticsService(db_session)
        stats = analytics.get_statistics()
        
        assert stats["total_tasks"] == 2
        assert stats["by_status"]["new"] == 1
        assert stats["by_status"]["done"] == 1


class TestDataFrameGeneration:
    """Тесты генерации DataFrame."""
    
    def test_get_dataframe(self, db_session, test_user):
        """Тест получения DataFrame с задачами."""
        tasks = [
            Task(
                title="DF Task",
                status=TaskStatus.IN_PROGRESS,
                assignee_id=test_user.id,
                created_at=datetime.now()
            ),
        ]
        db_session.add_all(tasks)
        db_session.commit()
        
        analytics = AnalyticsService(db_session)
        df = analytics.get_dataframe()
        
        assert len(df) == 1
        assert df.iloc[0]["title"] == "DF Task"
        assert df.iloc[0]["status"] == "in_progress"