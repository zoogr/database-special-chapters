"""
ORM-модели для таблиц User и Post.
Связь: один ко многим (OneToMany).
Один пользователь может иметь много постов.
"""

from sqlalchemy import Column, Integer, String, Text, DateTime, ForeignKey, Boolean
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.database import Base


class User(Base):
    """
    Модель пользователя.
    
    Таблица: users
    Связи: 
        - Один ко многим с Post (один пользователь -> много постов)
        - Каскадное удаление: при удалении пользователя удаляются все его посты
    """
    __tablename__ = "users"
    
    id = Column(Integer, primary_key=True, index=True)
    username = Column(String(50), unique=True, nullable=False, index=True)
    email = Column(String(255), unique=True, nullable=False, index=True)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    # Связь с Post (один ко многим)
    # cascade="all, delete-orphan" - каскадное удаление постов при удалении пользователя
    posts = relationship(
        "Post", 
        back_populates="author", 
        cascade="all, delete-orphan",
        passive_deletes=True
    )
    
    def __repr__(self):
        return f"<User(id={self.id}, username='{self.username}')>"


class Post(Base):
    """
    Модель поста (статьи).
    
    Таблица: posts
    Связи:
        - Многие к одному с User (много постов -> один автор)
        - При удалении пользователя посты удаляются автоматически (каскад)
    """
    __tablename__ = "posts"
    
    id = Column(Integer, primary_key=True, index=True)
    title = Column(String(200), nullable=False)
    content = Column(Text)
    published_at = Column(DateTime(timezone=True), nullable=True)
    
    # Внешний ключ на таблицу users
    # ondelete="CASCADE" - каскадное удаление на уровне БД
    author_id = Column(
        Integer, 
        ForeignKey("users.id", ondelete="CASCADE"), 
        nullable=False,
        index=True
    )
    
    # Обратная связь с User
    author = relationship("User", back_populates="posts")
    
    def __repr__(self):
        return f"<Post(id={self.id}, title='{self.title}', author_id={self.author_id})>"