import sqlite3
import datetime
import json

DB_NAME = "bot_database.db"

def init_db():
    conn = sqlite3.connect(DB_NAME)
    cur = conn.cursor()
    cur.execute('''
        CREATE TABLE IF NOT EXISTS users (
            user_id INTEGER PRIMARY KEY,
            state TEXT,
            temp_data TEXT,
            quote_time TEXT,
            receive_quotes INTEGER DEFAULT 0,
            last_quote_date TEXT
        )
    ''')
    cur.execute('''
        CREATE TABLE IF NOT EXISTS psychologist_messages (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER,
            message TEXT,
            timestamp TEXT,
            is_anonymous INTEGER,
            contact TEXT,
            answered INTEGER DEFAULT 0,
            answer_text TEXT,
            answer_timestamp TEXT
        )
    ''')
    cur.execute('''
        CREATE TABLE IF NOT EXISTS reminders (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER,
            remind_time TEXT,
            action TEXT,
            data TEXT
        )
    ''')
    cur.execute('''
        CREATE TABLE IF NOT EXISTS plans (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER,
            plan_type TEXT,
            tasks TEXT,
            created_at TEXT
        )
    ''')
    conn.commit()
    conn.close()

def get_user(user_id):
    conn = sqlite3.connect(DB_NAME)
    cur = conn.cursor()
    cur.execute("SELECT state, temp_data, quote_time, receive_quotes, last_quote_date FROM users WHERE user_id = ?", (user_id,))
    row = cur.fetchone()
    conn.close()
    if row:
        temp_data = row[1]
        if temp_data is None or temp_data == "":
            temp_data = None
        return {
            "state": row[0] if row[0] is not None else "main",
            "temp_data": temp_data,
            "quote_time": row[2],
            "receive_quotes": row[3] if row[3] is not None else 0,
            "last_quote_date": row[4]
        }
    return None

def set_user(user_id, state=None, temp_data=None, quote_time=None, receive_quotes=None, last_quote_date=None):
    conn = sqlite3.connect(DB_NAME)
    cur = conn.cursor()
    existing = get_user(user_id)
    if existing:
        updates = []
        params = []
        if state is not None:
            updates.append("state = ?")
            params.append(state)
        if temp_data is not None:
            updates.append("temp_data = ?")
            params.append(temp_data)
        if quote_time is not None:
            updates.append("quote_time = ?")
            params.append(quote_time)
        if receive_quotes is not None:
            updates.append("receive_quotes = ?")
            params.append(receive_quotes)
        if last_quote_date is not None:
            updates.append("last_quote_date = ?")
            params.append(last_quote_date)
        if updates:
            params.append(user_id)
            cur.execute(f"UPDATE users SET {', '.join(updates)} WHERE user_id = ?", params)
    else:
        temp_data_value = temp_data if temp_data is not None else ""
        cur.execute(
            "INSERT INTO users (user_id, state, temp_data, quote_time, receive_quotes, last_quote_date) VALUES (?, ?, ?, ?, ?, ?)",
            (user_id, state or "main", temp_data_value, quote_time or "", receive_quotes or 0, last_quote_date or "")
        )
    conn.commit()
    conn.close()

def save_psychologist_message(user_id, message, contact=None, is_anonymous=True):
    conn = sqlite3.connect(DB_NAME)
    cur = conn.cursor()
    cur.execute(
        "INSERT INTO psychologist_messages (user_id, message, timestamp, is_anonymous, contact, answered) VALUES (?, ?, ?, ?, ?, ?)",
        (user_id, message, datetime.datetime.now().isoformat(), 1 if is_anonymous else 0, contact, 0)
    )
    conn.commit()
    msg_id = cur.lastrowid
    conn.close()
    return msg_id

def get_message_by_id(msg_id):
    conn = sqlite3.connect(DB_NAME)
    cur = conn.cursor()
    cur.execute("SELECT user_id, message, contact, is_anonymous, answered FROM psychologist_messages WHERE id = ?", (msg_id,))
    row = cur.fetchone()
    conn.close()
    if row:
        return {
            "user_id": row[0],
            "message": row[1],
            "contact": row[2],
            "is_anonymous": row[3],
            "answered": row[4]
        }
    return None

def get_unanswered_messages():
    conn = sqlite3.connect(DB_NAME)
    cur = conn.cursor()
    cur.execute("SELECT id, user_id, message, contact, is_anonymous, timestamp FROM psychologist_messages WHERE answered = 0 ORDER BY id")
    rows = cur.fetchall()
    conn.close()
    return rows

def mark_message_answered(msg_id, answer_text):
    conn = sqlite3.connect(DB_NAME)
    cur = conn.cursor()
    cur.execute(
        "UPDATE psychologist_messages SET answered = 1, answer_text = ?, answer_timestamp = ? WHERE id = ?",
        (answer_text, datetime.datetime.now().isoformat(), msg_id)
    )
    conn.commit()
    conn.close()

def clear_user_state(user_id):
    conn = sqlite3.connect(DB_NAME)
    cur = conn.cursor()
    cur.execute("UPDATE users SET state = 'main', temp_data = '' WHERE user_id = ?", (user_id,))
    conn.commit()
    conn.close()
    print(f"🔄 Состояние пользователя {user_id} сброшено")

def add_reminder(user_id, remind_time, action, data=None):
    conn = sqlite3.connect(DB_NAME)
    cur = conn.cursor()
    data_str = json.dumps(data, ensure_ascii=False) if data else ""
    cur.execute(
        "INSERT INTO reminders (user_id, remind_time, action, data) VALUES (?, ?, ?, ?)",
        (user_id, remind_time, action, data_str)
    )
    conn.commit()
    conn.close()

def get_reminders_for_time(current_time):
    conn = sqlite3.connect(DB_NAME)
    cur = conn.cursor()
    cur.execute("SELECT user_id, action, data FROM reminders WHERE remind_time = ?", (current_time,))
    rows = cur.fetchall()
    conn.close()
    return rows

def delete_reminder(user_id, action):
    conn = sqlite3.connect(DB_NAME)
    cur = conn.cursor()
    cur.execute("DELETE FROM reminders WHERE user_id = ? AND action = ?", (user_id, action))
    conn.commit()
    conn.close()

def save_plan(user_id, plan_type, tasks):
    conn = sqlite3.connect(DB_NAME)
    cur = conn.cursor()
    tasks_json = json.dumps(tasks, ensure_ascii=False)
    cur.execute(
        "INSERT INTO plans (user_id, plan_type, tasks, created_at) VALUES (?, ?, ?, ?)",
        (user_id, plan_type, tasks_json, datetime.datetime.now().isoformat())
    )
    conn.commit()
    conn.close()

def get_user_plans(user_id, plan_type=None):
    conn = sqlite3.connect(DB_NAME)
    cur = conn.cursor()
    if plan_type:
        cur.execute("SELECT id, tasks, created_at FROM plans WHERE user_id = ? AND plan_type = ? ORDER BY created_at DESC", (user_id, plan_type))
    else:
        cur.execute("SELECT id, plan_type, tasks, created_at FROM plans WHERE user_id = ? ORDER BY created_at DESC", (user_id,))
    rows = cur.fetchall()
    conn.close()
    return rows
