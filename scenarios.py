import json
import random
import re
import datetime
from database import set_user, save_psychologist_message, add_reminder, save_plan

QUOTES = [
    "Каждый день — новая возможность стать лучше.",
    "Не бойся трудностей — они делают тебя сильнее.",
    "Ты способен на большее, чем думаешь.",
    "Улыбка — самый простой способ изменить мир вокруг.",
    "Верь в себя и свои силы.",
    "Не сравнивай себя с другими — сравнивай себя с собой вчерашним.",
    "Маленькие шаги ведут к большим победам.",
    "Твоя единственная граница — это ты сам."
]

def safe_json_loads(temp_data):
    if not temp_data or temp_data == "":
        return None
    try:
        return json.loads(temp_data)
    except json.JSONDecodeError:
        return None

def process_scenario(user_id, message, state, temp_data, notify_func=None, save_func=None):
    if state == "stress_test":
        return stress_test(user_id, message, temp_data, notify_func, save_func)
    elif state == "stress_breathing":
        return stress_breathing(user_id, message, temp_data, notify_func, save_func)
    elif state == "conflict_help":
        return conflict_help(user_id, message, temp_data, notify_func, save_func)
    elif state == "motivation_plan":
        return motivation_plan(user_id, message, temp_data, notify_func, save_func)
    elif state == "healthy_plan":
        return healthy_plan(user_id, message, temp_data, notify_func, save_func)
    elif state == "anonymous_message":
        return anonymous_message(user_id, message, temp_data, notify_func, save_func)
    elif state == "quote_subscribe":
        return quote_subscribe(user_id, message, temp_data, notify_func, save_func)
    elif state == "organize_plan":
        return organize_plan(user_id, message, temp_data, notify_func, save_func)
    elif state == "sleep_reminder":
        return sleep_reminder(user_id, message, temp_data, notify_func, save_func)
    elif state == "bad_mood":
        return bad_mood(user_id, message, temp_data, notify_func, save_func)
    elif state == "bullying":
        return bullying(user_id, message, temp_data, notify_func, save_func)
    elif state == "anxiety":
        return anxiety(user_id, message, temp_data, notify_func, save_func)
    elif state == "self_organization":
        return self_organization(user_id, message, temp_data, notify_func, save_func)
    else:
        return None, None

# -------------------- Стресс-тест --------------------
def stress_test(user_id, message, temp_data, notify_func=None, save_func=None):
    if temp_data is None:
        questions = [
            "Ты часто чувствуешь усталость?",
            "Тебе сложно сосредоточиться на уроках?",
            "Ты испытываешь раздражение без причины?",
            "Тебе трудно заснуть или ты просыпаешься ночью?",
            "Ты чувствуешь тревогу или беспокойство?"
        ]
        set_user(user_id, state="stress_test", temp_data=json.dumps({"questions": questions, "answers": [], "index": 0}))
        return questions[0], "yes_no"
    else:
        data = safe_json_loads(temp_data)
        if data is None:
            set_user(user_id, state="main", temp_data=None)
            return "Произошла ошибка. Давай начнём сначала. Выбери тему в меню.", None

        answers = data.get("answers", [])
        index = data.get("index", 0)
        questions = data.get("questions", [])

        if not questions:
            set_user(user_id, state="main", temp_data=None)
            return "Произошла ошибка. Давай начнём сначала.", None

        if message.lower() not in ["да", "нет"]:
            if index < len(questions):
                return "Пожалуйста, ответь Да или Нет.", "yes_no"
            else:
                return "Пожалуйста, ответь Да или Нет.", None

        answers.append(message.lower())
        index += 1

        if index < len(questions):
            data["answers"] = answers
            data["index"] = index
            set_user(user_id, temp_data=json.dumps(data))
            return questions[index], "yes_no"
        else:
            yes_count = sum(1 for a in answers if a == "да")
            if yes_count >= 3:
                set_user(user_id, state="stress_breathing", temp_data=None)
                return ("По твоим ответам возможно высокий уровень стресса.\n"
                        "Рекомендую попробовать техники расслабления: глубокое дыхание, прогулку.\n"
                        "Хочешь, я расскажу как делать дыхательное упражнение?"), "yes_no"
            else:
                set_user(user_id, state="main", temp_data=None)
                return ("Отлично! Ты хорошо справляешься со стрессом.\n"
                        "Продолжай в том же духе и не забывай отдыхать."), None

# -------------------- Ответ на вопрос о дыхании --------------------
def stress_breathing(user_id, message, temp_data, notify_func=None, save_func=None):
    if message.lower() == "да":
        breathing = (
            "Вот простое упражнение:\n\n"
            "1. Сядь удобно и закрой глаза.\n"
            "2. Медленно вдохни через нос на 4 секунды.\n"
            "3. Задержи дыхание на 7 секунд.\n"
            "4. Медленно выдохни через рот на 8 секунд.\n\n"
            "Повтори 3 раза. Это поможет успокоиться и снять напряжение."
        )
        set_user(user_id, state="main", temp_data=None)
        return breathing, None
    else:
        set_user(user_id, state="main", temp_data=None)
        return "Хорошо. Если захочешь узнать позже, выбери 'Стресс' снова.", None

# -------------------- Конфликты --------------------
def conflict_help(user_id, message, temp_data, notify_func=None, save_func=None):
    if temp_data is None:
        set_user(user_id, state="conflict_help", temp_data=json.dumps({"step": 1}))
        return ("Расскажи вкратце, что произошло.\n"
                "Ты можешь писать подробно или коротко."), None
    else:
        data = safe_json_loads(temp_data)
        if data is None:
            set_user(user_id, state="main", temp_data=None)
            return "Произошла ошибка. Давай начнём сначала.", None

        step = data.get("step", 1)

        if step == 1:
            data["description"] = message
            data["step"] = 2
            set_user(user_id, temp_data=json.dumps(data))
            return ("Понимаю, это неприятно. Вот несколько советов:\n"
                    "1. Попробуй спокойно поговорить и объяснить свои чувства.\n"
                    "2. Если сложно — обратись к учителю или школьному психологу.\n"
                    "3. Помни, что конфликт можно решить мирно.\n\n"
                    "Хочешь, я помогу составить сообщение для собеседника?"), "yes_no"
        elif step == 2:
            if message.lower() == "да":
                data["step"] = 3
                set_user(user_id, temp_data=json.dumps(data))
                return "Напиши, что ты хочешь сказать, а я помогу оформить.", None
            else:
                set_user(user_id, state="main", temp_data=None)
                return "Хорошо. Если захочешь поговорить с психологом, я всегда рядом.", None
        elif step == 3:
            suggested = f"«{message}»\n\nХочешь отправить это сообщение?"
            data["message_text"] = message
            data["step"] = 4
            set_user(user_id, temp_data=json.dumps(data))
            return suggested, "yes_no"
        elif step == 4:
            if message.lower() == "да":
                return ("Сообщение готово. Ты можешь скопировать его и отправить собеседнику.\n"
                        "Если хочешь, я могу помочь связаться с учителем или психологом."), "yes_no"
            else:
                set_user(user_id, state="main", temp_data=None)
                return "Понял. Если передумаешь, я здесь.", None
        return None, None

# -------------------- Мотивация к учебе --------------------
def motivation_plan(user_id, message, temp_data, notify_func=None, save_func=None):
    if temp_data is None:
        set_user(user_id, state="motivation_plan", temp_data=json.dumps({"step": 1}))
        return "Хочешь получить совет, как повысить мотивацию к учебе?", "yes_no"
    else:
        data = safe_json_loads(temp_data)
        if data is None:
            set_user(user_id, state="main", temp_data=None)
            return "Произошла ошибка. Давай начнём сначала.", None

        step = data.get("step", 1)

        if step == 1:
            if message.lower() == "да":
                data["step"] = 2
                set_user(user_id, temp_data=json.dumps(data))
                return ("Отлично! Вот несколько простых советов:\n"
                        "1. Ставь небольшие цели на каждый день — так легче видеть прогресс.\n"
                        "2. Делай перерывы во время занятий, чтобы не уставать.\n"
                        "3. Найди интересные способы учиться — видео, игры, проекты.\n"
                        "4. Помни, зачем тебе нужны знания — это твой путь к мечте!\n\n"
                        "Хочешь, я помогу составить план на сегодня?"), "yes_no"
            else:
                set_user(user_id, state="main", temp_data=None)
                return "Хорошо. Если передумаешь, я здесь.", None
        elif step == 2:
            if message.lower() == "да":
                data["step"] = 3
                set_user(user_id, temp_data=json.dumps(data))
                return "Сколько времени ты можешь уделить учебе сегодня? (выбери вариант)", "study_time"
            else:
                set_user(user_id, state="main", temp_data=None)
                return "Понял. Если захочешь составить план, напиши 'Мотивация' снова.", None
        elif step == 3:
            time_map = {"30 минут": 30, "1 час": 60, "2 часа": 120}
            if message in time_map:
                total_minutes = time_map[message]
                tasks = [
                    f"{total_minutes//3} минут — повторить материал по одному предмету",
                    f"{total_minutes//3} минут — сделать домашнее задание",
                    f"{total_minutes//3} минут — подготовиться к следующему уроку"
                ]
                plan_text = "\n".join([f"- {t}" for t in tasks])
                save_plan(user_id, "motivation", tasks)
                result = (f"Отлично! Предлагаю:\n{plan_text}\n\n"
                          "Не забывай делать короткие перерывы между задачами.\n"
                          "Хочешь, я буду напоминать о перерывах?")
                set_user(user_id, state="main", temp_data=None)
                return result, "yes_no"
            else:
                return "Пожалуйста, выбери из предложенных вариантов.", "study_time"
        return None, None

# -------------------- Здоровый образ жизни --------------------
def healthy_plan(user_id, message, temp_data, notify_func=None, save_func=None):
    if temp_data is None:
        set_user(user_id, state="healthy_plan", temp_data=json.dumps({"step": 1}))
        return "Хочешь узнать, как поддерживать здоровье и хорошее самочувствие?", "yes_no"
    else:
        data = safe_json_loads(temp_data)
        if data is None:
            set_user(user_id, state="main", temp_data=None)
            return "Произошла ошибка. Давай начнём сначала.", None

        step = data.get("step", 1)

        if step == 1:
            if message.lower() == "да":
                data["step"] = 2
                set_user(user_id, temp_data=json.dumps(data))
                return ("Вот несколько простых правил:\n"
                        "- Спи не менее 8 часов в сутки.\n"
                        "- Питайся разнообразно и сбалансированно.\n"
                        "- Занимайся спортом или просто гуляй на свежем воздухе.\n"
                        "- Ограничь время за гаджетами, особенно перед сном.\n"
                        "- Пей достаточно воды.\n\n"
                        "Хочешь, я помогу составить план здорового дня?"), "yes_no"
            else:
                set_user(user_id, state="main", temp_data=None)
                return "Хорошо. Если передумаешь, я здесь.", None
        elif step == 2:
            if message.lower() == "да":
                data["step"] = 3
                set_user(user_id, temp_data=json.dumps(data))
                return "Сколько времени ты готов уделять физической активности?", "physical"
            else:
                set_user(user_id, state="main", temp_data=None)
                return "Понял. Если захочешь составить план, напиши 'ЗОЖ' снова.", None
        elif step == 3:
            time_map = {"15 минут": 15, "30 минут": 30, "1 час": 60}
            if message in time_map:
                minutes = time_map[message]
                morning = "легкая зарядка или растяжка (10 минут)" if minutes >= 15 else "легкая зарядка (5 минут)"
                evening = f"прогулка или активная игра на улице ({minutes} минут)"
                plan_text = f"- Утром: {morning}\n- Вечером: {evening}"
                save_plan(user_id, "healthy", {"morning": morning, "evening": evening, "total_minutes": minutes})
                result = (f"Отлично! Предлагаю:\n{plan_text}\n\n"
                          "Если хочешь, я могу напоминать тебе о занятиях.")
                set_user(user_id, state="main", temp_data=None)
                return result, "yes_no"
            else:
                return "Пожалуйста, выбери из предложенных вариантов.", "physical"
        return None, None

# -------------------- Анонимное обращение к психологу --------------------
def anonymous_message(user_id, message, temp_data, notify_func=None, save_func=None):
    if temp_data is None:
        set_user(user_id, state="anonymous_message", temp_data=json.dumps({"step": 1}))
        return ("Расскажи, что тебя беспокоит. Ты можешь писать подробно или вкратце.\n"
                "Если хочешь остаться анонимным, не указывай свои данные."), None
    else:
        data = safe_json_loads(temp_data)
        if data is None:
            set_user(user_id, state="main", temp_data=None)
            return "Произошла ошибка. Давай начнём сначала. Выбери тему в меню.", None

        step = data.get("step", 1)

        if step == 1:
            data["message"] = message
            data["step"] = 2
            set_user(user_id, temp_data=json.dumps(data))
            return ("Спасибо, что поделился. Твой запрос будет передан психологу.\n"
                    "Если хочешь, можешь оставить контакт (например, email или номер телефона) для связи, "
                    "или остаться полностью анонимным.\n"
                    "Напиши контакт или слово 'Анонимно'."), None
        elif step == 2:
            if "message" not in data:
                set_user(user_id, state="main", temp_data=None)
                return "Произошла ошибка. Пожалуйста, начни заново, выбрав 'Психолог' в меню.", None

            contact = None if message.lower() == "анонимно" else message
            is_anonymous = (contact is None)

            msg_id = None
            if save_func:
                try:
                    msg_id = save_func(user_id, data["message"], contact=contact, is_anonymous=is_anonymous)
                    print(f"✅ Сообщение психологу сохранено (ID: {msg_id})")
                except Exception as e:
                    print(f"❌ Ошибка сохранения: {e}")

            if notify_func and msg_id:
                try:
                    notify_func(user_id, data["message"], contact, is_anonymous, msg_id)
                except Exception as e:
                    print(f"❌ Ошибка уведомления: {e}")

            set_user(user_id, state="main", temp_data=None)
            return ("✅ Твоё сообщение отправлено психологу!\n\n"
                    "Психолог свяжется с тобой в ближайшее время.\n\n"
                    "Если хочешь, я могу дать советы по самопомощи прямо сейчас.\n"
                    "Напиши 'Советы' или выбери другой пункт меню."), None
        else:
            set_user(user_id, state="main", temp_data=None)
            return "Произошла ошибка. Давай начнём сначала. Выбери тему в меню.", None

# -------------------- Подписка на цитаты --------------------
def quote_subscribe(user_id, message, temp_data, notify_func=None, save_func=None):
    if temp_data is None:
        set_user(user_id, state="quote_subscribe", temp_data=json.dumps({}))
        return "В какое время ты хочешь получать цитаты? (Утром / Днём / Вечером)", "time"
    else:
        time_map = {"утром": "08:00", "днём": "14:00", "вечером": "20:00"}
        if message.lower() in time_map:
            quote_time = time_map[message.lower()]
            set_user(user_id, receive_quotes=1, quote_time=quote_time)
            set_user(user_id, state="main", temp_data=None)
            return f"Отлично! Я буду присылать мотивационные сообщения {message.lower()}.", None
        else:
            return "Пожалуйста, выбери время: Утром / Днём / Вечером", "time"

# -------------------- Организация учебного пространства --------------------
def organize_plan(user_id, message, temp_data, notify_func=None, save_func=None):
    if temp_data is None:
        set_user(user_id, state="organize_plan", temp_data=json.dumps({"step": 1}))
        return "Хочешь узнать, как организовать своё учебное место для лучшей концентрации?", "yes_no"
    else:
        data = safe_json_loads(temp_data)
        if data is None:
            set_user(user_id, state="main", temp_data=None)
            return "Произошла ошибка. Давай начнём сначала.", None

        step = data.get("step", 1)

        if step == 1:
            if message.lower() == "да":
                data["step"] = 2
                set_user(user_id, temp_data=json.dumps(data))
                return ("Вот несколько советов:\n"
                        "- Убери все лишнее с рабочего стола.\n"
                        "- Обеспечь хорошее освещение.\n"
                        "- Держи под рукой все необходимые учебные материалы.\n"
                        "- Сделай место удобным — удобный стул, правильная высота стола.\n"
                        "- Минимизируй отвлекающие факторы (телефон, шум).\n\n"
                        "Хочешь, я помогу составить список для организации твоего рабочего места?"), "yes_no"
            else:
                set_user(user_id, state="main", temp_data=None)
                return "Хорошо. Если передумаешь, я здесь.", None
        elif step == 2:
            if message.lower() == "да":
                tasks = [
                    "Очистить рабочий стол от лишних предметов",
                    "Настроить освещение (лампа, свет)",
                    "Подготовить учебники и тетради",
                    "Убедиться, что стул и стол удобны",
                    "Убрать телефон в сторону"
                ]
                plan_text = "\n".join([f"- {t}" for t in tasks])
                save_plan(user_id, "organize", tasks)
                result = (f"Отлично! Вот план:\n{plan_text}\n\n"
                          "Ты можешь выполнить его сегодня или завтра. Удачи!")
                set_user(user_id, state="main", temp_data=None)
                return result, None
            else:
                set_user(user_id, state="main", temp_data=None)
                return "Понял. Если захочешь получить советы, напиши 'Организация' снова.", None
        return None, None

# -------------------- Здоровый сон --------------------
def sleep_reminder(user_id, message, temp_data, notify_func=None, save_func=None):
    if temp_data is None:
        set_user(user_id, state="sleep_reminder", temp_data=json.dumps({"step": 1}))
        return "Хочешь получить советы по здоровому сну и настроить напоминание?", "yes_no"
    else:
        data = safe_json_loads(temp_data)
        if data is None:
            set_user(user_id, state="main", temp_data=None)
            return "Произошла ошибка. Давай начнём сначала.", None

        step = data.get("step", 1)

        if step == 1:
            if message.lower() == "да":
                data["step"] = 2
                set_user(user_id, temp_data=json.dumps(data))
                return ("Отлично! Предлагаю:\n"
                        "- За 60 минут до сна — выключить телефон и компьютер.\n"
                        "- За 30 минут — заняться расслабляющим занятием (чтение, спокойная музыка).\n"
                        "- За 10 минут — сделать легкую растяжку или дыхательные упражнения.\n"
                        "- Ложиться спать в одно и то же время.\n\n"
                        "В какое время ты обычно хочешь ложиться спать? (например, 22:30)"), None
            else:
                set_user(user_id, state="main", temp_data=None)
                return "Хорошо. Если передумаешь, я здесь.", None
        elif step == 2:
            if re.match(r'^\d{1,2}:\d{2}$', message):
                bedtime = message
                data["bedtime"] = bedtime
                data["step"] = 3
                set_user(user_id, temp_data=json.dumps(data))
                return "Хочешь, чтобы я напоминал тебе начинать подготовку ко сну за 30 минут до этого времени?", "yes_no"
            else:
                return "Пожалуйста, введи время в формате ЧЧ:ММ (например, 22:30).", None
        elif step == 3:
            if message.lower() == "да":
                bedtime = data["bedtime"]
                hour, minute = map(int, bedtime.split(':'))
                remind_hour = (hour - 1) % 24
                remind_minute = minute
                remind_time = f"{remind_hour:02d}:{remind_minute:02d}"
                add_reminder(user_id, remind_time, "sleep_preparation", data={"bedtime": bedtime})
                set_user(user_id, state="main", temp_data=None)
                return f"Отлично! Я буду напоминать тебе о подготовке ко сну в {remind_time}. Спокойных снов!", None
            else:
                set_user(user_id, state="main", temp_data=None)
                return "Понял. Если захочешь настроить напоминание позже, напиши 'Сон'.", None
        return None, None

# -------------------- Помощь при плохом настроении --------------------
def bad_mood(user_id, message, temp_data, notify_func=None, save_func=None):
    if temp_data is None:
        set_user(user_id, state="bad_mood", temp_data=json.dumps({"step": 1}))
        return "Привет! Ты сегодня чувствуешь себя не очень хорошо? Хочешь поговорить или получить совет?", "yes_no"
    else:
        data = safe_json_loads(temp_data)
        if data is None:
            set_user(user_id, state="main", temp_data=None)
            return "Произошла ошибка. Давай начнём сначала.", None

        step = data.get("step", 1)

        if step == 1:
            if message.lower() == "да":
                data["step"] = 2
                set_user(user_id, temp_data=json.dumps(data))
                return ("Понимаю. Иногда помогает сделать что-то приятное для себя. Вот несколько идей:\n"
                        "- Послушать любимую музыку\n"
                        "- Сделать небольшую прогулку\n"
                        "- Нарисовать или написать что-то\n"
                        "- Поговорить с другом или близким человеком\n\n"
                        "Что тебе больше нравится сейчас?"), "activity"
            else:
                set_user(user_id, state="main", temp_data=None)
                return "Хорошо. Если захочешь поговорить, я всегда здесь.", None
        elif step == 2:
            data["choice"] = message
            data["step"] = 3
            set_user(user_id, temp_data=json.dumps(data))

            if message.lower() == "прогулка":
                return ("Отличный выбор! Свежий воздух и движение помогают улучшить настроение.\n"
                        "Постарайся выйти на улицу хотя бы на 10-15 минут. Если хочешь, могу напомнить об этом позже."), "yes_no"
            elif message.lower() == "музыка":
                return ("Музыка — отличный способ поднять настроение. Составь плейлист из любимых треков и послушай 10-15 минут.\n"
                        "Если хочешь, я могу напомнить об этом позже."), "yes_no"
            elif message.lower() == "творчество":
                return ("Творчество помогает выразить эмоции. Попробуй нарисовать что-то или написать короткий рассказ.\n"
                        "Если хочешь, я могу напомнить об этом позже."), "yes_no"
            elif message.lower() == "общение":
                return ("Общение с близкими людьми может помочь. Напиши другу или позвони родным.\n"
                        "Если хочешь, я могу напомнить об этом позже."), "yes_no"
            else:
                return "Пожалуйста, выбери один из вариантов.", "activity"
        elif step == 3:
            if message.lower() == "да":
                now = datetime.datetime.now()
                remind_time = (now + datetime.timedelta(minutes=15)).strftime("%H:%M")
                add_reminder(user_id, remind_time, "mood_boost", data={"activity": data["choice"]})
                set_user(user_id, state="main", temp_data=None)
                return "Хорошо, я напомню через 15 минут. Береги себя!", None
            else:
                set_user(user_id, state="main", temp_data=None)
                return "Понял. Если захочешь поговорить снова, я здесь.", None
        return None, None

# -------------------- Профилактика буллинга --------------------
def bullying(user_id, message, temp_data, notify_func=None, save_func=None):
    if temp_data is None:
        set_user(user_id, state="bullying", temp_data=json.dumps({"step": 1}))
        return "Хочешь узнать, как защитить себя и других от буллинга?", "yes_no"
    else:
        data = safe_json_loads(temp_data)
        if data is None:
            set_user(user_id, state="main", temp_data=None)
            return "Произошла ошибка. Давай начнём сначала.", None

        step = data.get("step", 1)

        if step == 1:
            if message.lower() == "да":
                data["step"] = 2
                set_user(user_id, temp_data=json.dumps(data))
                return ("Буллинг — это когда кто-то постоянно обижает или унижает другого. Вот что можно делать:\n"
                        "- Не молчи, если видишь буллинг — расскажи взрослым (учителю, родителям, школьному психологу).\n"
                        "- Поддерживай тех, кто оказался в трудной ситуации.\n"
                        "- Не участвуй в обидах и не поддавайся на провокации.\n"
                        "- Учись уверенно говорить «нет» и выражать свои чувства.\n\n"
                        "Хочешь, я помогу составить план действий, если столкнешься с буллингом?"), "yes_no"
            else:
                set_user(user_id, state="main", temp_data=None)
                return "Хорошо. Если захочешь узнать больше, напиши 'Буллинг'.", None
        elif step == 2:
            if message.lower() == "да":
                plan = ("Вот простой план:\n"
                        "1. Сохраняй спокойствие и не отвечай агрессией.\n"
                        "2. Обратись за помощью к взрослым.\n"
                        "3. Запиши, что произошло (даты, имена, ситуации).\n"
                        "4. Поддерживай друзей и не оставайся один.\n\n"
                        "Если хочешь, могу подсказать, к кому именно обратиться в твоей школе.")
                set_user(user_id, state="main", temp_data=None)
                return plan, None
            else:
                set_user(user_id, state="main", temp_data=None)
                return "Понял. Если захочешь обсудить, я здесь.", None
        return None, None

# -------------------- Поддержка при тревоге --------------------
def anxiety(user_id, message, temp_data, notify_func=None, save_func=None):
    if temp_data is None:
        set_user(user_id, state="anxiety", temp_data=json.dumps({"step": 1}))
        return "Ты чувствуешь тревогу или беспокойство? Я могу помочь.", "yes_no"
    else:
        data = safe_json_loads(temp_data)
        if data is None:
            set_user(user_id, state="main", temp_data=None)
            return "Произошла ошибка. Давай начнём сначала.", None

        step = data.get("step", 1)

        if step == 1:
            if message.lower() == "да":
                data["step"] = 2
                set_user(user_id, temp_data=json.dumps(data))
                return ("Это нормально — иногда все переживают тревогу. Вот несколько способов справиться:\n"
                        "- Сделай глубокое дыхательное упражнение (хочешь, я напомню, как?).\n"
                        "- Попробуй отвлечься на что-то приятное — музыку, хобби, прогулку.\n"
                        "- Поговори с кем-то, кому доверяешь.\n"
                        "- Запиши свои мысли — это помогает понять, что именно тревожит.\n\n"
                        "Хочешь, я помогу составить план, как справляться с тревогой?"), "yes_no"
            else:
                set_user(user_id, state="main", temp_data=None)
                return "Хорошо. Если захочешь поговорить, я здесь.", None
        elif step == 2:
            if message.lower() == "да":
                plan = ("Отлично! Предлагаю:\n"
                        "1. Утром — 5 минут дыхательных упражнений.\n"
                        "2. В течение дня — делать перерывы и заниматься любимым делом.\n"
                        "3. Вечером — записывать мысли и эмоции.\n\n"
                        "Если тревога станет сильнее, обязательно расскажи взрослым или школьному психологу.\n"
                        "Я могу помочь найти контакты.")
                set_user(user_id, state="main", temp_data=None)
                return plan, None
            else:
                set_user(user_id, state="main", temp_data=None)
                return "Понял. Если захочешь получить совет, напиши 'Тревога' снова.", None
        return None, None

# -------------------- Трудности с самоорганизацией --------------------
def self_organization(user_id, message, temp_data, notify_func=None, save_func=None):
    if temp_data is None:
        set_user(user_id, state="self_organization", temp_data=json.dumps({"step": 1}))
        return "Тебе сложно организовать свое время и справляться с делами? Давай попробуем вместе составить план.", "yes_no"
    else:
        data = safe_json_loads(temp_data)
        if data is None:
            set_user(user_id, state="main", temp_data=None)
            return "Произошла ошибка. Давай начнём сначала.", None

        step = data.get("step", 1)

        if step == 1:
            if message.lower() == "да":
                data["step"] = 2
                set_user(user_id, temp_data=json.dumps(data))
                return "Сколько у тебя дел или задач?", None
            else:
                set_user(user_id, state="main", temp_data=None)
                return "Хорошо. Если передумаешь, я здесь.", None
        elif step == 2:
            try:
                num_tasks = int(message)
                if num_tasks <= 0:
                    raise ValueError
                data["num_tasks"] = num_tasks
                data["tasks"] = []
                data["step"] = 3
                data["current_task"] = 1
                set_user(user_id, temp_data=json.dumps(data))
                return f"Назови задачу номер 1.", None
            except:
                return "Пожалуйста, введи целое число (например, 3).", None
        elif step == 3:
            current = data["current_task"]
            data["tasks"].append(message)

            if current < data["num_tasks"]:
                data["current_task"] += 1
                set_user(user_id, temp_data=json.dumps(data))
                return f"Назови задачу номер {data['current_task']}.", None
            else:
                tasks = data["tasks"]
                plan = []
                for i, task in enumerate(tasks, 1):
                    plan.append(f"{i}. {task} — 30 минут")
                plan_text = "\n".join(plan)
                result = (f"Отлично! Предлагаю такой порядок:\n{plan_text}\n\n"
                          "Между задачами делай короткие перерывы по 5-10 минут.\n"
                          "Хочешь, я помогу установить таймеры?")
                set_user(user_id, state="main", temp_data=None)
                return result, "yes_no"
        return None, None
