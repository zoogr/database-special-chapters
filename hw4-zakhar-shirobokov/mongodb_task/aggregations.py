"""
Агрегационные аналитические запросы.
Используют созданные индексы для оптимизации.
"""

from datetime import datetime, timedelta
from typing import List, Dict, Any


class AggregationQueries:
    """
    Класс для выполнения агрегационных запросов.
    """
    
    def __init__(self, collection):
        """
        Инициализация.
        
        Args:
            collection: Коллекция MongoDB
        """
        self.collection = collection
    
    def total_revenue_by_status(self) -> List[Dict[str, Any]]:
        """
        Общая выручка по статусам заказов.
        Использует индекс idx_status.
        
        Returns:
            List[Dict]: Статистика по статусам
        """
        print("\n📊 Выручка по статусам заказов:")
        print("-" * 60)
        
        pipeline = [
            {
                "$group": {
                    "_id": "$status",
                    "order_count": {"$sum": 1},
                    "total_revenue": {"$sum": "$final_amount"},
                    "avg_order_value": {"$avg": "$final_amount"}
                }
            },
            {
                "$sort": {"total_revenue": -1}
            },
            {
                "$project": {
                    "_id": 0,
                    "status": "$_id",
                    "order_count": 1,
                    "total_revenue": {"$round": ["$total_revenue", 2]},
                    "avg_order_value": {"$round": ["$avg_order_value", 2]}
                }
            }
        ]
        
        result = list(self.collection.aggregate(pipeline))
        
        for item in result:
            print(f"  {item['status']:15} | Заказы: {item['order_count']:4} | "
                  f"Выручка: {item['total_revenue']:>12.2f} | "
                  f"Средний: {item['avg_order_value']:>8.2f}")
        
        return result
    
    def revenue_by_city(self) -> List[Dict[str, Any]]:
        """
        Выручка по городам.
        Использует индекс idx_customer_city.
        
        Returns:
            List[Dict]: Статистика по городам
        """
        print("\n📊 Выручка по городам:")
        print("-" * 60)
        
        pipeline = [
            {
                "$group": {
                    "_id": "$customer.address.city",
                    "order_count": {"$sum": 1},
                    "total_revenue": {"$sum": "$final_amount"},
                    "unique_customers": {"$addToSet": "$customer.customer_id"}
                }
            },
            {
                "$addFields": {
                    "unique_customers_count": {"$size": "$unique_customers"}
                }
            },
            {
                "$sort": {"total_revenue": -1}
            },
            {
                "$limit": 10
            },
            {
                "$project": {
                    "_id": 0,
                    "city": "$_id",
                    "order_count": 1,
                    "total_revenue": {"$round": ["$total_revenue", 2]},
                    "unique_customers": "$unique_customers_count"
                }
            }
        ]
        
        result = list(self.collection.aggregate(pipeline))
        
        for i, item in enumerate(result, 1):
            print(f"  {i:2}. {item['city']:20} | Заказы: {item['order_count']:3} | "
                  f"Клиенты: {item['unique_customers']:3} | "
                  f"Выручка: {item['total_revenue']:>10.2f}")
        
        return result
    
    def sales_by_category(self) -> List[Dict[str, Any]]:
        """
        Продажи по категориям товаров.
        Использует unwind для массива items.
        
        Returns:
            List[Dict]: Статистика по категориям
        """
        print("\n📊 Продажи по категориям товаров:")
        print("-" * 60)
        
        pipeline = [
            {"$unwind": "$items"},
            {
                "$group": {
                    "_id": "$items.category",
                    "total_quantity": {"$sum": "$items.quantity"},
                    "total_revenue": {
                        "$sum": {
                            "$multiply": [
                                "$items.quantity",
                                "$items.price"
                            ]
                        }
                    },
                    "order_count": {"$sum": 1}
                }
            },
            {
                "$sort": {"total_revenue": -1}
            },
            {
                "$project": {
                    "_id": 0,
                    "category": "$_id",
                    "total_quantity": 1,
                    "total_revenue": {"$round": ["$total_revenue", 2]},
                    "order_count": 1
                }
            }
        ]
        
        result = list(self.collection.aggregate(pipeline))
        
        for item in result:
            print(f"  {item['category']:15} | Продано: {item['total_quantity']:5} | "
                  f"Выручка: {item['total_revenue']:>12.2f}")
        
        return result
    
    def payment_method_stats(self) -> List[Dict[str, Any]]:
        """
        Статистика по способам оплаты.
        
        Returns:
            List[Dict]: Статистика
        """
        print("\n📊 Статистика по способам оплаты:")
        print("-" * 60)
        
        pipeline = [
            {
                "$group": {
                    "_id": "$payment.method",
                    "count": {"$sum": 1},
                    "total_amount": {"$sum": "$payment.amount"},
                    "success_rate": {
                        "$avg": {
                            "$cond": [
                                {"$eq": ["$payment.status", "completed"]},
                                1,
                                0
                            ]
                        }
                    }
                }
            },
            {
                "$project": {
                    "_id": 0,
                    "method": "$_id",
                    "count": 1,
                    "total_amount": {"$round": ["$total_amount", 2]},
                    "success_rate": {"$round": [{"$multiply": ["$success_rate", 100]}, 1]}
                }
            },
            {"$sort": {"count": -1}}
        ]
        
        result = list(self.collection.aggregate(pipeline))
        
        for item in result:
            print(f"  {item['method']:10} | Заказы: {item['count']:4} | "
                  f"Сумма: {item['total_amount']:>12.2f} | "
                  f"Успешных: {item['success_rate']:5.1f}%")
        
        return result
    
    def monthly_trend(self) -> List[Dict[str, Any]]:
        """
        Месячная динамика продаж.
        Использует индекс idx_order_date_desc.
        
        Returns:
            List[Dict]: Динамика по месяцам
        """
        print("\n📊 Месячная динамика продаж:")
        print("-" * 60)
        
        pipeline = [
            {
                "$group": {
                    "_id": {
                        "year": {"$year": "$order_date"},
                        "month": {"$month": "$order_date"}
                    },
                    "order_count": {"$sum": 1},
                    "total_revenue": {"$sum": "$final_amount"},
                    "unique_customers": {"$addToSet": "$customer.customer_id"}
                }
            },
            {
                "$addFields": {
                    "unique_customers_count": {"$size": "$unique_customers"}
                }
            },
            {
                "$sort": {
                    "_id.year": -1,
                    "_id.month": -1
                }
            },
            {
                "$limit": 12
            },
            {
                "$project": {
                    "_id": 0,
                    "year": "$_id.year",
                    "month": "$_id.month",
                    "order_count": 1,
                    "total_revenue": {"$round": ["$total_revenue", 2]},
                    "unique_customers": "$unique_customers_count"
                }
            }
        ]
        
        result = list(self.collection.aggregate(pipeline))
        
        month_names = [
            'Янв', 'Фев', 'Мар', 'Апр', 'Май', 'Июн',
            'Июл', 'Авг', 'Сен', 'Окт', 'Ноя', 'Дек'
        ]
        
        for item in result:
            month_name = month_names[item['month'] - 1]
            print(f"  {month_name} {item['year']} | Заказы: {item['order_count']:4} | "
                  f"Клиенты: {item['unique_customers']:3} | "
                  f"Выручка: {item['total_revenue']:>10.2f}")
        
        return result
    
    def top_customers(self, limit: int = 10) -> List[Dict[str, Any]]:
        """
        Топ клиентов по сумме заказов.
        Использует индекс idx_customer_id.
        
        Args:
            limit: Количество клиентов в топе
            
        Returns:
            List[Dict]: Топ клиентов
        """
        print(f"\n📊 Топ {limit} клиентов по сумме заказов:")
        print("-" * 60)
        
        pipeline = [
            {
                "$group": {
                    "_id": "$customer.customer_id",
                    "customer_name": {"$first": "$customer.name"},
                    "city": {"$first": "$customer.address.city"},
                    "total_orders": {"$sum": 1},
                    "total_spent": {"$sum": "$final_amount"},
                    "avg_order_value": {"$avg": "$final_amount"}
                }
            },
            {
                "$sort": {"total_spent": -1}
            },
            {"$limit": limit},
            {
                "$project": {
                    "_id": 0,
                    "customer_id": "$_id",
                    "customer_name": 1,
                    "city": 1,
                    "total_orders": 1,
                    "total_spent": {"$round": ["$total_spent", 2]},
                    "avg_order_value": {"$round": ["$avg_order_value", 2]}
                }
            }
        ]
        
        result = list(self.collection.aggregate(pipeline))
        
        for i, item in enumerate(result, 1):
            print(f"  {i:2}. {item['customer_name']:25} | "
                  f"Заказы: {item['total_orders']:2} | "
                  f"Потрачено: {item['total_spent']:>10.2f} | "
                  f"Средний: {item['avg_order_value']:>8.2f}")
        
        return result
    
    def shipping_stats(self) -> List[Dict[str, Any]]:
        """
        Статистика по способам доставки.
        
        Returns:
            List[Dict]: Статистика
        """
        print("\n📊 Статистика по способам доставки:")
        print("-" * 60)
        
        pipeline = [
            {
                "$group": {
                    "_id": "$shipping.method",
                    "count": {"$sum": 1},
                    "delivered": {
                        "$sum": {
                            "$cond": [
                                {"$eq": ["$shipping.status", "delivered"]},
                                1,
                                0
                            ]
                        }
                    }
                }
            },
            {
                "$addFields": {
                    "delivery_rate": {
                        "$cond": [
                            {"$eq": ["$count", 0]},
                            0,
                            {"$divide": ["$delivered", "$count"]}
                        ]
                    }
                }
            },
            {
                "$project": {
                    "_id": 0,
                    "method": "$_id",
                    "count": 1,
                    "delivered": 1,
                    "delivery_rate": {"$round": [{"$multiply": ["$delivery_rate", 100]}, 1]}
                }
            },
            {"$sort": {"count": -1}}
        ]
        
        result = list(self.collection.aggregate(pipeline))
        
        for item in result:
            print(f"  {item['method']:10} | Заказы: {item['count']:4} | "
                  f"Доставлено: {item['delivered']:4} | "
                  f"Успешность: {item['delivery_rate']:5.1f}%")
        
        return result
    
    def run_all_analytics(self):
        """
        Запуск всех аналитических запросов.
        """
        print("=" * 70)
        print("📊 АГРЕГАЦИОННЫЕ АНАЛИТИЧЕСКИЕ ЗАПРОСЫ")
        print("=" * 70)
        
        self.total_revenue_by_status()
        self.revenue_by_city()
        self.sales_by_category()
        self.payment_method_stats()
        self.monthly_trend()
        self.top_customers()
        self.shipping_stats()
        
        print("\n" + "=" * 70)
        print("✅ Все аналитические запросы выполнены!")
        print("=" * 70)