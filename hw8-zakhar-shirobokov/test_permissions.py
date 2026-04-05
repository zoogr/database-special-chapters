import psycopg2
from psycopg2 import OperationalError, ProgrammingError

def test_user_permissions():
    """Тестирование прав пользователя app_user"""
    
    print("=" * 60)
    print("ТЕСТИРОВАНИЕ ПРАВ ДОСТУПА ПОЛЬЗОВАТЕЛЯ")
    print("=" * 60)
    
    # Подключение от имени app_user
    config = {
        'host': 'localhost',
        'database': 'test_db',
        'user': 'app_user',
        'password': 'secure_password_123'
    }
    
    try:
        conn = psycopg2.connect(**config)
        cursor = conn.cursor()
        
        # ✅ Тест 1: SELECT (должен работать)
        print("\n✅ Тест 1: SELECT из таблицы users")
        try:
            cursor.execute("SELECT * FROM users")
            users = cursor.fetchall()
            print(f"   УСПЕХ! Получено записей: {len(users)}")
        except ProgrammingError as e:
            print(f"   ❌ ОШИБКА: {e}")
        
        # ✅ Тест 2: INSERT (должен работать)
        print("\n✅ Тест 2: INSERT в таблицу users")
        try:
            cursor.execute(
                "INSERT INTO users (username, email, password_hash) VALUES (%s, %s, %s)",
                ('test_user', 'test@example.com', 'hash789')
            )
            conn.commit()
            print("   УСПЕХ! Запись добавлена")
        except ProgrammingError as e:
            print(f"   ❌ ОШИБКА: {e}")
            conn.rollback()
        
        # ❌ Тест 3: DELETE (должен быть запрещён)
        print("\n❌ Тест 3: DELETE из таблицы users (должен быть запрещён)")
        try:
            cursor.execute("DELETE FROM users WHERE username='test_user'")
            conn.commit()
            print("   ⚠️  ВНИМАНИЕ: DELETE разрешили (это плохо!)")
        except ProgrammingError as e:
            print(f"   ✅ ЗАПРЕЩЕНО: {e.pgerror}")
            conn.rollback()
        
        # ❌ Тест 4: DROP TABLE (должен быть запрещён)
        print("\n❌ Тест 4: DROP TABLE users (должен быть запрещён)")
        try:
            cursor.execute("DROP TABLE users")
            conn.commit()
            print("   ⚠️  ВНИМАНИЕ: DROP TABLE разрешили (это критично!)")
        except ProgrammingError as e:
            print(f"   ✅ ЗАПРЕЩЕНО: {e.pgerror}")
            conn.rollback()
        
        # ❌ Тест 5: CREATE TABLE (должен быть запрещён)
        print("\n❌ Тест 5: CREATE TABLE (должен быть запрещён)")
        try:
            cursor.execute("CREATE TABLE test_table (id INT)")
            conn.commit()
            print("   ⚠️  ВНИМАНИЕ: CREATE TABLE разрешили")
        except ProgrammingError as e:
            print(f"   ✅ ЗАПРЕЩЕНО: {e.pgerror}")
            conn.rollback()
        
        # ✅ Тест 6: UPDATE (должен работать)
        print("\n✅ Тест 6: UPDATE таблицы users")
        try:
            cursor.execute(
                "UPDATE users SET email=%s WHERE username=%s",
                ('newemail@example.com', 'alice')
            )
            conn.commit()
            print("   УСПЕХ! Запись обновлена")
        except ProgrammingError as e:
            print(f"   ❌ ОШИБКА: {e}")
            conn.rollback()
        
        cursor.close()
        conn.close()
        
    except OperationalError as e:
        print(f"\n❌ Ошибка подключения: {e}")


if __name__ == "__main__":
    test_user_permissions()