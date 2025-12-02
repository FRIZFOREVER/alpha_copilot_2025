#!/usr/bin/env python3
import os
import sys
import uuid
import random
from datetime import datetime, timedelta
import psycopg2
from dateutil import parser

# Конфигурация подключения к БД
DB_CONFIG = {
    "host": "postgres",
    "database": "app",
    "user": "app",
    "password": "app123",
    "port": "5432"
}

# Новые теги из файла
TAGS = [
    "general",
    "finance",
    "law",
    "marketing",
    "management"
]

def generate_test_data(start_date: datetime, end_date: datetime, 
                       user_login: str, user_password: str) -> None:
    """Генерация тестовых данных"""
    
    conn = None
    try:
        # Подключение к БД
        print("Подключаемся к базе данных...")
        conn = psycopg2.connect(**DB_CONFIG)
        cursor = conn.cursor()
        
        # Проверяем существование таблиц
        cursor.execute("SELECT EXISTS (SELECT FROM information_schema.tables WHERE table_name = 'users')")
        if not cursor.fetchone()[0]:
            print("Ошибка: Таблицы не существуют. Убедитесь, что миграции выполнены.")
            return
        
        # Проверяем существование расширения pgcrypto
        cursor.execute("SELECT EXISTS (SELECT 1 FROM pg_extension WHERE extname = 'pgcrypto')")
        if not cursor.fetchone()[0]:
            print("Устанавливаем расширение pgcrypto...")
            cursor.execute("CREATE EXTENSION IF NOT EXISTS pgcrypto")
            conn.commit()
        
        # Генерируем bcrypt хеш пароля с использованием PostgreSQL crypt()
        print(f"Генерируем bcrypt хеш для пароля '{user_password}' с помощью PostgreSQL crypt()...")
        cursor.execute("SELECT crypt(%s, gen_salt('bf', 12))", (user_password,))
        password_hash = cursor.fetchone()[0]
        
        # 1. Создание мокового пользователя
        print(f"Создаем мокового пользователя с логином '{user_login}'...")
        user_uuid = str(uuid.uuid4())
        cursor.execute("""
            INSERT INTO users (uuid, fio, login, password_hash, user_info, business_info, additional_instructions)
            VALUES (%s, %s, %s, %s, %s, %s, %s)
            RETURNING id
        """, (
            user_uuid,
            "Тестовый Пользователь",
            user_login,
            password_hash,
            "Тестовая информация о пользователе",
            "Тестовая бизнес информация",
            "Дополнительные инструкции"
        ))
        user_id = cursor.fetchone()[0]
        
        # Проверяем, что пароль работает
        cursor.execute("""
            SELECT uuid 
            FROM users 
            WHERE login = %s
            AND password_hash = crypt(%s, password_hash)
        """, (user_login, user_password))
        result = cursor.fetchone()
        
        if result:
            print(f"✓ Проверка пароля успешна. UUID пользователя: {result[0]}")
        else:
            print("✗ Ошибка: Проверка пароля не удалась!")
            conn.rollback()
            sys.exit(1)
        
        # 2. Создание чата для пользователя
        print("Создаем чат...")
        cursor.execute("""
            INSERT INTO chats (name, user_id, create_date)
            VALUES (%s, %s, %s)
            RETURNING id
        """, ("Основной чат", user_id, start_date))
        chat_id = cursor.fetchone()[0]
        
        # 3. Генерация данных по дням
        print("Генерируем вопросы и ответы...")
        current_date = start_date
        total_questions = 0
        total_answers = 0
        tag_distribution = {tag: 0 for tag in TAGS}
        tag_distribution[None] = 0  # Вопросы без тега
        
        while current_date <= end_date:
            # Случайное количество вопросов и ответов от 0 до 50
            num_items = random.randint(0, 50)
            
            for _ in range(num_items):
                # Случайное время в течение дня
                random_hour = random.randint(0, 23)
                random_minute = random.randint(0, 59)
                random_second = random.randint(0, 59)
                
                question_time = current_date.replace(
                    hour=random_hour,
                    minute=random_minute,
                    second=random_second
                )
                
                # Создаем ответ
                answer_time = question_time + timedelta(seconds=random.randint(10, 300))
                
                # 30% вероятности наличия file_url в ответе
                answer_file_url = "" if random.random() < 0.3 else None
                
                cursor.execute("""
                    INSERT INTO answers (time_utc, message, visible, chat_id, rating, file_url)
                    VALUES (%s, %s, %s, %s, %s, %s)
                    RETURNING answer_id
                """, (
                    answer_time,
                    f"Ответ на вопрос от {question_time.strftime('%Y-%m-%d %H:%M:%S')}",
                    True,
                    chat_id,
                    random.randint(1, 5) if random.random() < 0.7 else None,
                    answer_file_url
                ))
                answer_id = cursor.fetchone()[0]
                
                # Выбираем случайный тег (с вероятностью 40% что тег будет, 60% что None)
                selected_tag = random.choice(TAGS) if random.random() < 0.4 else None
                if selected_tag:
                    tag_distribution[selected_tag] += 1
                else:
                    tag_distribution[None] += 1
                
                # Создаем вопрос, связанный с ответом
                cursor.execute("""
                    INSERT INTO questions (time_utc, message, visible, chat_id, answer_id, 
                                          voice_url, file_url, tag)
                    VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
                """, (
                    question_time,
                    f"Вопрос от {question_time.strftime('%Y-%m-%d %H:%M:%S')}",
                    True,
                    chat_id,
                    answer_id,
                    f"https://example.com/voice/{random.randint(1000, 9999)}.mp3" if random.random() < 0.5 else None,
                    f"https://example.com/file/{random.randint(1000, 9999)}.pdf" if random.random() < 0.4 else None,
                    selected_tag
                ))
                
                total_answers += 1
                total_questions += 1
            
            # Переход к следующему дню
            current_date += timedelta(days=1)
            
            # Прогресс
            if (current_date - start_date).days % 7 == 0 or current_date > end_date:
                days_processed = min((current_date - start_date).days, (end_date - start_date).days + 1)
                print(f"Обработано дней: {days_processed}")
        
        # 4. Создание нескольких записей в supports
        print("Создаем обращения в поддержку...")
        for i in range(1, 6):
            support_date = start_date + timedelta(days=random.randint(0, (end_date - start_date).days))
            cursor.execute("""
                INSERT INTO supports (message, user_id, chat_id, create_date)
                VALUES (%s, %s, %s, %s)
            """, (
                f"Обращение в поддержку #{i} от пользователя {user_id}",
                user_id,
                chat_id,
                support_date
            ))
        
        # Фиксация изменений
        conn.commit()
        
        print("\n" + "="*50)
        print("Генерация данных завершена успешно!")
        print(f"Период: {start_date.strftime('%Y-%m-%d')} - {end_date.strftime('%Y-%m-%d')}")
        print(f"Создано пользователей: 1")
        print(f"Логин пользователя: {user_login}")
        print(f"Пароль пользователя: {user_password}")
        print(f"Хеш пароля: {password_hash[:20]}...")  # Показываем только начало хеша
        print(f"Создано чатов: 1")
        print(f"Создано вопросов: {total_questions}")
        print(f"Создано ответов: {total_answers}")
        print(f"Создано обращений в поддержку: 5")
        
        # Статистика по тегам
        print("\nРаспределение вопросов по тегам:")
        print("-" * 30)
        for tag, count in tag_distribution.items():
            tag_name = "без тега" if tag is None else tag
            print(f"{tag_name}: {count} вопросов")
        
        print("="*50)
        
        # Тестируем аутентификацию
        print("\nТестирование аутентификации:")
        cursor.execute("""
            SELECT uuid, fio 
            FROM users 
            WHERE login = %s
            AND password_hash = crypt(%s, password_hash)
        """, (user_login, user_password))
        test_user = cursor.fetchone()
        
        if test_user:
            print(f"✓ Аутентификация успешна!")
            print(f"  UUID: {test_user[0]}")
            print(f"  ФИО: {test_user[1]}")
        else:
            print("✗ Ошибка аутентификации!")
        
        # Показываем примеры вопросов с разными тегами
        print("\nПримеры вопросов с тегами:")
        cursor.execute("""
            SELECT tag, message 
            FROM questions 
            WHERE tag IS NOT NULL 
            ORDER BY RANDOM() 
            LIMIT 5
        """)
        examples = cursor.fetchall()
        
        for tag, message in examples:
            print(f"  [{tag}] {message[:50]}...")
        
    except psycopg2.OperationalError as e:
        print(f"Ошибка подключения к базе данных: {e}")
        print("Убедитесь, что сервер PostgreSQL запущен и доступен")
        sys.exit(1)
    except Exception as e:
        print(f"Ошибка: {e}")
        if conn:
            conn.rollback()
        sys.exit(1)
    finally:
        if conn:
            cursor.close()
            conn.close()

def wait_for_postgres() -> bool:
    """Ожидание готовности PostgreSQL"""
    import time
    
    print("Ожидаем готовности PostgreSQL...")
    max_attempts = 30
    for attempt in range(max_attempts):
        try:
            conn = psycopg2.connect(**DB_CONFIG)
            conn.close()
            print("PostgreSQL готов!")
            return True
        except psycopg2.OperationalError:
            if attempt < max_attempts - 1:
                print(f"Попытка {attempt + 1}/{max_attempts}...")
                time.sleep(2)
    return False

def main():
    """Основная функция"""
    print("\n" + "="*50)
    print("Генератор тестовых данных для базы данных")
    print("Доступные теги: " + ", ".join(TAGS))
    print("="*50)
    
    # Получаем переменные окружения
    auto_start = os.environ.get('AUTO_START', 'true').lower() == 'true'
    start_date_str = os.environ.get('START_DATE', '2024-01-01')
    end_date_str = os.environ.get('END_DATE', '2024-12-31')
    user_login = os.environ.get('SEED_USER_LOGIN', 'test_user')
    user_password = os.environ.get('SEED_USER_PASSWORD', 'test_password_123')
    
    if not auto_start:
        print("Предупреждение: AUTO_START=false, но интерактивный режим отключен.")
        print("Используется автоматический режим с параметрами из переменных окружения.")
    
    try:
        start_date = parser.parse(start_date_str)
        end_date = parser.parse(end_date_str)
        
        print(f"\nПараметры генерации:")
        print(f"START_DATE: {start_date.strftime('%Y-%m-%d')}")
        print(f"END_DATE: {end_date.strftime('%Y-%m-%d')}")
        print(f"Логин пользователя: {user_login}")
        print(f"Пароль пользователя: {user_password}")
        print(f"Всего дней: {(end_date - start_date).days + 1}")
        print(f"Генерация начинается через 3 секунды...")
        print("(Нажмите Ctrl+C для отмены)")
        
        # Небольшая задержка для визуального подтверждения
        import time
        time.sleep(3)
        
        if not wait_for_postgres():
            print("Не удалось подключиться к PostgreSQL")
            sys.exit(1)
        
        generate_test_data(start_date, end_date, user_login, user_password)
        
    except KeyboardInterrupt:
        print("\n\nПрограмма прервана пользователем")
        sys.exit(0)
    except Exception as e:
        print(f"Ошибка при генерации: {e}")
        print("Проверьте формат дат в переменных окружения (YYYY-MM-DD)")
        sys.exit(1)

if __name__ == "__main__":
    main()