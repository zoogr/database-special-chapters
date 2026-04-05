"""
CRUD операции для таблицы users.
Каждая операция имеет обработку ошибок и откат транзакций.
"""

from sqlalchemy import select, update, delete
from sqlalchemy.exc import SQLAlchemyError, IntegrityError
from database import engine, users_table
from typing import Optional, List, Dict, Any


class UserCRUD:
    """
    Класс для выполнения CRUD операций над таблицей users.
    """

    # ==================== CREATE ====================
    def create_user(self, name: str, email: str, age: Optional[int] = None) -> Optional[int]:
        """
        Создание нового пользователя.
        
        Args:
            name: Имя пользователя
            email: Email (должен быть уникальным)
            age: Возраст (необязательный)
            
        Returns:
            int: ID созданного пользователя или None при ошибке
        """
        print(f"\n➕ Создание пользователя: {name} ({email})")
        
        try:
            with engine.begin() as connection:  # begin() автоматически делает commit/rollback
                result = connection.execute(
                    users_table.insert(),
                    {"name": name, "email": email, "age": age}
                )
                user_id = result.inserted_primary_key[0]
                print(f"✅ Пользователь создан с ID: {user_id}")
                return user_id
                
        except IntegrityError as e:
            # Ошибка нарушения целостности (например, дубликат email)
            print(f"❌ Ошибка целостности данных: {e}")
            print("💡 Возможно, пользователь с таким email уже существует")
            return None
            
        except SQLAlchemyError as e:
            # Другие ошибки SQLAlchemy
            print(f"❌ Ошибка SQLAlchemy при создании: {e}")
            return None
            
        except Exception as e:
            # Любые другие ошибки
            print(f"❌ Неожиданная ошибка: {e}")
            return None

    # ==================== READ (все пользователи) ====================
    def get_all_users(self) -> List[Dict[str, Any]]:
        """
        Получение всех пользователей.
        
        Returns:
            List[Dict]: Список словарей с данными пользователей
        """
        print("\n📚 Чтение всех пользователей...")
        
        try:
            with engine.connect() as connection:  # connect() только для чтения
                result = connection.execute(select(users_table))
                users = result.fetchall()
                
                # Преобразуем в список словарей
                users_list = [
                    {"id": row.id, "name": row.name, "email": row.email, "age": row.age}
                    for row in users
                ]
                
                print(f"✅ Найдено пользователей: {len(users_list)}")
                return users_list
                
        except SQLAlchemyError as e:
            print(f"❌ Ошибка при чтении: {e}")
            return []
            
        except Exception as e:
            print(f"❌ Неожиданная ошибка: {e}")
            return []

    # ==================== READ (один пользователь) ====================
    def get_user_by_id(self, user_id: int) -> Optional[Dict[str, Any]]:
        """
        Получение пользователя по ID.
        
        Args:
            user_id: ID пользователя
            
        Returns:
            Dict или None если не найден
        """
        print(f"\n🔍 Поиск пользователя с ID: {user_id}")
        
        try:
            with engine.connect() as connection:
                result = connection.execute(
                    select(users_table).where(users_table.c.id == user_id)
                )
                user = result.fetchone()
                
                if user:
                    user_dict = {
                        "id": user.id,
                        "name": user.name,
                        "email": user.email,
                        "age": user.age
                    }
                    print(f"✅ Пользователь найден: {user_dict}")
                    return user_dict
                else:
                    print(f"⚠️  Пользователь с ID {user_id} не найден")
                    return None
                    
        except SQLAlchemyError as e:
            print(f"❌ Ошибка при чтении: {e}")
            return None

    # ==================== UPDATE ====================
    def update_user(
        self, 
        user_id: int, 
        name: Optional[str] = None,
        email: Optional[str] = None,
        age: Optional[int] = None
    ) -> bool:
        """
        Обновление данных пользователя.
        
        Args:
            user_id: ID пользователя для обновления
            name: Новое имя (необязательно)
            email: Новый email (необязательно)
            age: Новый возраст (необязательно)
            
        Returns:
            bool: True если успешно, False иначе
        """
        print(f"\n✏️  Обновление пользователя с ID: {user_id}")
        
        # Формируем словарь с данными для обновления (только указанные поля)
        update_data = {}
        if name is not None:
            update_data["name"] = name
        if email is not None:
            update_data["email"] = email
        if age is not None:
            update_data["age"] = age
            
        if not update_data:
            print("⚠️  Нет данных для обновления")
            return False
        
        try:
            with engine.begin() as connection:
                result = connection.execute(
                    update(users_table)
                    .where(users_table.c.id == user_id)
                    .values(update_data)
                )
                
                if result.rowcount > 0:
                    print(f"✅ Пользователь {user_id} обновлен. Изменено строк: {result.rowcount}")
                    return True
                else:
                    print(f"⚠️  Пользователь с ID {user_id} не найден")
                    return False
                    
        except IntegrityError as e:
            print(f"❌ Ошибка целостности данных: {e}")
            print("💡 Возможно, такой email уже занят другим пользователем")
            return False
            
        except SQLAlchemyError as e:
            print(f"❌ Ошибка SQLAlchemy при обновлении: {e}")
            return False
            
        except Exception as e:
            print(f"❌ Неожиданная ошибка: {e}")
            return False

    # ==================== DELETE ====================
    def delete_user(self, user_id: int) -> bool:
        """
        Удаление пользователя по ID.
        
        Args:
            user_id: ID пользователя для удаления
            
        Returns:
            bool: True если успешно, False иначе
        """
        print(f"\n🗑️  Удаление пользователя с ID: {user_id}")
        
        try:
            with engine.begin() as connection:
                result = connection.execute(
                    delete(users_table)
                    .where(users_table.c.id == user_id)
                )
                
                if result.rowcount > 0:
                    print(f"✅ Пользователь {user_id} удалён. Удалено строк: {result.rowcount}")
                    return True
                else:
                    print(f"⚠️  Пользователь с ID {user_id} не найден")
                    return False
                    
        except SQLAlchemyError as e:
            print(f"❌ Ошибка SQLAlchemy при удалении: {e}")
            return False
            
        except Exception as e:
            print(f"❌ Неожиданная ошибка: {e}")
            return False


# ==================== УДОБНЫЕ ФУНКЦИИ-ОБЁРТКИ ====================
# Можно использовать как методы класса, так и эти функции

def create_user(name: str, email: str, age: Optional[int] = None) -> Optional[int]:
    """Функция-обёртка для создания пользователя"""
    crud = UserCRUD()
    return crud.create_user(name, email, age)


def get_all_users() -> List[Dict[str, Any]]:
    """Функция-обёртка для получения всех пользователей"""
    crud = UserCRUD()
    return crud.get_all_users()


def get_user_by_id(user_id: int) -> Optional[Dict[str, Any]]:
    """Функция-обёртка для получения пользователя по ID"""
    crud = UserCRUD()
    return crud.get_user_by_id(user_id)


def update_user(user_id: int, **kwargs) -> bool:
    """Функция-обёртка для обновления пользователя"""
    crud = UserCRUD()
    return crud.update_user(user_id, **kwargs)


def delete_user(user_id: int) -> bool:
    """Функция-обёртка для удаления пользователя"""
    crud = UserCRUD()
    return crud.delete_user(user_id)