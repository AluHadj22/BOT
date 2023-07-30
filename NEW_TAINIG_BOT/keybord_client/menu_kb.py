from aiogram.types import ReplyKeyboardMarkup, KeyboardButton, ReplyKeyboardRemove



button_load_menu = KeyboardButton('/load_Menu')
button_delete_menu = KeyboardButton('/delete_Menu')

button_case_admin = ReplyKeyboardMarkup(resize_keyboard=True).add(button_load_menu).add(button_delete_menu)
