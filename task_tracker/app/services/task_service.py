"""
Сервис для работы с задачами.
Инкапсулирует бизнес-логику и операции с базой данных.
"""

from sqlalchemy.orm import Session
from sqlalchemy import func, extract, and_
from typing import List, Optional, Tuple
from datetime import datetime
from app.models.task import Task, User, TaskStatus
from app.schemas.task import TaskCreate, TaskUpdate, TaskFilter
import pandas as pd


class TaskService:
    """
    Сервис для управления задачами.
    
    Предоставляет методы для CRUD операций и фильтрации задач.
    
    Attributes:
        db: Сессия базы данных
    """
    
    def __init__(self, db: Session):
        """
        Инициализация сервиса.
        
        Args:
            db: Сессия базы данных
        """
        self.db = db
    
    def create_task(self, task: TaskCreate) -> Task:
        """
        Создание новой задачи.
        
        Args:
            task: Данные для создания задачи
            
        Returns:
            Созданная задача
        """
        db_task = Task(**task.model_dump())
        self.db.add(db_task)
        self.db.commit()
        self.db.refresh(db_task)
        return db_task
    
    def get_task(self, task_id: int) -> Optional[Task]:
        """
        Получение задачи по идентификатору.
        
        Args:
            task_id: Идентификатор задачи
            
        Returns:
            Задача или None, если не найдена
        """
        return self.db.query(Task).filter(Task.id == task_id).first()
    
    def get_tasks(self, filters: TaskFilter) -> List[Task]:
        """
        Получение списка задач с фильтрацией.
        
        Args:
            filters: Параметры фильтрации
            
        Returns:
            Список задач, соответствующих фильтрам
        """
        query = self.db.query(Task)
        
        # Применение фильтров
        if filters.status:
            query = query.filter(Task.status == filters.status)
        if filters.assignee_id:
            query = query.filter(Task.assignee_id == filters.assignee_id)
        if filters.date_from:
            query = query.filter(Task.created_at >= filters.date_from)
        if filters.date_to:
            query = query.filter(Task.created_at <= filters.date_to)
        
        return query.all()
    
    def update_task(self, task_id: int, task: TaskUpdate) -> Optional[Task]:
        """
        Обновление задачи.
        
        Args:
            task_id: Идентификатор задачи
            task: Новые данные задачи
            
        Returns:
            Обновленная задача или None
        """
        db_task = self.get_task(task_id)
        if not db_task:
            return None
        
        # Обновление только указанных полей
        update_data = task.model_dump(exclude_unset=True)
        for field, value in update_data.items():
            setattr(db_task, field, value)
        
        self.db.commit()
        self.db.refresh(db_task)
        return db_task
    
    def delete_task(self, task_id: int) -> bool:
        """
        Удаление задачи.
        
        Args:
            task_id: Идентификатор задачи
            
        Returns:
            True если задача удалена, False если не найдена
        """
        db_task = self.get_task(task_id)
        if not db_task:
            return False
        
        self.db.delete(db_task)
        self.db.commit()
        return True
    
    def get_tasks_by_status(self, status: TaskStatus) -> List[Task]:
        """
        Получение задач по статусу.
        
        Args:
            status: Статус задач
            
        Returns:
            Список задач с указанным статусом
        """
        return self.db.query(Task).filter(Task.status == status).all()
    
    def get_overdue_tasks(self) -> List[Task]:
        """
        Получение просроченных задач.
        
        Returns:
            Список просроченных задач
        """
        return self.db.query(Task).filter(
            and_(
                Task.due_date < datetime.now(),
                Task.status != TaskStatus.DONE
            )
        ).all()