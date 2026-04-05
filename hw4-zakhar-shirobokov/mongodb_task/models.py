"""
Класс для работы с коллекцией orders (заказы в интернет-магазине).
Сложная структура данных с вложенными документами.
"""

from pymongo import MongoClient, ASCENDING, DESCENDING
from pymongo.errors import DuplicateKeyError, ConnectionFailure
from datetime import datetime, timedelta
from typing import List, Dict, Any, Optional
from bson import ObjectId
from faker import Faker
import random

fake = Faker('ru_RU')


class OrderCollection:
    """
    Класс для управления коллекцией заказов.
    
    Структура документа:
    {
        "_id": ObjectId,
        "order_number": str,                    # Номер заказа
        "customer": {                           # Вложенный документ: клиент
            "customer_id": str,
            "name": str,
            "email": str,
            "phone": str,
            "address": {                        # Вложенный документ: адрес
                "street": str,
                "city": str,
                "country": str,
                "postal_code": str
            }
        },
        "items": [                              # Массив вложенных документов
            {
                "product_id": str,
                "name": str,
                "category": str,
                "quantity": int,
                "price": float,
                "discount": float
            }
        ],
        "payment": {                            # Вложенный документ: оплата
            "method": str,                      # card/cash/online
            "status": str,                      # pending/completed/failed
            "transaction_id": str,
            "amount": float
        },
        "shipping": {                           # Вложенный документ: доставка
            "method": str,                      # courier/pickup/post
            "status": str,                      # pending/shipped/delivered
            "tracking_number": str,
            "estimated_delivery": datetime
        },
        "order_date": datetime,
        "status": str,                          # new/processing/completed/cancelled
        "total_amount": float,
        "discount_amount": float,
        "final_amount": float,
        "notes": str,
        "metadata": {                           # Дополнительные метаданные
            "source": str,                      # website/mobile/app
            "ip_address": str,
            "user_agent": str,
            "session_id": str
        },
        "created_at": datetime,
        "updated_at": datetime
    }
    """
    
    def __init__(self, database):
        """
        Инициализация коллекции.
        
        Args:
            database: База данных MongoDB
        """
        self.db = database
        self.collection = database['orders']
    
    def create_indexes(self):
        """
        Создание индексов для оптимизации запросов.
        """
        print("\n📊 Создание индексов...")
        
        # Одиночные индексы
        self.collection.create_index(
            [("order_number", ASCENDING)],
            unique=True,
            name="idx_order_number_unique"
        )
        
        self.collection.create_index(
            [("customer.customer_id", ASCENDING)],
            name="idx_customer_id"
        )
        
        self.collection.create_index(
            [("customer.address.city", ASCENDING)],
            name="idx_customer_city"
        )
        
        self.collection.create_index(
            [("order_date", DESCENDING)],
            name="idx_order_date_desc"
        )
        
        self.collection.create_index(
            [("status", ASCENDING)],
            name="idx_status"
        )
        
        self.collection.create_index(
            [("payment.status", ASCENDING)],
            name="idx_payment_status"
        )
        
        self.collection.create_index(
            [("shipping.status", ASCENDING)],
            name="idx_shipping_status"
        )
        
        # Составные индексы
        self.collection.create_index(
            [
                ("customer.customer_id", ASCENDING),
                ("order_date", DESCENDING)
            ],
            name="idx_customer_date"
        )
        
        self.collection.create_index(
            [
                ("status", ASCENDING),
                ("order_date", DESCENDING)
            ],
            name="idx_status_date"
        )
        
        self.collection.create_index(
            [
                ("customer.address.city", ASCENDING),
                ("status", ASCENDING)
            ],
            name="idx_city_status"
        )
        
        # Полнотекстовый индекс
        self.collection.create_index(
            [
                ("customer.name", "text"),
                ("customer.email", "text"),
                ("items.name", "text"),
                ("notes", "text")
            ],
            name="idx_text_search"
        )
        
        print("✅ Индексы созданы успешно!")
    
    def generate_sample_order(self, order_num: int) -> Dict[str, Any]:
        """
        Генерация одного заказа со сложной структурой.
        
        Args:
            order_num: Порядковый номер заказа
            
        Returns:
            Dict: Документ заказа
        """
        # Генерация товаров
        categories = ['Электроника', 'Одежда', 'Продукты', 'Книги', 'Спорт', 'Дом']
        num_items = random.randint(1, 5)
        
        items = []
        for _ in range(num_items):
            item = {
                "product_id": f"PROD-{random.randint(10000, 99999)}",
                "name": fake.word().title() + " " + fake.word(),
                "category": random.choice(categories),
                "quantity": random.randint(1, 10),
                "price": round(random.uniform(100, 50000), 2),
                "discount": round(random.uniform(0, 20), 2)
            }
            items.append(item)
        
        # Расчет сумм
        subtotal = sum(item["price"] * item["quantity"] for item in items)
        discount_amount = round(subtotal * random.uniform(0, 0.15), 2)
        final_amount = round(subtotal - discount_amount, 2)
        
        # Генерация дат
        order_date = fake.date_time_between(start_date='-1y', end_date='now')
        
        # Статусы
        order_statuses = ['new', 'processing', 'completed', 'cancelled']
        payment_statuses = ['pending', 'completed', 'failed']
        shipping_statuses = ['pending', 'shipped', 'delivered']
        payment_methods = ['card', 'cash', 'online']
        shipping_methods = ['courier', 'pickup', 'post']
        sources = ['website', 'mobile', 'app']
        
        order_status = random.choice(order_statuses)
        
        document = {
            "order_number": f"ORD-{2024000 + order_num}",
            "customer": {
                "customer_id": f"CUST-{random.randint(1000, 9999)}",
                "name": fake.name(),
                "email": fake.email(),
                "phone": fake.phone_number(),
                "address": {
                    "street": fake.street_address(),
                    "city": fake.city(),
                    "country": "Russia",
                    "postal_code": fake.postcode()
                }
            },
            "items": items,
            "payment": {
                "method": random.choice(payment_methods),
                "status": random.choice(payment_statuses) if order_status != 'cancelled' else 'failed',
                "transaction_id": f"TXN-{random.randint(100000, 999999)}",
                "amount": final_amount
            },
            "shipping": {
                "method": random.choice(shipping_methods),
                "status": random.choice(shipping_statuses) if order_status == 'completed' else 'pending',
                "tracking_number": f"TRK-{random.randint(1000000, 9999999)}",
                "estimated_delivery": order_date + timedelta(days=random.randint(3, 14))
            },
            "order_date": order_date,
            "status": order_status,
            "total_amount": subtotal,
            "discount_amount": discount_amount,
            "final_amount": final_amount,
            "notes": fake.sentence(nb_words=10) if random.random() > 0.7 else "",
            "metadata": {
                "source": random.choice(sources),
                "ip_address": fake.ipv4(),
                "user_agent": fake.user_agent(),
                "session_id": fake.uuid4()
            },
            "created_at": order_date,
            "updated_at": datetime.now()
        }
        
        return document
    
    def insert_sample_data(self, num_records: int = 1000):
        """
        Вставка тестовых данных.
        
        Args:
            num_records: Количество записей для генерации
        """
        print(f"\n📝 Генерация {num_records} заказов...")
        
        orders = []
        for i in range(num_records):
            order = self.generate_sample_order(i)
            orders.append(order)
        
        print("💾 Вставка данных в коллекцию...")
        try:
            result = self.collection.insert_many(orders)
            print(f"✅ Вставлено {len(result.inserted_ids)} документов")
            return result.inserted_ids
        except DuplicateKeyError as e:
            print(f"❌ Ошибка: дублирование ключа - {e}")
            return []
        except Exception as e:
            print(f"❌ Ошибка вставки: {e}")
            return []
    
    def create_order(self, order_data: Dict[str, Any]) -> Optional[ObjectId]:
        """
        Создание нового заказа.
        
        Args:
            order_data: Данные заказа
            
        Returns:
            ObjectId: ID созданного документа или None
        """
        try:
            order_data["created_at"] = datetime.now()
            order_data["updated_at"] = datetime.now()
            
            result = self.collection.insert_one(order_data)
            print(f"✅ Заказ создан: {result.inserted_id}")
            return result.inserted_id
        except DuplicateKeyError:
            print("❌ Заказ с таким номером уже существует")
            return None
        except Exception as e:
            print(f"❌ Ошибка создания заказа: {e}")
            return None
    
    def get_order_by_number(self, order_number: str) -> Optional[Dict[str, Any]]:
        """
        Поиск заказа по номеру.
        
        Args:
            order_number: Номер заказа
            
        Returns:
            Dict или None
        """
        try:
            order = self.collection.find_one({"order_number": order_number})
            if order:
                order["_id"] = str(order["_id"])  # Конвертация ObjectId
            return order
        except Exception as e:
            print(f"❌ Ошибка поиска: {e}")
            return None
    
    def get_orders_by_customer(self, customer_id: str) -> List[Dict[str, Any]]:
        """
        Получение всех заказов клиента.
        
        Args:
            customer_id: ID клиента
            
        Returns:
            List[Dict]: Список заказов
        """
        try:
            cursor = self.collection.find(
                {"customer.customer_id": customer_id}
            ).sort("order_date", -1)
            
            orders = list(cursor)
            for order in orders:
                order["_id"] = str(order["_id"])
            
            return orders
        except Exception as e:
            print(f"❌ Ошибка поиска: {e}")
            return []
    
    def update_order_status(self, order_number: str, new_status: str) -> bool:
        """
        Обновление статуса заказа.
        
        Args:
            order_number: Номер заказа
            new_status: Новый статус
            
        Returns:
            bool: True если успешно
        """
        try:
            result = self.collection.update_one(
                {"order_number": order_number},
                {
                    "$set": {
                        "status": new_status,
                        "updated_at": datetime.now()
                    }
                }
            )
            
            if result.modified_count > 0:
                print(f"✅ Статус обновлён: {order_number} -> {new_status}")
                return True
            else:
                print(f"⚠️  Заказ не найден: {order_number}")
                return False
        except Exception as e:
            print(f"❌ Ошибка обновления: {e}")
            return False
    
    def delete_order(self, order_number: str) -> bool:
        """
        Удаление заказа.
        
        Args:
            order_number: Номер заказа
            
        Returns:
            bool: True если успешно
        """
        try:
            result = self.collection.delete_one({"order_number": order_number})
            if result.deleted_count > 0:
                print(f"✅ Заказ удалён: {order_number}")
                return True
            else:
                print(f"⚠️  Заказ не найден: {order_number}")
                return False
        except Exception as e:
            print(f"❌ Ошибка удаления: {e}")
            return False
    
    def get_collection_stats(self) -> Dict[str, Any]:
        """
        Получение статистики коллекции.
        
        Returns:
            Dict: Статистика
        """
        stats = self.collection.aggregate([
            {
                "$group": {
                    "_id": "$status",
                    "count": {"$sum": 1},
                    "total_revenue": {"$sum": "$final_amount"}
                }
            }
        ])
        
        return list(stats)