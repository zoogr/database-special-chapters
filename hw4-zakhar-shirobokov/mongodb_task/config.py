"""
Конфигурация подключения к MongoDB.
"""

from pymongo import MongoClient
from pymongo.server_api import ServerApi
import os
from dotenv import load_dotenv

load_dotenv()

# Параметры подключения
MONGODB_URI = os.getenv("MONGODB_URI", "mongodb://localhost:27017/")
DATABASE_NAME = os.getenv("DATABASE_NAME", "ecommerce_db")


def get_mongodb_client():
    """
    Создание клиента MongoDB.
    
    Returns:
        MongoClient: Клиент MongoDB
    """
    client = MongoClient(
        MONGODB_URI,
        server_api=ServerApi('1'),
        connectTimeoutMS=5000,
        socketTimeoutMS=5000
    )
    return client


def get_database():
    """
    Получение базы данных.
    
    Returns:
        Database: База данных MongoDB
    """
    client = get_mongodb_client()
    db = client[DATABASE_NAME]
    return db