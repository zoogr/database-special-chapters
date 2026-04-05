import psycopg2
from psycopg2 import sql
from sqlalchemy import create_engine, text
import getpass

class SQLInjectionDemo:
    def __init__(self, db_config):
        self.db_config = db_config
        
    def get_connection(self):
        """Получение подключения к БД"""
        return psycopg2.connect(**self.db_config)
    
    # ==================== УЯЗВИМЫЙ КОД ====================
    
    def vulnerable_login(self, username, password):
        """
        ❌ УЯЗВИМАЯ функция - SQL Injection через конкатенацию
        """
        conn = self.get_connection()
        cursor = conn.cursor()
        
        # УЯЗВИМОСТЬ: конкатенация строк
        query = f"SELECT * FROM users WHERE username='{username}' AND password='{password}'"
        
        print(f"❌ Уязвимый запрос: {query}")
        cursor.execute(query)
        result = cursor.fetchall()
        
        cursor.close()
        conn.close()
        return result
    
    def vulnerable_search_users(self, user_id):
        """
        ❌ УЯЗВИМАЯ функция - SQL Injection через форматирование
        """
        conn = self.get_connection()
        cursor = conn.cursor()
        
        # УЯЗВИМОСТЬ: использование % форматирования
        query = "SELECT * FROM users WHERE id = %s" % user_id
        
        print(f"❌ Уязвимый запрос: {query}")
        cursor.execute(query)
        result = cursor.fetchall()
        
        cursor.close()
        conn.close()
        return result
    
    def vulnerable_delete_table(self, table_name):
        """
        ❌ УЯЗВИМАЯ функция - возможность удаления таблицы
        """
        conn = self.get_connection()
        cursor = conn.cursor()
        
        # УЯЗВИМОСТЬ: прямая подстановка имени таблицы
        query = f"DROP TABLE {table_name}"
        
        print(f"❌ Уязвимый запрос: {query}")
        cursor.execute(query)
        conn.commit()
        
        cursor.close()
        conn.close()
    
    # ==================== ЗАЩИЩЁННЫЙ КОД ====================
    
    def safe_login(self, username, password):
        """
        ✅ БЕЗОПАСНАЯ функция - параметризованный запрос
        """
        conn = self.get_connection()
        cursor = conn.cursor()
        
        # БЕЗОПАСНОСТЬ: параметризация запроса
        query = "SELECT * FROM users WHERE username=%s AND password=%s"
        
        print(f"✅ Безопасный запрос: {query}")
        print(f"   Параметры: username={username}, password=***")
        
        cursor.execute(query, (username, password))
        result = cursor.fetchall()
        
        cursor.close()
        conn.close()
        return result
    
    def safe_search_users(self, user_id):
        """
        ✅ БЕЗОПАСНАЯ функция - параметризованный запрос
        """
        conn = self.get_connection()
        cursor = conn.cursor()
        
        # БЕЗОПАСНОСТЬ: использование параметра
        query = "SELECT * FROM users WHERE id = %s"
        
        print(f"✅ Безопасный запрос: {query}")
        print(f"   Параметр: id={user_id}")
        
        cursor.execute(query, (user_id,))
        result = cursor.fetchall()
        
        cursor.close()
        conn.close()
        return result
    
    def safe_delete_table(self, table_name):
        """
        ✅ БЕЗОПАСНАЯ функция - экранирование идентификаторов
        """
        conn = self.get_connection()
        cursor = conn.cursor()
        
        # БЕЗОПАСНОСТЬ: использование sql.Identifier для экранирования
        query = sql.SQL("DROP TABLE {}").format(sql.Identifier(table_name))
        
        print(f"✅ Безопасный запрос: {query.as_string(conn)}")
        
        cursor.execute(query)
        conn.commit()
        
        cursor.close()
        conn.close()
    
    # ==================== SQLALCHEMY ВЕРСИЯ ====================
    
    def sqlalchemy_vulnerable(self, username):
        """
        ❌ УЯЗВИМЫЙ код через SQLAlchemy
        """
        engine = create_engine(f"postgresql://{self.db_config['user']}:{self.db_config['password']}@{self.db_config['host']}/{self.db_config['database']}")
        
        # УЯЗВИМОСТЬ: f-string в запросе
        query = f"SELECT * FROM users WHERE username='{username}'"
        
        print(f"❌ SQLAlchemy уязвимый: {query}")
        
        with engine.connect() as conn:
            result = conn.execute(text(query))
            return result.fetchall()
    
    def sqlalchemy_safe(self, username):
        """
        ✅ БЕЗОПАСНЫЙ код через SQLAlchemy
        """
        engine = create_engine(f"postgresql://{self.db_config['user']}:{self.db_config['password']}@{self.db_config['host']}/{self.db_config['database']}")
        
        # БЕЗОПАСНОСТЬ: параметризованный запрос
        query = text("SELECT * FROM users WHERE username=:username")
        
        print(f"✅ SQLAlchemy безопасный: {query}")
        
        with engine.connect() as conn:
            result = conn.execute(query, {"username": username})
            return result.fetchall()


# ==================== ДЕМО АТАКИ ====================

def demonstrate_sql_injection():
    """Демонстрация SQL Injection атак"""
    
    db_config = {
        'host': 'localhost',
        'database': 'test_db',
        'user': 'postgres',
        'password': 'postgres'
    }
    
    demo = SQLInjectionDemo(db_config)
    
    print("=" * 60)
    print("ДЕМОНСТРАЦИЯ SQL INJECTION")
    print("=" * 60)
    
    # Атака 1: Обход аутентификации
    print("\n📌 Атака 1: Обход аутентификации")
    print("-" * 60)
    
    malicious_username = "admin' OR '1'='1"
    malicious_password = "' OR '1'='1"
    
    print(f"Ввод злоумышленника:")
    print(f"  Username: {malicious_username}")
    print(f"  Password: {malicious_password}")
    
    print("\n❌ Уязвимая функция:")
    try:
        result = demo.vulnerable_login(malicious_username, malicious_password)
        print(f"   Результат: УСПЕХ! Получено записей: {len(result)}")
    except Exception as e:
        print(f"   Ошибка: {e}")
    
    print("\n✅ Защищённая функция:")
    try:
        result = demo.safe_login(malicious_username, malicious_password)
        print(f"   Результат: {len(result)} записей (атака заблокирована)")
    except Exception as e:
        print(f"   Ошибка: {e}")
    
    # Атака 2: Удаление таблицы
    print("\n📌 Атака 2: Удаление таблицы")
    print("-" * 60)
    
    malicious_input = "users; DROP TABLE users; --"
    
    print(f"Ввод злоумышленника: {malicious_input}")
    
    print("\n❌ Уязвимая функция:")
    print(f"   Выполнит: DROP TABLE users")
    
    print("\n✅ Защищённая функция:")
    print(f"   Будет искать таблицу с именем 'users; DROP TABLE users; --'")
    print(f"   (атака заблокирована)")


if __name__ == "__main__":
    demonstrate_sql_injection()