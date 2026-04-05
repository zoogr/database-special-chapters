"""
Модели данных для приложения трекера задач.
Определяет структуру таблиц базы данных и их связи.
"""

from sqlalchemy import (
    Column, 
    Integer, 
    String, 
    DateTime, 
    ForeignKey, 
    Enum as SQLEnum,
    Text,
    Index
)
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
import enum
from app.database import Base


class TaskStatus(str, enum.Enum):
    """
    Перечисление статусов задачи.
    
    Attributes:
        NEW: Новая задача
        IN_PROGRESS: Задача в работе
        DONE: Задача выполнена
        CANCELLED: Задача отменена
    """
    NEW = "new"
    IN_PROGRESS = "in_progress"
    DONE = "done"
    CANCELLED = "cancelled"


class User(Base):
    """
    Модель пользователя системы.
    
    Attributes:
        id: Уникальный идентификатор пользователя
        email: Электронная почта (уникальная)
        hashed_password: Хэш пароля
        full_name: Полное имя пользователя
        created_at: Дата и время создания записи
    """
    __tablename__ = "users"
    
    id = Column(Integer, primary_key=True, index=True)
    email = Column(String(255), unique=True, index=True, nullable=False)
    hashed_password = Column(String(255), nullable=False)
    full_name = Column(String(100))
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    # Связь с задачами (один ко многим)
    tasks = relationship("Task", back_populates="assignee", cascade="all, delete-orphan")
    
    # Индексы для оптимизации поиска
    __table_args__ = (
        Index('ix_users_email', 'email'),
    )


class Task(Base):
    """
    Модель задачи.
    
    Attributes:
        id: Уникальный идентификатор задачи
        title: Заголовок задачи (до 200 символов)
        description: Подробное описание задачи
        status: Текущий статус задачи
        assignee_id: Идентификатор исполнителя
        created_at: Дата и время создания
        updated_at: Дата и время последнего обновления
        due_date: Крайний срок выполнения
    """
    __tablename__ = "tasks"
    
    id = Column(Integer, primary_key=True, index=True)
    title = Column(String(200), nullable=False, index=True)
    description = Column(Text)
    status = Column(
        SQLEnum(TaskStatus), 
        default=TaskStatus.NEW, 
        index=True,
        nullable=False
    )
    assignee_id = Column(Integer, ForeignKey("users.id", ondelete="SET NULL"))
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    due_date = Column(DateTime(timezone=True))
    
    # Связь с пользователем (многие к одному)
    assignee = relationship("User", back_populates="tasks")
    
    # Индексы для оптимизации запросов
    __table_args__ = (
        Index('ix_tasks_status', 'status'),
        Index('ix_tasks_assignee', 'assignee_id'),
        Index('ix_tasks_created_at', 'created_at'),
        Index('ix_tasks_composite', 'status', 'assignee_id'),
    )