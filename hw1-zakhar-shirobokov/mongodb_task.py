"""
Подключение к MongoDB и создание коллекции с тестовыми данными.
"""

from pymongo import MongoClient
from datetime import datetime, timedelta
from faker import Faker
import random

# Инициализация Faker для генерации реалистичных данных
fake = Faker('ru_RU')  # Русские данные
Faker.seed(42)  # Для воспроизводимости результатов


def connect_to_mongodb():
    """
    Подключение к локальной MongoDB.
    
    Returns:
        MongoClient: Клиент MongoDB
    """
    try:
        client = MongoClient('mongodb://localhost:27017/', 
                           serverSelectionTimeoutMS=5000)
        # Проверка подключения
        client.admin.command('ping')
        print("✅ Успешное подключение к MongoDB!")
        return client
    except Exception as e:
        print(f"❌ Ошибка подключения: {e}")
        print("💡 Убедитесь, что MongoDB запущен (docker-compose up -d)")
        raise


def generate_sample_data(num_records=100):
    """
    Генерация тестовых данных с разными типами полей.
    
    Args:
        num_records: Количество записей для генерации
        
    Returns:
        List[Dict]: Список словарей с данными
    """
    print(f"\n📝 Генерация {num_records} записей...")
    
    records = []
    categories = ['Электроника', 'Одежда', 'Продукты', 'Книги', 'Спорт']
    statuses = ['новый', 'в обработке', 'выполнен', 'отменен']
    
    for i in range(num_records):
        # Генерация случайной даты в прошлом году
        random_date = fake.date_time_between(start_date='-1y', end_date='now')
        
        record = {
            # Строковые поля
            'full_name': fake.name(),
            'email': fake.email(),
            'city': fake.city(),
            'address': fake.address(),
            'category': random.choice(categories),
            'status': random.choice(statuses),
            'description': fake.sentence(nb_words=10),
            
            # Числовые поля
            'age': random.randint(18, 70),
            'price': round(random.uniform(100, 10000), 2),
            'quantity': random.randint(1, 100),
            'rating': round(random.uniform(1.0, 5.0), 1),
            'discount_percent': random.randint(0, 30),
            
            # Дата и время
            'created_at': random_date,
            'updated_at': random_date + timedelta(days=random.randint(1, 30)),
            'birth_date': fake.date_of_birth(minimum_age=18, maximum_age=70),
            
            # Логические значения
            'is_active': random.choice([True, False]),
            'is_verified': random.choice([True, False]),
            'premium_member': random.choice([True, False]),
            
            # Вложенные данные (список)
            'tags': [fake.word() for _ in range(random.randint(2, 5))],
            'phone_numbers': [fake.phone_number() for _ in range(random.randint(1, 3))],
            
            # Вложенный документ
            'metadata': {
                'ip_address': fake.ipv4(),
                'user_agent': fake.user_agent(),
                'login_count': random.randint(1, 1000),
                'last_login': fake.date_time_this_year()
            },
            
            # Порядковый номер
            'record_number': i + 1,
            'generated_at': datetime.now()
        }
        
        records.append(record)
    
    print(f"✅ Сгенерировано {len(records)} записей")
    return records


def create_and_populate_collection(db, collection_name='sample_data', num_records=100):
    """
    Создание коллекции и заполнение данными.
    
    Args:
        db: База данных MongoDB
        collection_name: Имя коллекции
        num_records: Количество записей
    """
    # Удаление существующей коллекции (если есть)
    if collection_name in db.list_collection_names():
        print(f"\n🗑️  Удаление существующей коллекции '{collection_name}'...")
        db[collection_name].drop()
    
    # Создание новой коллекции
    print(f"\n📦 Создание коллекции '{collection_name}'...")
    collection = db[collection_name]
    
    # Генерация данных
    records = generate_sample_data(num_records)
    
    # Вставка данных
    print(f"\n💾 Вставка данных в коллекцию...")
    result = collection.insert_many(records)
    
    print(f"✅ Вставлено {len(result.inserted_ids)} документов")
    return collection


def display_collection_info(collection):
    """
    Вывод информации о коллекции.
    
    Args:
        collection: Коллекция MongoDB
    """
    print("\n" + "=" * 70)
    print("📊 ИНФОРМАЦИЯ О КОЛЛЕКЦИИ")
    print("=" * 70)
    
    # Общее количество записей
    total_count = collection.count_documents({})
    print(f"\n📈 Общее количество записей: {total_count}")
    
    # Пример одной записи
    print("\n📋 Пример одной записи:")
    print("-" * 70)
    sample_record = collection.find_one()
    
    if sample_record:
        # Красивый вывод с ограничением длины строк
        for key, value in sample_record.items():
            value_str = str(value)
            if len(value_str) > 60:
                value_str = value_str[:57] + "..."
            print(f"  {key:20} : {value_str}")
    
    # Статистика по полям
    print("\n📊 Статистика по полям:")
    print("-" * 70)
    
    # Примеры агрегаций
    avg_age = collection.aggregate([
        {"$group": {"_id": None, "average": {"$avg": "$age"}}}
    ]).next()['average']
    print(f"  Средний возраст: {avg_age:.1f}")
    
    avg_price = collection.aggregate([
        {"$group": {"_id": None, "average": {"$avg": "$price"}}}
    ]).next()['average']
    print(f"  Средняя цена: {avg_price:.2f}")
    
    # Количество активных
    active_count = collection.count_documents({"is_active": True})
    print(f"  Активных записей: {active_count} ({active_count/total_count*100:.1f}%)")
    
    # Распределение по категориям
    print("\n  Распределение по категориям:")
    category_stats = collection.aggregate([
        {"$group": {"_id": "$category", "count": {"$sum": 1}}},
        {"$sort": {"count": -1}}
    ])
    
    for stat in category_stats:
        print(f"    • {stat['_id']}: {stat['count']}")
    
    print("\n" + "=" * 70)


def main():
    """
    Основная функция выполнения задания.
    """
    print("=" * 70)
    print("ЗАДАНИЕ: Подключение к MongoDB и создание коллекции")
    print("=" * 70)
    
    try:
        # Шаг 1: Подключение
        client = connect_to_mongodb()
        
        # Шаг 2: Выбор/создание базы данных
        db = client['task_database']
        print(f"\n📁 База данных: {db.name}")
        
        # Шаг 3: Создание и заполнение коллекции
        collection = create_and_populate_collection(
            db, 
            collection_name='sample_data',
            num_records=100
        )
        
        # Шаг 4: Вывод информации
        display_collection_info(collection)
        
        # Шаг 5: Проверка типов данных
        print("\n📎 ТИПЫ ДАННЫХ В КОЛЛЕКЦИИ:")
        print("-" * 70)
        sample = collection.find_one()
        if sample:
            for key, value in list(sample.items())[:10]:  # Первые 10 полей
                print(f"  {key:25} : {type(value).__name__}")
        
        print("\n✅ Задание выполнено успешно!")
        print("\n💡 Откройте MongoDB Compass и подключитесь к mongodb://localhost:27017")
        
        # Закрытие соединения
        client.close()
        
    except Exception as e:
        print(f"\n❌ Произошла ошибка: {e}")
        raise


if __name__ == "__main__":
    main()