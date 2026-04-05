"""
Subscriber для pub/sub модели.
Подписывается на каналы и читает сообщения.
"""

import time
import json
from redis import Redis
from config import get_redis_client


class MessageSubscriber:
    """
    Подписчик на сообщения Redis Pub/Sub.
    """
    
    def __init__(self, redis_client: Redis = None):
        """
        Инициализация подписчика.
        
        Args:
            redis_client: Клиент Redis
        """
        self.redis = redis_client or get_redis_client()
        self.pubsub = self.redis.pubsub()
        self.running = False
    
    def subscribe(self, *channels: str):
        """
        Подписка на каналы.
        
        Args:
            channels: Названия каналов
        """
        print(f"\n📡 Подписка на каналы: {', '.join(channels)}")
        self.pubsub.subscribe(*channels)
        print("✅ Подписка оформлена!")
    
    def unsubscribe(self, *channels: str):
        """
        Отписка от каналов.
        
        Args:
            channels: Названия каналов
        """
        print(f"\n🚫 Отписка от каналов: {', '.join(channels)}")
        self.pubsub.unsubscribe(*channels)
    
    def listen(self, timeout: int = None):
        """
        Прослушивание сообщений.
        
        Args:
            timeout: Время прослушивания в секундах (None = бесконечно)
        """
        print("\n👂 Прослушивание сообщений...")
        print("Нажмите Ctrl+C для остановки")
        
        self.running = True
        start_time = time.time()
        message_count = 0
        
        try:
            while self.running:
                # Проверка таймаута
                if timeout and (time.time() - start_time) > timeout:
                    print(f"\n⏰ Таймаут {timeout} секунд истёк")
                    break
                
                # Получение сообщения
                message = self.pubsub.get_message()
                
                if message:
                    # Пропускаем служебные сообщения о подписке
                    if message['type'] in ('subscribe', 'psubscribe'):
                        print(f"✅ Подписан на: {message['channel']}")
                        continue
                    
                    if message['type'] in ('unsubscribe', 'punsubscribe'):
                        print(f"❌ Отписан от: {message['channel']}")
                        continue
                    
                    # Обработка обычного сообщения
                    if message['type'] == 'message':
                        message_count += 1
                        channel = message['channel']
                        data = message['data']
                        
                        # Попытка распарсить JSON
                        try:
                            parsed_data = json.loads(data)
                            print(f"\n📨 [{message_count}] Канал '{channel}':")
                            print(f"   Данные: {parsed_data}")
                        except json.JSONDecodeError:
                            print(f"\n📨 [{message_count}] Канал '{channel}': {data}")
                
                # Небольшая пауза чтобы не нагружать CPU
                time.sleep(0.01)
                
        except KeyboardInterrupt:
            print("\n⏹️  Остановка по команде пользователя")
        
        finally:
            self.running = False
            print(f"\n📊 Всего получено сообщений: {message_count}")
    
    def stop(self):
        """
        Остановка прослушивания.
        """
        self.running = False
    
    def close(self):
        """
        Закрытие соединения.
        """
        self.pubsub.close()
        print("🔌 Соединение закрыто")


def main():
    """
    Пример подписки на сообщения.
    """
    print("=" * 70)
    print("REDIS PUB/SUB - SUBSCRIBER")
    print("=" * 70)
    
    subscriber = MessageSubscriber()
    
    # Подписка на каналы
    subscriber.subscribe("chat", "notifications")
    
    # Прослушивание в течение 30 секунд
    subscriber.listen(timeout=30)
    
    # Отписка и закрытие
    subscriber.unsubscribe("chat", "notifications")
    subscriber.close()
    
    print("\n" + "=" * 70)
    print("✅ Subscriber завершил работу!")
    print("=" * 70)


if __name__ == "__main__":
    main()