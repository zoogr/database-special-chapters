"""
Основной файл для демонстрации всех возможностей Redis.
"""

from config import test_connection
from caching import CacheManager, get_user_with_cache
from task_queue import TaskProducer
from task_worker import TaskWorker


def main():
    """
    Демонстрация всех функций.
    """
    print("=" * 70)
    print("REDIS TASK: Полный пример")
    print("=" * 70)
    
    # Проверка подключения
    if not test_connection():
        return
    
    # ==================== КЭШИРОВАНИЕ ====================
    print("\n" + "=" * 70)
    print(" ЧАСТЬ 1: КЭШИРОВАНИЕ С TTL")
    print("=" * 70)
    
    cache = CacheManager()
    
    # Первое обращение
    print("\n1️⃣  Первое обращение (кэш отсутствует):")
    user1 = get_user_with_cache(100, cache)
    print(f"   Результат: {user1}")
    
    # Второе обращение
    print("\n2️⃣  Второе обращение (данные в кэше):")
    user2 = get_user_with_cache(100, cache)
    print(f"   Результат: {user2}")
    
    # Проверка TTL
    ttl = cache.get_ttl("user:100")
    print(f"\n3️⃣  Оставшийся TTL: {ttl} секунд")
    
    # Очистка
    cache.delete("user:100")
    
    # ==================== ОЧЕРЕДЬ ЗАДАЧ ====================
    print("\n" + "=" * 70)
    print("📦 ЧАСТЬ 2: ОЧЕРЕДЬ ЗАДАЧ")
    print("=" * 70)
    
    producer = TaskProducer()
    
    # Создание задач
    print("\n📝 Создание задач...")
    producer.send_email_task("test@example.com", "Тест", "Привет!")
    producer.generate_report_task("sales", {"month": "january"})
    
    queue_length = producer.get_queue_length()
    print(f"\n📊 В очереди: {queue_length} задач")
    
    # Обработка одной задачи
    print("\n⚙️  Обработка одной задачи:")
    worker = TaskWorker()
    worker.run_once()
    
    print("\n" + "=" * 70)
    print("✅ Демонстрация завершена!")
    print("=" * 70)
    print("\n💡 Для pub/sub запустите:")
    print("   1. subscriber.py (в одном терминале)")
    print("   2. publisher.py (в другом терминале)")
    print("\n💡 Для очереди задач:")
    print("   1. task_queue.py (создание задач)")
    print("   2. task_worker.py (обработка задач)")


if __name__ == "__main__":
    main()