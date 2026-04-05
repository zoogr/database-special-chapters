"""
Основной файл для демонстрации работы с MongoDB.
"""

from config import get_database
from models import OrderCollection
from aggregations import AggregationQueries


def main():
    """
    Основная функция.
    """
    print("=" * 70)
    print("MONGODB TASK: Работа с PyMongo")
    print("=" * 70)
    
    try:
        # Получение базы данных
        db = get_database()
        print(f"\n✅ Подключено к базе данных: {db.name}")
        
        # Создание объекта для работы с коллекцией
        orders = OrderCollection(db)
        
        # Создание индексов
        orders.create_indexes()
        
        # Вставка тестовых данных
        orders.insert_sample_data(num_records=1000)
        
        # Демонстрация CRUD операций
        print("\n" + "=" * 70)
        print("📝 CRUD ОПЕРАЦИИ")
        print("=" * 70)
        
        # Создание заказа
        sample_order = orders.generate_sample_order(9999)
        order_id = orders.create_order(sample_order)
        
        # Поиск заказа
        if order_id:
            found_order = orders.get_order_by_number(sample_order["order_number"])
            if found_order:
                print(f"\n✅ Найден заказ: {found_order['order_number']}")
                print(f"   Клиент: {found_order['customer']['name']}")
                print(f"   Сумма: {found_order['final_amount']}")
        
        # Обновление статуса
        orders.update_order_status(sample_order["order_number"], "processing")
        
        # Получение заказов клиента
        customer_id = sample_order["customer"]["customer_id"]
        customer_orders = orders.get_orders_by_customer(customer_id)
        print(f"\n📋 Заказов у клиента {customer_id}: {len(customer_orders)}")
        
        # Удаление заказа
        orders.delete_order(sample_order["order_number"])
        
        # Агрегационные запросы
        analytics = AggregationQueries(orders.collection)
        analytics.run_all_analytics()
        
        # Статистика коллекции
        print("\n📊 СТАТИСТИКА КОЛЛЕКЦИИ")
        print("-" * 70)
        total_orders = orders.collection.count_documents({})
        print(f"Общее количество заказов: {total_orders}")
        
        # Информация об индексах
        print("\n📎 ИНДЕКСЫ В КОЛЛЕКЦИИ:")
        print("-" * 70)
        indexes = orders.collection.list_indexes()
        for idx in indexes:
            print(f"  • {idx['name']}: {dict(idx['key'])}")
        
        print("\n" + "=" * 70)
        print("✅ Задание выполнено успешно!")
        print("=" * 70)
        print("\n💡 Откройте MongoDB Compass для визуального просмотра данных")
        print("   Подключение: mongodb://localhost:27017/ecommerce_db")
        
    except Exception as e:
        print(f"\n❌ Ошибка: {e}")
        print("💡 Убедитесь, что MongoDB запущен")
        raise


if __name__ == "__main__":
    main()