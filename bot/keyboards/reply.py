from aiogram.types import KeyboardButton
from aiogram.utils.keyboard import ReplyKeyboardBuilder


def get_keyboard(
    *buttons: str,
    placeholder: str | None = None,
    request_contact: bool = False,
    request_location: bool = False,
    adjust_values: tuple[int, ...] | None = None,
    one_time_kbd: bool = False,
):
    keyboard = ReplyKeyboardBuilder()
    for text in buttons:
        if request_contact and 'телеф' in text.lower():
            keyboard.add(KeyboardButton(text=text, request_contact=True))
        elif request_location and 'локац' in text.lower():
            keyboard.add(KeyboardButton(text=text, request_location=True))
        else:
            keyboard.add(KeyboardButton(text=text))
    if adjust_values:
        keyboard.adjust(*adjust_values)

    return keyboard.as_markup(
        resize_keyboard=True, input_field_placeholder=placeholder, one_time_keyboard=one_time_kbd
    )
