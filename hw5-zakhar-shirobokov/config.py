"""
Конфигурация подключения к Redis.
"""

import redis
from redis import Redis
import os
from dotenv import load_dotenv

load_dotenv()

# Параметры подключения
REDIS_HOST = os.getenv("REDIS_HOST", "localhost")
REDIS_PORT = int(os.getenv("REDIS_PORT", 6379))
REDIS_DB = int(os.getenv("REDIS_DB", 0))
REDIS_PASSWORD = os.getenv("REDIS_PASSWORD", None)


def get_redis_client() -> Redis:
    """
    Создание клиента Redis.
    
    Returns:
        Redis: Клиент Redis
    """
    client = redis.Redis(
        host=REDIS_HOST,
        port=REDIS_PORT,
        db=REDIS_DB,
        password=REDIS_PASSWORD,
        decode_responses=True,
        socket_connect_timeout=5
    )
    return client


def test_connection():
    """
    Проверка подключения к Redis.
    """
    try:
        client = get_redis_client()
        client.ping()
        print("✅ Подключение к Redis успешно!")
        return True
    except redis.ConnectionError as e:
        print(f"❌ Ошибка подключения к Redis: {e}")
        print("💡 Убедитесь, что Redis запущен (redis-server или docker run redis)")
        return False