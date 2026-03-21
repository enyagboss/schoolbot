import sqlite3
from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.cron import CronTrigger
import datetime
import random
from database import get_user, get_reminders_for_time, delete_reminder
from config import QUOTE_TIMES

scheduler = BackgroundScheduler()

def start_scheduler(vk_session):
    # Запланировать отправку цитат по расписанию для каждого пользователя
    # Это сложнее, т.к. у каждого своё время. Проще запускать задачу каждую минуту и проверять БД.
    scheduler.add_job(check_and_send_quotes, 'interval', minutes=1, args=[vk_session])
    scheduler.add_job(check_and_send_reminders, 'interval', minutes=1, args=[vk_session])
    scheduler.start()

def check_and_send_quotes(vk_session):
    """Проверяем, кому нужно отправить цитату сейчас."""
    now = datetime.datetime.now().strftime("%H:%M")
    # В реальном проекте нужно хранить последнюю дату отправки, чтобы не отправлять повторно.
    # Здесь для простоты будем отправлять, если время совпадает и пользователь подписан.
    # Для более точной реализации нужно хранить в БД дату последней отправки и отправлять не чаще раза в день.
    from database import init_db, set_user
    conn = sqlite3.connect("bot_database.db")
    cur = conn.cursor()
    cur.execute("SELECT user_id, quote_time FROM users WHERE receive_quotes = 1 AND quote_time = ?", (now,))
    rows = cur.fetchall()
    conn.close()
    quotes = [
        "Каждый день — новая возможность стать лучше.",
        "Не бойся трудностей — они делают тебя сильнее.",
        "Ты способен на большее, чем думаешь.",
        "Улыбка — самый простой способ изменить мир вокруг.",
        "Верь в себя и свои силы."
    ]
    for row in rows:
        user_id = row[0]
        quote = random.choice(quotes)
        # Отправляем сообщение
        try:
            vk_session.method("messages.send", {"user_id": user_id, "message": quote, "random_id": 0})
        except Exception as e:
            print(f"Ошибка отправки цитаты пользователю {user_id}: {e}")

def check_and_send_reminders(vk_session):
    """Проверяем напоминания."""
    now = datetime.datetime.now().strftime("%H:%M")
    reminders = get_reminders_for_time(now)
    for user_id, action, data in reminders:
        if action == "sleep_preparation":
            text = "Напоминание: пора начинать подготовку ко сну! Выключи телефон, сделай расслабляющие упражнения."
        elif action == "mood_boost":
            # data приходит как строка JSON
            import json
            try:
                d = json.loads(data)
                activity = d.get("activity", "что-то приятное")
                text = f"Напоминание: попробуй {activity}, чтобы улучшить настроение."
            except:
                text = "Напоминание: сделай что-то приятное для себя, чтобы улучшить настроение."
        else:
            text = "Напоминание от твоего помощника."
        try:
            vk_session.method("messages.send", {"user_id": user_id, "message": text, "random_id": 0})
        except Exception as e:
            print(f"Ошибка отправки напоминания пользователю {user_id}: {e}")
        # Удаляем напоминание, если оно одноразовое
        delete_reminder(user_id, action)