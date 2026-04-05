"""
Worker для очереди задач.
Обрабатывает задачи из Redis Queue.
"""

import time
import json
from datetime import datetime
from typing import Callable, Dict
from redis import Redis
from config import get_redis_client


class TaskWorker:
    """
    Обработчик задач из очереди.
    """
    
    def __init__(self, redis_client: Redis = None, queue_name: str = "task_queue"):
        """
        Инициализация обработчика.
        
        Args:
            redis_client: Клиент Redis
            queue_name: Название очереди
        """
        self.redis = redis_client or get_redis_client()
        self.queue_name = queue_name
        self.handlers: Dict[str, Callable] = {}
        self.running = False
        self.processed_count = 0
        self.failed_count = 0
        
        # Регистрация обработчиков
        self._register_handlers()
    
    def _register_handlers(self):
        """
        Регистрация обработчиков для разных типов задач.
        """
        self.handlers = {
            "email/send": self._handle_email_send,
            "report/generate": self._handle_report_generate,
            "system/cleanup": self._handle_system_cleanup
        }
    
    def _handle_email_send(self, payload: dict) -> bool:
        """
        Обработчик задачи отправки email.
        """
        recipient = payload.get("recipient")
        subject = payload.get("subject")
        body = payload.get("body")
        
        print(f"   📧 Отправка email:")
        print(f"      Кому: {recipient}")
        print(f"      Тема: {subject}")
        print(f"      Текст: {body[:50]}...")
        
        # Имитация отправки
        time.sleep(1)
        
        print(f"   ✅ Email отправлен!")
        return True
    
    def _handle_report_generate(self, payload: dict) -> bool:
        """
        Обработчик задачи генерации отчёта.
        """
        report_type = payload.get("report_type")
        params = payload.get("params")
        
        print(f"   📊 Генерация отчёта:")
        print(f"      Тип: {report_type}")
        print(f"      Параметры: {params}")
        
        # Имитация генерации
        time.sleep(2)
        
        print(f"   ✅ Отчёт сгенерирован!")
        return True
    
    def _handle_system_cleanup(self, payload: dict) -> bool:
        """
        Обработчик задачи очистки системы.
        """
        resource_id = payload.get("resource_id")
        
        print(f"   🧹 Очистка ресурсов:")
        print(f"      Ресурс: {resource_id}")
        
        # Имитация очистки
        time.sleep(1)
        
        print(f"   ✅ Ресурсы очищены!")
        return True
    
    def process_task(self, task_json: str) -> bool:
        """
        Обработка одной задачи.
        
        Args:
            task_json: JSON строка с задачей
            
        Returns:
            bool: True если успешно
        """
        try:
            task = json.loads(task_json)
            
            task_id = task.get("id")
            task_type = task.get("type")
            payload = task.get("payload", {})
            
            print(f"\n🔧 Обработка задачи: {task_id}")
            print(f"   Тип: {task_type}")
            
            # Поиск обработчика
            handler = self.handlers.get(task_type)
            
            if handler:
                # Обновление статуса
                task["status"] = "processing"
                task["started_at"] = datetime.now().isoformat()
                
                # Выполнение
                success = handler(payload)
                
                if success:
                    task["status"] = "completed"
                    task["completed_at"] = datetime.now().isoformat()
                    self.processed_count += 1
                    print(f"   ✅ Задача выполнена!")
                else:
                    task["status"] = "failed"
                    self.failed_count += 1
                    print(f"   ❌ Задача не выполнена!")
            else:
                print(f"   ⚠️  Обработчик для типа '{task_type}' не найден")
                task["status"] = "failed"
                self.failed_count += 1
                return False
            
            return True
            
        except json.JSONDecodeError as e:
            print(f"   ❌ Ошибка парсинга JSON: {e}")
            self.failed_count += 1
            return False
        except Exception as e:
            print(f"   ❌ Ошибка обработки: {e}")
            self.failed_count += 1
            return False
    
    def run(self, poll_interval: float = 1.0):
        """
        Запуск обработки очереди.
        
        Args:
            poll_interval: Интервал опроса очереди (секунды)
        """
        print("\n🚀 Запуск Worker...")
        print("Нажмите Ctrl+C для остановки")
        
        self.running = True
        
        try:
            while self.running:
                # Блокирующее получение задачи из очереди
                result = self.redis.blpop(self.queue_name, timeout=poll_interval)
                
                if result:
                    # result = (queue_name, task_json)
                    queue_name, task_json = result
                    self.process_task(task_json)
                else:
                    # Очередь пуста
                    print(".", end="", flush=True)
        
        except KeyboardInterrupt:
            print("\n\n⏹️  Остановка по команде пользователя")
        
        finally:
            self.running = False
            self.print_stats()
    
    def run_once(self) -> bool:
        """
        Обработка одной задачи (для тестирования).
        
        Returns:
            bool: True если задача обработана
        """
        result = self.redis.blpop(self.queue_name, timeout=5)
        
        if result:
            queue_name, task_json = result
            return self.process_task(task_json)
        
        return False
    
    def print_stats(self):
        """
        Вывод статистики.
        """
        print("\n" + "=" * 70)
        print("📊 СТАТИСТИКА WORKER")
        print("=" * 70)
        print(f"✅ Обработано задач: {self.processed_count}")
        print(f"❌ Ошибок: {self.failed_count}")
        total = self.processed_count + self.failed_count
        if total > 0:
            success_rate = (self.processed_count / total) * 100
            print(f"📈 Успешность: {success_rate:.1f}%")
        print("=" * 70)


def main():
    """
    Запуск worker.
    """
    print("=" * 70)
    print("TASK QUEUE - WORKER")
    print("=" * 70)
    
    worker = TaskWorker()
    
    # Запуск обработки
    worker.run(poll_interval=1.0)


if __name__ == "__main__":
    main()