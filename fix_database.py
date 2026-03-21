import sqlite3
import json

DB_NAME = "bot_database.db"

def fix_database():
    conn = sqlite3.connect(DB_NAME)
    cur = conn.cursor()
    
    # Получаем всех пользователей
    cur.execute("SELECT user_id, state, temp_data FROM users")
    rows = cur.fetchall()
    
    for row in rows:
        user_id, state, temp_data = row
        
        # Проверяем temp_data
        if temp_data and temp_data != "":
            try:
                # Пытаемся распарсить JSON
                json.loads(temp_data)
            except json.JSONDecodeError:
                # Если невалидный, очищаем
                print(f"Очищаю temp_data для пользователя {user_id}")
                cur.execute("UPDATE users SET temp_data = '', state = 'main' WHERE user_id = ?", (user_id,))
        else:
            # Если пусто, но состояние не main - сбрасываем
            if state != "main":
                print(f"Сбрасываю состояние пользователя {user_id} с {state} на main")
                cur.execute("UPDATE users SET state = 'main' WHERE user_id = ?", (user_id,))
    
    conn.commit()
    conn.close()
    print("База данных исправлена")

if __name__ == "__main__":
    fix_database()