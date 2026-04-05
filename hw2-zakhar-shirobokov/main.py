"""
Пример использования CRUD операций.
Демонстрация создания, чтения, обновления и удаления пользователей.
"""

from database import create_tables, drop_tables
from crud import UserCRUD, create_user, get_all_users, get_user_by_id


def main():
    """
    Основная функция для демонстрации CRUD операций.
    """
    print("=" * 60)
    print("📊 SQLAlchemy Core - CRUD операции с PostgreSQL")
    print("=" * 60)
    
    # Шаг 1: Создаём таблицы
    create_tables()
    
    # Шаг 2: Создаём экземпляр CRUD класса
    crud = UserCRUD()
    
    # ==================== CREATE ====================
    print("\n" + "=" * 60)
    print("📝 ШАГ 1: Создание пользователей")
    print("=" * 60)
    
    user1_id = crud.create_user("Иван Иванов", "ivan@example.com", 25)
    user2_id = crud.create_user("Мария Петрова", "maria@example.com", 30)
    user3_id = crud.create_user("Пётр Сидоров", "petr@example.com", 28)
    
    # Попытка создать дубликат (должна завершиться ошибкой)
    print("\n Тест: попытка создать дубликат email...")
    crud.create_user("Дубликат", "ivan@example.com", 99)
    
    # ==================== READ ====================
    print("\n" + "=" * 60)
    print("📚 ШАГ 2: Чтение всех пользователей")
    print("=" * 60)
    
    all_users = crud.get_all_users()
    print(f"\n📋 Всего пользователей в БД: {len(all_users)}")
    for user in all_users:
        print(f"   {user}")
    
    # Чтение одного пользователя
    print("\n🔍 Поиск пользователя по ID...")
    user = crud.get_user_by_id(user1_id)
    if user:
        print(f"   Найден: {user}")
    
    # Поиск несуществующего
    print("\n🔍 Поиск несуществующего пользователя...")
    crud.get_user_by_id(999)
    
    # ==================== UPDATE ====================
    print("\n" + "=" * 60)
    print("✏️  ШАГ 3: Обновление пользователей")
    print("=" * 60)
    
    # Обновление по ID
    print("\n🔄 Обновление имени пользователя...")
    crud.update_user(user1_id, name="Иван Петрович Иванов")
    
    print("\n🔄 Обновление возраста...")
    crud.update_user(user2_id, age=31)
    
    print("\n🔄 Обновление нескольких полей сразу...")
    crud.update_user(user3_id, name="Пётр Александрович Сидоров", age=29)
    
    # Попытка обновить email на существующий (должна завершиться ошибкой)
    print("\n🧪 Тест: попытка установить существующий email...")
    crud.update_user(user3_id, email="ivan@example.com")
    
    # Обновление несуществующего пользователя
    print("\n🧪 Тест: обновление несуществующего пользователя...")
    crud.update_user(999, name="Никто")
    
    # ==================== DELETE ====================
    print("\n" + "=" * 60)
    print("🗑️  ШАГ 4: Удаление пользователей")
    print("=" * 60)
    
    # Удаление пользователя
    print("\n🗑️  Удаление пользователя...")
    crud.delete_user(user3_id)
    
    # Проверка что удалён
    print("\n📚 Проверка - чтение всех пользователей после удаления:")
    all_users = crud.get_all_users()
    print(f"   Осталось пользователей: {len(all_users)}")
    
    # Удаление несуществующего
    print("\n🧪 Тест: удаление несуществующего пользователя...")
    crud.delete_user(999)
    
    # ==================== ФИНАЛЬНЫЙ ОТЧЁТ ====================
    print("\n" + "=" * 60)
    print("📊 ФИНАЛЬНОЕ СОСТОЯНИЕ БАЗЫ ДАННЫХ")
    print("=" * 60)
    
    final_users = crud.get_all_users()
    print(f"\n✅ В базе данных осталось {len(final_users)} пользователей:")
    for user in final_users:
        print(f"   • {user['name']} ({user['email']}), возраст: {user['age']}")
    
    # ==================== ИСПОЛЬЗОВАНИЕ ФУНКЦИЙ-ОБЁРТОК ====================
    print("\n" + "=" * 60)
    print("🧪 Тестирование функций-обёрток")
    print("=" * 60)
    
    print("\n➕ Создание через функцию-обёртку:")
    new_id = create_user("Анна Смирнова", "anna@example.com", 27)
    
    print("\n📚 Чтение через функцию-обёртку:")
    users = get_all_users()
    print(f"   Всего: {len(users)}")
    
    print("\n🔍 Поиск через функцию-обёртку:")
    user = get_user_by_id(new_id)
    print(f"   {user}")
    
    print("\n" + "=" * 60)
    print("✅ Все операции завершены!")
    print("=" * 60)


if __name__ == "__main__":
    main()