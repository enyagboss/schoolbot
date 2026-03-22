import vk_api
from vk_api.longpoll import VkLongPoll, VkEventType
import time
import random
import traceback
import datetime
import re
from collections import defaultdict

from config import VK_TOKEN, GROUP_ID, PSYCHOLOGIST_ID, ADMIN_ID
from database import (init_db, get_user, set_user, save_psychologist_message,
                      clear_user_state, get_unanswered_messages, mark_message_answered,
                      get_message_by_id)
from keyboards import (main_keyboard, yes_no_keyboard, time_keyboard,
                       activity_keyboard, study_time_keyboard,
                       physical_activity_keyboard, cancel_keyboard,
                       psychologist_keyboard)
import scenarios

init_db()

vk_session = vk_api.VkApi(token=VK_TOKEN)
vk = vk_session.get_api()
longpoll = VkLongPoll(vk_session)

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

def send_msg(user_id, text, keyboard=None):
    try:
        if keyboard:
            vk.messages.send(
                user_id=user_id,
                message=text,
                random_id=0,
                keyboard=keyboard.get_keyboard()
            )
        else:
            vk.messages.send(
                user_id=user_id,
                message=text,
                random_id=0
            )
    except Exception as e:
        print(f"Ошибка отправки сообщения {user_id}: {e}")

def notify_psychologist(user_id, message_text, contact, is_anonymous, msg_id):
    if PSYCHOLOGIST_ID:
        text = f"📨 НОВОЕ ОБРАЩЕНИЕ #{msg_id}\n\n"
        if is_anonymous:
            text += f"👤 Отправитель: Аноним\n"
        else:
            text += f"👤 Отправитель: Пользователь {user_id}\n"
        # Контакт не показываем для анонимных
        if not is_anonymous and contact:
            text += f"📞 Контакт для связи: {contact}\n"
        text += f"\n💬 Текст:\n{message_text}\n\n"
        text += f"📅 {datetime.datetime.now().strftime('%d.%m.%Y %H:%M')}\n"
        text += f"\n✍️ Чтобы ответить, используйте команду: ответ {msg_id} [ваш ответ]"
        send_msg(PSYCHOLOGIST_ID, text, keyboard=psychologist_keyboard())

BAD_WORDS = ['мат', 'ругательство', 'хуй', 'пизда', 'бля', 'сука']
def contains_bad_words(text):
    for word in BAD_WORDS:
        if word in text.lower():
            return True
    return False

last_processed = defaultdict(float)

def handle_message(user_id, text):
    # Защита от дублирования
    key = (user_id, text)
    now = time.time()
    if now - last_processed[key] < 2:
        print(f"⚠️ Пропущен дубль от {user_id}: {text}")
        return
    last_processed[key] = now

    # ========== ПСИХОЛОГ ==========
    if PSYCHOLOGIST_ID and user_id == PSYCHOLOGIST_ID:
        # Кнопка "Список"
        if text == "Список":
            unanswered = get_unanswered_messages()
            if not unanswered:
                send_msg(user_id, "📭 Нет неотвеченных обращений.", keyboard=psychologist_keyboard())
                return
            msg = "📋 НЕОТВЕЧЕННЫЕ ОБРАЩЕНИЯ:\n\n"
            for m in unanswered:
                msg += f"#{m[0]} от {m[5][:10]} "
                if m[4]:
                    msg += "(Аноним)"
                else:
                    msg += f"(пользователь {m[1]})"
                if not m[4] and m[3]:
                    msg += f" Контакт: {m[3]}"
                msg += f"\n{m[2][:100]}\n\n"
            send_msg(user_id, msg, keyboard=psychologist_keyboard())
            return

        # Кнопка "Инструкция"
        if text == "Инструкция":
            instr = (
                "📖 ИНСТРУКЦИЯ ПО ОТВЕТУ НА ОБРАЩЕНИЯ\n\n"
                "1. Чтобы ответить на обращение, используйте команду:\n"
                "   ответ <ID> <текст ответа>\n"
                "   Пример: ответ 1 Спасибо за ваше сообщение, мы свяжемся с вами.\n\n"
                "2. Если обращение анонимное, вы также можете ответить — пользователь получит сообщение от бота.\n\n"
                "3. Если обращение анонимное и оставлен контакт, вы можете ответить через бота или напрямую.\n\n"
                "4. Чтобы просмотреть список неотвеченных обращений, нажмите кнопку 'Список'.\n\n"
                "5. После ответа обращение будет помечено как отвеченное и исчезнет из списка.\n\n"
                "❗ Важно: вы должны быть подписаны на сообщения бота, чтобы получать уведомления о новых обращениях."
            )
            send_msg(user_id, instr, keyboard=psychologist_keyboard())
            return

        # Команда "ответ"
        match = re.match(r'^ответ\s+(\d+)\s+(.+)$', text, re.IGNORECASE | re.DOTALL)
        if match:
            msg_id = int(match.group(1))
            answer_text = match.group(2).strip()
            # Проверяем, что ID есть в списке неотвеченных
            unanswered = get_unanswered_messages()
            unanswered_ids = [m[0] for m in unanswered]
            if msg_id not in unanswered_ids:
                send_msg(user_id, f"❌ Обращение #{msg_id} не найдено в списке неотвеченных. Актуальные ID: {', '.join(map(str, unanswered_ids)) if unanswered_ids else 'нет'}", keyboard=psychologist_keyboard())
                return
            msg_data = get_message_by_id(msg_id)
            if not msg_data:
                send_msg(user_id, f"❌ Ошибка: обращение #{msg_id} существует в списке, но не найдено в БД. Попробуйте позже.", keyboard=psychologist_keyboard())
                return
            if msg_data["answered"]:
                send_msg(user_id, f"⚠️ Обращение #{msg_id} уже было отвечено.", keyboard=psychologist_keyboard())
                return

            user_to_send = msg_data["user_id"]
            is_anonymous = msg_data["is_anonymous"]

            try:
                if is_anonymous:
                    vk.messages.send(
                        user_id=user_to_send,
                        message=f"📩 Ответ психолога на ваше анонимное обращение #{msg_id}:\n\n{answer_text}",
                        random_id=0
                    )
                else:
                    vk.messages.send(
                        user_id=user_to_send,
                        message=f"📩 Ответ психолога на ваше обращение #{msg_id}:\n\n{answer_text}",
                        random_id=0
                    )
                send_msg(user_id, f"✅ Ответ отправлен пользователю.", keyboard=psychologist_keyboard())
                mark_message_answered(msg_id, answer_text)
                send_msg(user_id, f"✅ Обращение #{msg_id} отмечено как отвеченное.", keyboard=psychologist_keyboard())
            except Exception as e:
                send_msg(user_id, f"❌ Не удалось отправить ответ: {e}\nОбращение осталось в списке неотвеченных.", keyboard=psychologist_keyboard())
            return

        # Если ничего не подошло – показываем меню психолога
        send_msg(user_id, "Используй кнопки меню или команду 'ответ <id> <текст>'", keyboard=psychologist_keyboard())
        return

    # ========== ОБЫЧНЫЕ ПОЛЬЗОВАТЕЛИ ==========
    # Отмена
    if text.lower() in ["отмена", "cancel", "стоп", "выйти"]:
        clear_user_state(user_id)
        send_msg(user_id, "❌ Действие отменено. Возвращаюсь в главное меню.", keyboard=main_keyboard())
        return

    if contains_bad_words(text):
        send_msg(user_id, "Пожалуйста, избегай нецензурной лексики. Я здесь, чтобы помогать.")
        return

    # Команда "Советы"
    if text.lower() == "советы":
        advice = ("📚 *Советы по самопомощи*\n\n"
                  "• Если чувствуешь тревогу – сделай дыхательное упражнение: вдох 4 сек, задержка 7, выдох 8.\n"
                  "• Сделай короткую прогулку на свежем воздухе.\n"
                  "• Напиши свои мысли в блокнот, чтобы разобраться в чувствах.\n"
                  "• Поговори с другом или близким человеком.\n"
                  "• Если нужно, обратись к психологу через меню.")
        send_msg(user_id, advice, keyboard=main_keyboard())
        return

    user_data = get_user(user_id)
    if user_data is None:
        set_user(user_id, state="main")
        user_data = get_user(user_id)

    state = user_data["state"]
    temp_data = user_data["temp_data"]

    # Сценарии
    if state != "main":
        try:
            response, keyboard_type = scenarios.process_scenario(
                user_id, text, state, temp_data,
                notify_func=notify_psychologist,
                save_func=save_psychologist_message
            )
            if response:
                if keyboard_type == "yes_no":
                    send_msg(user_id, response, keyboard=yes_no_keyboard())
                elif keyboard_type == "time":
                    send_msg(user_id, response, keyboard=time_keyboard())
                elif keyboard_type == "activity":
                    send_msg(user_id, response, keyboard=activity_keyboard())
                elif keyboard_type == "study_time":
                    send_msg(user_id, response, keyboard=study_time_keyboard())
                elif keyboard_type == "physical":
                    send_msg(user_id, response, keyboard=physical_activity_keyboard())
                elif keyboard_type == "cancel":
                    send_msg(user_id, response, keyboard=cancel_keyboard())
                else:
                    send_msg(user_id, response, keyboard=main_keyboard())
            else:
                clear_user_state(user_id)
                send_msg(user_id, "Произошла ошибка. Давай начнём сначала.", keyboard=main_keyboard())
        except Exception as e:
            print(f"❌ Ошибка в сценарии: {e}")
            traceback.print_exc()
            clear_user_state(user_id)
            send_msg(user_id, "Произошла ошибка. Давай начнём сначала.", keyboard=main_keyboard())
        return

    # Главное меню
    if text.lower() in ["начать", "старт", "привет", "здравствуй"]:
        send_msg(user_id, "Привет! Я твой помощник. Выбери тему:", keyboard=main_keyboard())
        return
    elif text == "Стресс":
        response, _ = scenarios.stress_test(user_id, "start", None)
        send_msg(user_id, response, keyboard=yes_no_keyboard())
        return
    elif text == "Конфликты":
        response, _ = scenarios.conflict_help(user_id, "start", None)
        send_msg(user_id, response)
        return
    elif text == "Мотивация":
        send_msg(user_id, "Хочешь получить совет, как повысить мотивацию к учёбе?", keyboard=yes_no_keyboard())
        set_user(user_id, state="motivation_plan")
        return
    elif text == "ЗОЖ":
        send_msg(user_id, "Хочешь узнать, как поддерживать здоровье и хорошее самочувствие?", keyboard=yes_no_keyboard())
        set_user(user_id, state="healthy_plan")
        return
    elif text == "Психолог":
        clear_user_state(user_id)
        send_msg(user_id, "Ты можешь анонимно рассказать о своих переживаниях, и я помогу связаться со школьным психологом.\nНапиши 'Да', чтобы начать, или выбери другой пункт.", keyboard=yes_no_keyboard())
        set_user(user_id, state="anonymous_message")
        return
    elif text == "Цитата":
        quote = random.choice(QUOTES)
        send_msg(user_id, quote, keyboard=main_keyboard())
        send_msg(user_id, "Хочешь получать такие цитаты каждый день?", keyboard=yes_no_keyboard())
        set_user(user_id, state="quote_subscribe")
        return
    elif text == "Сон":
        response, _ = scenarios.sleep_reminder(user_id, "start", None)
        send_msg(user_id, response, keyboard=yes_no_keyboard())
        return
    elif text == "Организация":
        response, _ = scenarios.organize_plan(user_id, "start", None)
        send_msg(user_id, response, keyboard=yes_no_keyboard())
        return
    elif text == "Помощь":
        help_text = ("🤖 Я твой школьный помощник!\n\n"
                     "📋 Я умею:\n"
                     "• Проводить тест на стресс\n"
                     "• Помогать в конфликтных ситуациях\n"
                     "• Давать советы по мотивации и ЗОЖ\n"
                     "• Передавать анонимные сообщения психологу\n"
                     "• Присылать мотивационные цитаты\n"
                     "• Давать рекомендации по организации и сну\n\n"
                     "💡 Просто выбери нужную тему в меню.\n\n"
                     "Также ты можешь написать:\n"
                     "• 'Плохое настроение' - получить совет\n"
                     "• 'Буллинг' - узнать как защитить себя\n"
                     "• 'Тревога' - справиться с беспокойством\n"
                     "• 'Самоорганизация' - составить план дел\n"
                     "• 'Советы' - получить советы по самопомощи\n\n"
                     "❗ Чтобы выйти из любого диалога, напиши 'Отмена'")
        send_msg(user_id, help_text, keyboard=main_keyboard())
        return
    elif text == "Отмена":
        clear_user_state(user_id)
        send_msg(user_id, "Главное меню:", keyboard=main_keyboard())
        return
    else:
        # Дополнительные команды
        if text.lower() in ["плохое настроение", "настроение", "грусть"]:
            response, _ = scenarios.bad_mood(user_id, "start", None)
            send_msg(user_id, response, keyboard=yes_no_keyboard())
            return
        elif text.lower() in ["буллинг", "травля", "обижают"]:
            response, _ = scenarios.bullying(user_id, "start", None)
            send_msg(user_id, response, keyboard=yes_no_keyboard())
            return
        elif text.lower() in ["тревога", "беспокойство", "волнение"]:
            response, _ = scenarios.anxiety(user_id, "start", None)
            send_msg(user_id, response, keyboard=yes_no_keyboard())
            return
        elif text.lower() in ["самоорганизация", "план", "дела"]:
            response, _ = scenarios.self_organization(user_id, "start", None)
            send_msg(user_id, response, keyboard=yes_no_keyboard())
            return
        else:
            send_msg(user_id, "Я не понял. Выбери одну из кнопок или напиши 'Помощь':", keyboard=main_keyboard())
            return

def main():
    print("=" * 50)
    print("🤖 Школьный бот-помощник запущен!")
    print(f"📱 Группа ID: {GROUP_ID}")
    print(f"👨‍⚕️ Психолог ID: {PSYCHOLOGIST_ID}")
    print("=" * 50)
    print("Ожидание сообщений...")
    print("Совет: для выхода из любого диалога напишите 'Отмена'")

    while True:
        try:
            for event in longpoll.listen():
                if event.type == VkEventType.MESSAGE_NEW and event.to_me:
                    user_id = event.user_id
                    text = event.text.strip()
                    print(f"📩 Получено сообщение от {user_id}: {text[:50]}")
                    handle_message(user_id, text)
        except Exception as e:
            print(f"❌ Ошибка в основном цикле: {e}")
            traceback.print_exc()
            time.sleep(5)

if __name__ == "__main__":
    main()
