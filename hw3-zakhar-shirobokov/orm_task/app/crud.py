"""
CRUD операции для моделей User и Post.
Использование ORM-методов с каскадным удалением.
"""

from sqlalchemy.orm import Session
from typing import List, Optional
from datetime import datetime
from app.models import User, Post


# ==================== USER CRUD ====================

def create_user(db: Session, username: str, email: str, is_active: bool = True) -> User:
    """
    Создание нового пользователя.
    
    Args:
        db: Сессия базы данных
        username: Имя пользователя
        email: Email
        is_active: Статус активности
        
    Returns:
        User: Созданный пользователь
    """
    db_user = User(
        username=username,
        email=email,
        is_active=is_active
    )
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user


def get_user(db: Session, user_id: int) -> Optional[User]:
    """
    Получение пользователя по ID.
    
    Args:
        db: Сессия базы данных
        user_id: ID пользователя
        
    Returns:
        User или None
    """
    return db.query(User).filter(User.id == user_id).first()


def get_all_users(db: Session) -> List[User]:
    """
    Получение всех пользователей.
    
    Args:
        db: Сессия базы данных
        
    Returns:
        List[User]: Список пользователей
    """
    return db.query(User).all()


def update_user(
    db: Session, 
    user_id: int, 
    username: Optional[str] = None,
    email: Optional[str] = None,
    is_active: Optional[bool] = None
) -> Optional[User]:
    """
    Обновление данных пользователя.
    
    Args:
        db: Сессия базы данных
        user_id: ID пользователя
        username: Новое имя (необязательно)
        email: Новый email (необязательно)
        is_active: Новый статус (необязательно)
        
    Returns:
        User или None
    """
    db_user = get_user(db, user_id)
    if not db_user:
        return None
    
    if username is not None:
        db_user.username = username
    if email is not None:
        db_user.email = email
    if is_active is not None:
        db_user.is_active = is_active
    
    db.commit()
    db.refresh(db_user)
    return db_user


def delete_user(db: Session, user_id: int) -> bool:
    """
    Удаление пользователя (с каскадным удалением постов).
    
    Args:
        db: Сессия базы данных
        user_id: ID пользователя
        
    Returns:
        bool: True если успешно, False если не найден
    """
    db_user = get_user(db, user_id)
    if not db_user:
        return False
    
    # Каскадное удаление сработает автоматически благодаря cascade="all, delete-orphan"
    db.delete(db_user)
    db.commit()
    return True


# ==================== POST CRUD ====================

def create_post(
    db: Session, 
    title: str, 
    content: str, 
    author_id: int,
    publish: bool = False
) -> Post:
    """
    Создание нового поста.
    
    Args:
        db: Сессия базы данных
        title: Заголовок
        content: Содержимое
        author_id: ID автора
        publish: Опубликовать сразу
        
    Returns:
        Post: Созданный пост
    """
    db_post = Post(
        title=title,
        content=content,
        author_id=author_id,
        published_at=datetime.now() if publish else None
    )
    db.add(db_post)
    db.commit()
    db.refresh(db_post)
    return db_post


def get_post(db: Session, post_id: int) -> Optional[Post]:
    """
    Получение поста по ID с информацией об авторе.
    
    Args:
        db: Сессия базы данных
        post_id: ID поста
        
    Returns:
        Post или None
    """
    return db.query(Post).filter(Post.id == post_id).first()


def get_all_posts(db: Session) -> List[Post]:
    """
    Получение всех постов с информацией об авторах.
    
    Args:
        db: Сессия базы данных
        
    Returns:
        List[Post]: Список постов
    """
    return db.query(Post).all()


def get_posts_by_author(db: Session, author_id: int) -> List[Post]:
    """
    Получение всех постов конкретного автора.
    
    Args:
        db: Сессия базы данных
        author_id: ID автора
        
    Returns:
        List[Post]: Список постов
    """
    return db.query(Post).filter(Post.author_id == author_id).all()


def update_post(
    db: Session,
    post_id: int,
    title: Optional[str] = None,
    content: Optional[str] = None,
    publish: Optional[bool] = None
) -> Optional[Post]:
    """
    Обновление поста.
    
    Args:
        db: Сессия базы данных
        post_id: ID поста
        title: Новый заголовок
        content: Новое содержимое
        publish: Опубликовать/снять с публикации
        
    Returns:
        Post или None
    """
    db_post = get_post(db, post_id)
    if not db_post:
        return None
    
    if title is not None:
        db_post.title = title
    if content is not None:
        db_post.content = content
    if publish is not None:
        db_post.published_at = datetime.now() if publish else None
    
    db.commit()
    db.refresh(db_post)
    return db_post


def delete_post(db: Session, post_id: int) -> bool:
    """
    Удаление поста.
    
    Args:
        db: Сессия базы данных
        post_id: ID поста
        
    Returns:
        bool: True если успешно, False если не найден
    """
    db_post = get_post(db, post_id)
    if not db_post:
        return False
    
    db.delete(db_post)
    db.commit()
    return True