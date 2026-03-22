from vk_api.keyboard import VkKeyboard, VkKeyboardColor

def main_keyboard():
    keyboard = VkKeyboard(one_time=False)
    keyboard.add_button("Стресс", color=VkKeyboardColor.PRIMARY)
    keyboard.add_button("Конфликты", color=VkKeyboardColor.PRIMARY)
    keyboard.add_line()
    keyboard.add_button("Мотивация", color=VkKeyboardColor.PRIMARY)
    keyboard.add_button("ЗОЖ", color=VkKeyboardColor.PRIMARY)
    keyboard.add_line()
    keyboard.add_button("Психолог", color=VkKeyboardColor.NEGATIVE)
    keyboard.add_button("Цитата", color=VkKeyboardColor.SECONDARY)
    keyboard.add_line()
    keyboard.add_button("Сон", color=VkKeyboardColor.SECONDARY)
    keyboard.add_button("Организация", color=VkKeyboardColor.SECONDARY)
    keyboard.add_line()
    keyboard.add_button("Помощь", color=VkKeyboardColor.SECONDARY)
    keyboard.add_button("Отмена", color=VkKeyboardColor.NEGATIVE)
    return keyboard

def yes_no_keyboard():
    keyboard = VkKeyboard(one_time=True)
    keyboard.add_button("Да", color=VkKeyboardColor.POSITIVE)
    keyboard.add_button("Нет", color=VkKeyboardColor.NEGATIVE)
    keyboard.add_button("Отмена", color=VkKeyboardColor.SECONDARY)
    return keyboard

def time_keyboard():
    keyboard = VkKeyboard(one_time=True)
    keyboard.add_button("Утром", color=VkKeyboardColor.PRIMARY)
    keyboard.add_button("Днём", color=VkKeyboardColor.PRIMARY)
    keyboard.add_button("Вечером", color=VkKeyboardColor.PRIMARY)
    keyboard.add_button("Отмена", color=VkKeyboardColor.SECONDARY)
    return keyboard

def activity_keyboard():
    keyboard = VkKeyboard(one_time=True)
    keyboard.add_button("Музыка", color=VkKeyboardColor.SECONDARY)
    keyboard.add_button("Прогулка", color=VkKeyboardColor.SECONDARY)
    keyboard.add_button("Творчество", color=VkKeyboardColor.SECONDARY)
    keyboard.add_button("Общение", color=VkKeyboardColor.SECONDARY)
    keyboard.add_button("Отмена", color=VkKeyboardColor.SECONDARY)
    return keyboard

def study_time_keyboard():
    keyboard = VkKeyboard(one_time=True)
    keyboard.add_button("30 минут", color=VkKeyboardColor.PRIMARY)
    keyboard.add_button("1 час", color=VkKeyboardColor.PRIMARY)
    keyboard.add_button("2 часа", color=VkKeyboardColor.PRIMARY)
    keyboard.add_button("Отмена", color=VkKeyboardColor.SECONDARY)
    return keyboard

def physical_activity_keyboard():
    keyboard = VkKeyboard(one_time=True)
    keyboard.add_button("15 минут", color=VkKeyboardColor.PRIMARY)
    keyboard.add_button("30 минут", color=VkKeyboardColor.PRIMARY)
    keyboard.add_button("1 час", color=VkKeyboardColor.PRIMARY)
    keyboard.add_button("Отмена", color=VkKeyboardColor.SECONDARY)
    return keyboard

def cancel_keyboard():
    keyboard = VkKeyboard(one_time=True)
    keyboard.add_button("Отмена", color=VkKeyboardColor.NEGATIVE)
    return keyboard

def psychologist_keyboard():
    keyboard = VkKeyboard(one_time=False)
    keyboard.add_button("Список", color=VkKeyboardColor.PRIMARY)
    keyboard.add_button("Инструкция", color=VkKeyboardColor.SECONDARY)
    return keyboard
