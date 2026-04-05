"""
Модуль для работы с кэшированием в Redis.
TTL (Time To Live) - время жизни кэша.
"""

import json
import time
from typing import Any, Optional
from redis import Redis
from config import get_redis_client


class CacheManager:
    """
    Менеджер кэша с поддержкой TTL.
    """
    
    def __init__(self, redis_client: Redis = None):
        """
        Инициализация менеджера кэша.
        
        Args:
            redis_client: Клиент Redis
        """
        self.redis = redis_client or get_redis_client()
    
    def set(self, key: str, value: Any, ttl: int = 60) -> bool:
        """
        Сохранение значения в кэш с TTL.
        
        Args:
            key: Ключ
            value: Значение (любой тип, будет сериализован в JSON)
            ttl: Время жизни в секундах (по умолчанию 60)
            
        Returns:
            bool: True если успешно
        """
        try:
            # Сериализация значения в JSON
            serialized_value = json.dumps(value)
            
            # Установка значения с TTL
            result = self.redis.setex(key, ttl, serialized_value)
            
            print(f"💾 Кэш установлен: {key} (TTL: {ttl}s)")
            return result
            
        except Exception as e:
            print(f"❌ Ошибка записи в кэш: {e}")
            return False
    
    def get(self, key: str) -> Optional[Any]:
        """
        Получение значения из кэша.
        
        Args:
            key: Ключ
            
        Returns:
            Значение или None если не найдено
        """
        try:
            value = self.redis.get(key)
            
            if value is None:
                print(f"⚠️  Кэш не найден: {key}")
                return None
            
            # Десериализация из JSON
            deserialized_value = json.loads(value)
            
            # Проверка оставшегося TTL
            remaining_ttl = self.redis.ttl(key)
            print(f"✅ Кэш получен: {key} (осталось TTL: {remaining_ttl}s)")
            
            return deserialized_value
            
        except json.JSONDecodeError:
            print("❌ Ошибка десериализации JSON")
            return None
        except Exception as e:
            print(f"❌ Ошибка чтения из кэша: {e}")
            return None
    
    def delete(self, key: str) -> bool:
        """
        Удаление значения из кэша.
        
        Args:
            key: Ключ
            
        Returns:
            bool: True если ключ существовал
        """
        try:
            result = self.redis.delete(key)
            if result > 0:
                print(f"🗑️  Кэш удалён: {key}")
                return True
            else:
                print(f"⚠️  Ключ не найден: {key}")
                return False
        except Exception as e:
            print(f"❌ Ошибка удаления из кэша: {e}")
            return False
    
    def clear_pattern(self, pattern: str) -> int:
        """
        Очистка всех ключей по шаблону.
        
        Args:
            pattern: Шаблон ключей (например, "user:*")
            
        Returns:
            int: Количество удалённых ключей
        """
        try:
            keys = self.redis.keys(pattern)
            if keys:
                count = self.redis.delete(*keys)
                print(f"🗑️  Удалено {count} ключей по шаблону: {pattern}")
                return count
            else:
                print(f"⚠️  Ключи по шаблону не найдены: {pattern}")
                return 0
        except Exception as e:
            print(f"❌ Ошибка очистки по шаблону: {e}")
            return 0
    
    def get_ttl(self, key: str) -> int:
        """
        Получение оставшегося TTL ключа.
        
        Args:
            key: Ключ
            
        Returns:
            int: Оставшееся время жизни в секундах (-1 если нет TTL, -2 если ключ не существует)
        """
        return self.redis.ttl(key)
    
    def exists(self, key: str) -> bool:
        """
        Проверка существования ключа.
        
        Args:
            key: Ключ
            
        Returns:
            bool: True если ключ существует
        """
        return self.redis.exists(key) > 0


# ==================== ПРИМЕР ИСПОЛЬЗОВАНИЯ ====================

def expensive_operation(user_id: int) -> dict:
    """
    Имитация дорогой операции (например, запрос к БД).
    """
    print(f"⏳ Выполнение дорогой операции для user_id={user_id}...")
    time.sleep(2)  # Имитация задержки
    
    return {
        "user_id": user_id,
        "name": f"User {user_id}",
        "email": f"user{user_id}@example.com",
        "timestamp": time.time()
    }


def get_user_with_cache(user_id: int, cache_manager: CacheManager) -> dict:
    """
    Получение пользователя с кэшированием.
    
    Args:
        user_id: ID пользователя
        cache_manager: Менеджер кэша
        
    Returns:
        dict: Данные пользователя
    """
    cache_key = f"user:{user_id}"
    
    # Попытка получить из кэша
    cached_data = cache_manager.get(cache_key)
    
    if cached_data is not None:
        print("✨ Данные получены из кэша!")
        return cached_data
    
    # Если в кэше нет - выполняем дорогую операцию
    user_data = expensive_operation(user_id)
    
    # Сохраняем в кэш на 300 секунд (5 минут)
    cache_manager.set(cache_key, user_data, ttl=300)
    
    print("💾 Данные сохранены в кэш и получены из источника!")
    return user_data


def main():
    """
    Пример использования кэширования.
    """
    print("=" * 70)
    print("REDIS CACHING С TTL")
    print("=" * 70)
    
    cache = CacheManager()
    
    print("\n📝 ТЕСТ 1: Первое обращение (кэш отсутствует)")
    user1 = get_user_with_cache(123, cache)
    print(f"Пользователь: {user1}")
    
    print("\n📝 ТЕСТ 2: Второе обращение (данные в кэше)")
    user2 = get_user_with_cache(123, cache)
    print(f"Пользователь: {user2}")
    
    print("\n📝 ТЕСТ 3: Разные пользователи")
    user3 = get_user_with_cache(456, cache)
    print(f"Пользователь: {user3}")
    
    print("\n📝 ТЕСТ 4: Проверка TTL")
    ttl = cache.get_ttl("user:123")
    print(f"Оставшийся TTL для user:123: {ttl} секунд")
    
    print("\n📝 ТЕСТ 5: Ручное удаление из кэша")
    cache.delete("user:123")
    
    print("\n📝 ТЕСТ 6: После удаления (кэш снова отсутствует)")
    user4 = get_user_with_cache(123, cache)
    print(f"Пользователь: {user4}")
    
    print("\n" + "=" * 70)
    print("✅ Кэширование с TTL работает!")
    print("=" * 70)


if __name__ == "__main__":
    main()