"""
Publisher для pub/sub модели.
Публикует сообщения в каналы Redis.
"""

import time
import json
from redis import Redis
from config import get_redis_client


class MessagePublisher:
    """
    Издатель сообщений для Redis Pub/Sub.
    """
    
    def __init__(self, redis_client: Redis = None):
        """
        Инициализация издателя.
        
        Args:
            redis_client: Клиент Redis
        """
        self.redis = redis_client or get_redis_client()
    
    def publish(self, channel: str, message: any) -> int:
        """
        Публикация сообщения в канал.
        
        Args:
            channel: Название канала
            message: Сообщение (любой тип)
            
        Returns:
            int: Количество подписчиков, получивших сообщение
        """
        try:
            # Сериализация сообщения
            if isinstance(message, (dict, list)):
                serialized_message = json.dumps(message)
            else:
                serialized_message = str(message)
            
            # Публикация
            subscribers_count = self.redis.publish(channel, serialized_message)
            
            print(f"📤 Опубликовано в '{channel}': {serialized_message}")
            print(f"   Получателей: {subscribers_count}")
            
            return subscribers_count
            
        except Exception as e:
            print(f"❌ Ошибка публикации: {e}")
            return 0
    
    def publish_multiple(self, channel: str, messages: list, delay: float = 1.0):
        """
        Публикация нескольких сообщений с задержкой.
        
        Args:
            channel: Название канала
            messages: Список сообщений
            delay: Задержка между сообщениями (секунды)
        """
        print(f"\n📢 Публикация {len(messages)} сообщений в канал '{channel}'...")
        
        for i, message in enumerate(messages, 1):
            print(f"\n[{i}/{len(messages)}]")
            self.publish(channel, message)
            time.sleep(delay)
        
        print("\n✅ Все сообщения опубликованы!")


def main():
    """
    Пример публикации сообщений.
    """
    print("=" * 70)
    print("REDIS PUB/SUB - PUBLISHER")
    print("=" * 70)
    
    publisher = MessagePublisher()
    
    # Простые текстовые сообщения
    print("\n📝 ТЕСТ 1: Текстовые сообщения")
    text_messages = [
        "Привет, мир!",
        "Это сообщение 2",
        "Сообщение 3",
        "Пока!"
    ]
    publisher.publish_multiple("chat", text_messages, delay=2)
    
    # JSON сообщения
    print("\n📝 ТЕСТ 2: JSON сообщения")
    json_messages = [
        {"type": "notification", "text": "Новый заказ!", "priority": "high"},
        {"type": "notification", "text": "Оплата получена", "priority": "medium"},
        {"type": "notification", "text": "Заказ доставлен", "priority": "low"}
    ]
    publisher.publish_multiple("notifications", json_messages, delay=2)
    
    print("\n" + "=" * 70)
    print("✅ Publisher завершил работу!")
    print("=" * 70)


if __name__ == "__main__":
    main()