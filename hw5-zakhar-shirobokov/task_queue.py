"""
Producer для очереди задач.
Добавляет задачи в Redis Queue (RQ).
"""

import time
import json
import uuid
from datetime import datetime
from redis import Redis
from config import get_redis_client


class TaskProducer:
    """
    Производитель задач для очереди.
    """
    
    def __init__(self, redis_client: Redis = None, queue_name: str = "task_queue"):
        """
        Инициализация производителя.
        
        Args:
            redis_client: Клиент Redis
            queue_name: Название очереди
        """
        self.redis = redis_client or get_redis_client()
        self.queue_name = queue_name
    
    def create_task(self, task_type: str, payload: dict, priority: str = "normal") -> str:
        """
        Создание и добавление задачи в очередь.
        
        Args:
            task_type: Тип задачи (email/send, report/generate, etc.)
            payload: Данные задачи
            priority: Приоритет (low, normal, high)
            
        Returns:
            str: ID задачи
        """
        task_id = str(uuid.uuid4())
        
        task = {
            "id": task_id,
            "type": task_type,
            "payload": payload,
            "priority": priority,
            "created_at": datetime.now().isoformat(),
            "status": "pending"
        }
        
        # Сериализация
        task_json = json.dumps(task)
        
        # Добавление в очередь (в начало для высоких приоритетов)
        if priority == "high":
            self.redis.lpush(self.queue_name, task_json)
        else:
            self.redis.rpush(self.queue_name, task_json)
        
        print(f"✅ Задача создана: {task_id}")
        print(f"   Тип: {task_type}")
        print(f"   Приоритет: {priority}")
        print(f"   Данные: {payload}")
        
        return task_id
    
    def send_email_task(self, recipient: str, subject: str, body: str) -> str:
        """
        Создание задачи на отправку email.
        """
        return self.create_task(
            task_type="email/send",
            payload={
                "recipient": recipient,
                "subject": subject,
                "body": body
            },
            priority="normal"
        )
    
    def generate_report_task(self, report_type: str, params: dict) -> str:
        """
        Создание задачи на генерацию отчёта.
        """
        return self.create_task(
            task_type="report/generate",
            payload={
                "report_type": report_type,
                "params": params
            },
            priority="high"
        )
    
    def cleanup_task(self, resource_id: str) -> str:
        """
        Создание задачи на очистку ресурсов.
        """
        return self.create_task(
            task_type="system/cleanup",
            payload={
                "resource_id": resource_id
            },
            priority="low"
        )
    
    def get_queue_length(self) -> int:
        """
        Получение длины очереди.
        """
        return self.redis.llen(self.queue_name)
    
    def clear_queue(self) -> int:
        """
        Очистка очереди.
        """
        count = self.get_queue_length()
        self.redis.delete(self.queue_name)
        print(f"🗑️  Очередь очищена ({count} задач удалено)")
        return count


def main():
    """
    Пример создания задач.
    """
    print("=" * 70)
    print("TASK QUEUE - PRODUCER")
    print("=" * 70)
    
    producer = TaskProducer()
    
    print("\n📝 Создание задач...")
    
    # Задачи на отправку email
    print("\n📧 Задачи EMAIL:")
    producer.send_email_task(
        recipient="user1@example.com",
        subject="Добро пожаловать!",
        body="Спасибо за регистрацию!"
    )
    
    producer.send_email_task(
        recipient="user2@example.com",
        subject="Ваш заказ подтверждён",
        body="Заказ #12345 принят в работу"
    )
    
    # Задачи на генерацию отчётов
    print("\n📊 Задачи REPORTS:")
    producer.generate_report_task(
        report_type="sales",
        params={"from": "2024-01-01", "to": "2024-01-31"}
    )
    
    producer.generate_report_task(
        report_type="users",
        params={"period": "monthly", "year": 2024}
    )
    
    # Задачи на очистку
    print("\n🧹 Задачи CLEANUP:")
    producer.cleanup_task(resource_id="temp_files_001")
    producer.cleanup_task(resource_id="cache_old")
    
    # Статистика
    queue_length = producer.get_queue_length()
    print(f"\n📊 В очереди задач: {queue_length}")
    
    print("\n" + "=" * 70)
    print("✅ Producer завершил работу!")
    print("💡 Запустите task_worker.py для обработки задач")
    print("=" * 70)


if __name__ == "__main__":
    main()