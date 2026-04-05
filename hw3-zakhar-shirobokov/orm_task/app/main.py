"""
Пример использования ORM-моделей и CRUD операций.
Демонстрация каскадного удаления.
"""

from sqlalchemy.orm import Session
from app.database import engine, Base, SessionLocal
from app import crud
from app.models import User, Post


def create_tables():
    """Создание всех таблиц."""
    print("📦 Создание таблиц...")
    Base.metadata.create_all(bind=engine)
    print("✅ Таблицы созданы!")


def main():
    """Демонстрация работы с ORM."""
    print("=" * 70)
    print("ORM TASK: User и Post с каскадным удалением")
    print("=" * 70)
    
    # Создание таблиц
    create_tables()
    
    # Создание сессии
    db = SessionLocal()
    
    try:
        # ==================== CREATE ====================
        print("\n" + "=" * 70)
        print("📝 ШАГ 1: Создание пользователей и постов")
        print("=" * 70)
        
        # Создание пользователей
        user1 = crud.create_user(db, username="alice", email="alice@example.com")
        user2 = crud.create_user(db, username="bob", email="bob@example.com")
        
        print(f"\n✅ Создан пользователь: {user1}")
        print(f"✅ Создан пользователь: {user2}")
        
        # Создание постов
        post1 = crud.create_post(db, "Первый пост Алисы", "Содержание поста 1", user1.id, publish=True)
        post2 = crud.create_post(db, "Второй пост Алисы", "Содержание поста 2", user1.id, publish=False)
        post3 = crud.create_post(db, "Пост Боба", "Содержание поста 3", user2.id, publish=True)
        
        print(f"✅ Создан пост: {post1}")
        print(f"✅ Создан пост: {post2}")
        print(f"✅ Создан пост: {post3}")
        
        # ==================== READ ====================
        print("\n" + "=" * 70)
        print("📚 ШАГ 2: Чтение данных")
        print("=" * 70)
        
        # Получение всех пользователей
        users = crud.get_all_users(db)
        print(f"\n👥 Всего пользователей: {len(users)}")
        for user in users:
            print(f"   • {user}")
        
        # Получение всех постов
        posts = crud.get_all_posts(db)
        print(f"\n📄 Всего постов: {len(posts)}")
        for post in posts:
            print(f"   • {post} (автор: {post.author.username})")
        
        # Получение постов конкретного автора
        alice_posts = crud.get_posts_by_author(db, user1.id)
        print(f"\n📄 Посты пользователя {user1.username}: {len(alice_posts)}")
        for post in alice_posts:
            print(f"   • {post.title}")
        
        # ==================== UPDATE ====================
        print("\n" + "=" * 70)
        print("✏️  ШАГ 3: Обновление данных")
        print("=" * 70)
        
        # Обновление пользователя
        updated_user = crud.update_user(db, user1.id, email="alice.new@example.com")
        print(f"\n✅ Email обновлён: {updated_user.email}")
        
        # Обновление поста
        updated_post = crud.update_post(db, post1.id, title="Обновлённый заголовок", publish=True)
        print(f"✅ Заголовок обновлён: {updated_post.title}")
        
        # ==================== DELETE (с каскадом) ====================
        print("\n" + "=" * 70)
        print("🗑️  ШАГ 4: Удаление с каскадом")
        print("=" * 70)
        
        # Проверка количества постов перед удалением
        posts_before = crud.get_all_posts(db)
        print(f"\n📊 Постов до удаления: {len(posts_before)}")
        
        # Удаление пользователя (должны удалиться и его посты)
        print(f"\n🗑️  Удаление пользователя {user1.username}...")
        crud.delete_user(db, user1.id)
        
        # Проверка после удаления
        posts_after = crud.get_all_posts(db)
        print(f"📊 Постов после удаления: {len(posts_after)}")
        print("✅ Посты пользователя удалены автоматически (каскадное удаление)!")
        
        # ==================== ФИНАЛЬНЫЙ ОТЧЁТ ====================
        print("\n" + "=" * 70)
        print("📊 ФИНАЛЬНОЕ СОСТОЯНИЕ")
        print("=" * 70)
        
        users = crud.get_all_users(db)
        posts = crud.get_all_posts(db)
        
        print(f"\n👥 Пользователей: {len(users)}")
        for user in users:
            print(f"   • {user.username} ({user.email})")
        
        print(f"\n📄 Постов: {len(posts)}")
        for post in posts:
            print(f"   • {post.title} (автор: {post.author.username})")
        
        print("\n" + "=" * 70)
        print("✅ Задание выполнено успешно!")
        print("=" * 70)
        
    finally:
        db.close()


if __name__ == "__main__":
    main()