-- ==================== СОЗДАНИЕ ПОЛЬЗОВАТЕЛЯ С ОГРАНИЧЕННЫМИ ПРАВАМИ ====================

-- 1. Создаём пользователя (роли)
CREATE USER app_user WITH PASSWORD 'secure_password_123';

-- 2. Предоставляем подключение к базе данных
GRANT CONNECT ON DATABASE test_db TO app_user;

-- 3. Предоставляем права на схему public
GRANT USAGE ON SCHEMA public TO app_user;

-- 4. Предоставляем права только на SELECT, INSERT, UPDATE (без DELETE и DROP)
GRANT SELECT, INSERT, UPDATE ON ALL TABLES IN SCHEMA public TO app_user;

-- 5. Предоставляем права на последовательности (для автоинкремента)
GRANT USAGE, SELECT ON ALL SEQUENCES IN SCHEMA public TO app_user;

-- 6. Запрещаем создание таблиц
REVOKE CREATE ON SCHEMA public FROM app_user;

-- 7. Запрещаем удаление таблиц (явно)
REVOKE DROP ON ALL TABLES IN SCHEMA public FROM app_user;

-- 8. Запрещаем изменение структуры таблиц
REVOKE ALTER ON ALL TABLES IN SCHEMA public FROM app_user;

-- 9. Для будущих таблиц создаём DEFAULT PRIVILEGES
ALTER DEFAULT PRIVILEGES IN SCHEMA public 
    GRANT SELECT, INSERT, UPDATE ON TABLES TO app_user;

ALTER DEFAULT PRIVILEGES IN SCHEMA public 
    GRANT USAGE, SELECT ON SEQUENCES TO app_user;

-- ==================== ПРОВЕРКА ПРАВ ====================

-- Просмотр прав пользователя
SELECT 
    grantee,
    table_name,
    privilege_type
FROM information_schema.role_table_grants
WHERE grantee = 'app_user';

-- ==================== ПРИМЕР СОЗДАНИЯ ТАБЛИЦ ДЛЯ ТЕСТИРОВАНИЯ ====================

CREATE TABLE users (
    id SERIAL PRIMARY KEY,
    username VARCHAR(50) NOT NULL,
    email VARCHAR(100) UNIQUE NOT NULL,
    password_hash VARCHAR(255) NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE products (
    id SERIAL PRIMARY KEY,
    name VARCHAR(100) NOT NULL,
    price DECIMAL(10, 2) NOT NULL,
    stock INTEGER DEFAULT 0
);

-- Вставка тестовых данных
INSERT INTO users (username, email, password_hash) VALUES
    ('alice', 'alice@example.com', 'hash123'),
    ('bob', 'bob@example.com', 'hash456');

INSERT INTO products (name, price, stock) VALUES
    ('Laptop', 999.99, 10),
    ('Mouse', 25.50, 50);

-- Предоставление прав на новые таблицы
GRANT SELECT, INSERT, UPDATE ON users TO app_user;
GRANT SELECT, INSERT, UPDATE ON products TO app_user;
GRANT USAGE, SELECT ON SEQUENCE users_id_seq TO app_user;
GRANT USAGE, SELECT ON SEQUENCE products_id_seq TO app_user;