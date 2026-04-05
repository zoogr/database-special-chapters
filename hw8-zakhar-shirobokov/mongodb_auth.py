from pymongo import MongoClient, errors
import sys

class MongoDBAuthManager:
    """Управление аутентификацией и правами MongoDB через Python"""
    
    def __init__(self, host="localhost", port=27017):
        self.host = host
        self.port = port
        self.admin_uri = f"mongodb://admin:SuperSecretAdmin123!@{host}:{port}/?authSource=admin"
    
    def get_client(self, username=None, password=None, db="admin", auth_source="admin"):
        """Создание клиента с/без аутентификации"""
        if username and password:
            uri = f"mongodb://{username}:{password}@{self.host}:{self.port}/{db}?authSource={auth_source}"
        else:
            uri = f"mongodb://{self.host}:{self.port}/"
            
        try:
            client = MongoClient(uri, serverSelectionTimeoutMS=3000)
            client.admin.command('ping')  # Проверка подключения
            return client
        except errors.ServerSelectionTimeoutError:
            print(f"❌ Не удалось подключиться к MongoDB {self.host}:{self.port}")
            sys.exit(1)
        except errors.OperationFailure as e:
            print(f"❌ Ошибка аутентификации: {e}")
            return None

    def setup_initial_admin(self):
        """
        Создаёт root-администратора.
        ⚠️ Запускать только ПЕРВЫЙ раз, когда в MongoDB ещё нет пользователей!
        """
        print("🔧 Создание root-администратора...")
        # Подключаемся без пароля (MongoDB разрешает это до создания первого пользователя)
        client = self.get_client()
        admin_db = client.admin
        
        # Создаём пользователя root
        admin_db.command(
            "createUser",
            "admin",
            pwd="SuperSecretAdmin123!",
            roles=[{"role": "root", "db": "admin"}]
        )
        print("✅ Root-администратор создан")
        client.close()

    def create_application_users(self):
        """Создаёт пользователей приложения с разными ролями"""
        print("\n👥 Создание пользователей приложения...")
        client = self.get_client(username="admin", password="SuperSecretAdmin123!")
        if not client:
            return
        
        admin_db = client.admin
        
        # 1. Пользователь для приложения (чтение + запись в свою БД)
        admin_db.command(
            "createUser",
            "app_user",
            pwd="AppUserPass123!",
            roles=[
                {"role": "readWrite", "db": "myapp_db"},
                {"role": "dbAdmin", "db": "myapp_db"}
            ]
        )
        print("   ✅ Создан: app_user (readWrite + dbAdmin на myapp_db)")
        
        # 2. Пользователь только для чтения
        admin_db.command(
            "createUser",
            "readonly_user",
            pwd="ReadOnlyPass123!",
            roles=[
                {"role": "read", "db": "myapp_db"}
            ]
        )
        print("   ✅ Создан: readonly_user (только чтение myapp_db)")
        
        # 3. Пользователь для мониторинга (без доступа к данным)
        admin_db.command(
            "createUser",
            "monitor_user",
            pwd="MonitorPass123!",
            roles=[
                {"role": "clusterMonitor", "db": "admin"},
                {"role": "read", "db": "myapp_db"}
            ]
        )
        print("   ✅ Создан: monitor_user (clusterMonitor + read)")
        
        client.close()

    def test_authentication(self):
        """Тестирование аутентификации и прав доступа"""
        print("\n Тестирование аутентификации и прав:")
        print("=" * 60)
        
        test_cases = [
            {
                "name": "app_user",
                "password": "AppUserPass123!",
                "db": "myapp_db",
                "auth_source": "admin",
                "expected_write": True,
                "expected_read": True
            },
            {
                "name": "readonly_user",
                "password": "ReadOnlyPass123!",
                "db": "myapp_db",
                "auth_source": "admin",
                "expected_write": False,
                "expected_read": True
            },
            {
                "name": "monitor_user",
                "password": "MonitorPass123!",
                "db": "myapp_db",
                "auth_source": "admin",
                "expected_write": False,
                "expected_read": True
            },
            {
                "name": "wrong_user",
                "password": "WrongPass123!",
                "db": "myapp_db",
                "auth_source": "admin",
                "expected_write": False,
                "expected_read": False
            }
        ]
        
        for test in test_cases:
            print(f"\n📌 Тест: {test['name']}")
            print("-" * 40)
            
            client = self.get_client(
                username=test["name"],
                password=test["password"],
                db=test["db"],
                auth_source=test["auth_source"]
            )
            
            if not client:
                print("   ❌ Аутентификация не пройдена")
                continue
                
            db = client[test["db"]]
            
            # Тест записи
            if test["expected_write"]:
                try:
                    db.test_collection.insert_one({"user": test["name"], "test": "write"})
                    print("   ✅ Запись: РАЗРЕШЕНА")
                except errors.OperationFailure as e:
                    print(f"   ❌ Запись: ЗАПРЕЩЕНА ({e.details.get('errmsg', 'Unknown')})")
            else:
                try:
                    db.test_collection.insert_one({"user": test["name"], "test": "write"})
                    print("   ⚠️  Запись: РАЗРЕШЕНА (ОШИБКА В ПРАВАХ!)")
                except errors.OperationFailure:
                    print("   ✅ Запись: ЗАПРЕЩЕНА")
            
            # Тест чтения
            if test["expected_read"]:
                try:
                    count = db.test_collection.count_documents({})
                    print(f"   ✅ Чтение: РАЗРЕШЕНО (документов: {count})")
                except errors.OperationFailure as e:
                    print(f"   ❌ Чтение: ЗАПРЕЩЕНО ({e.details.get('errmsg', 'Unknown')})")
            else:
                try:
                    db.test_collection.count_documents({})
                    print("   ⚠️  Чтение: РАЗРЕШЕНО (ОШИБКА В ПРАВАХ!)")
                except errors.OperationFailure:
                    print("   ✅ Чтение: ЗАПРЕЩЕНО")
            
            client.close()

    def cleanup(self):
        """Удаление тестовых пользователей (для отката)"""
        print("\n️  Очистка тестовых пользователей...")
        client = self.get_client(username="admin", password="SuperSecretAdmin123!")
        if not client:
            return
            
        admin_db = client.admin
        for user in ["app_user", "readonly_user", "monitor_user"]:
            try:
                admin_db.command("dropUser", user)
                print(f"   ✅ Удалён: {user}")
            except errors.OperationFailure:
                print(f"   ℹ️  Пользователь {user} не найден")
                
        client.close()


def main():
    print("=" * 60)
    print(" НАСТРОЙКА АУТЕНТИФИКАЦИИ MONGODB (Чистый Python)")
    print("=" * 60)
    
    manager = MongoDBAuthManager()
    
    # Меню выбора действия
    print("\nВыберите действие:")
    print("1. Создать root-администратора (только 1 раз!)")
    print("2. Создать пользователей приложения")
    print("3. Протестировать аутентификацию и права")
    print("4. Очистить тестовых пользователей")
    print("5. Запустить полный цикл (1 -> 2 -> 3)")
    
    choice = input("\nВведите номер (1-5): ").strip()
    
    if choice == "1":
        manager.setup_initial_admin()
    elif choice == "2":
        manager.create_application_users()
    elif choice == "3":
        manager.test_authentication()
    elif choice == "4":
        manager.cleanup()
    elif choice == "5":
        manager.setup_initial_admin()
        manager.create_application_users()
        manager.test_authentication()
    else:
        print("❌ Неверный выбор")


if __name__ == "__main__":
    main()