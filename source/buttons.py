from aiogram.types import KeyboardButton, ReplyKeyboardMarkup

# Клавиатуры
keyboard_start_image_unique = [[KeyboardButton(text='🌄 Уникализировать медиа 📷')]]
keyboard_stop_image_unique = [[KeyboardButton(text='❌ Остановить')]]


# Конфигурации
keyboard_start_image_unique_configured = ReplyKeyboardMarkup(
    keyboard=keyboard_start_image_unique,
    resize_keyboard=True,  # меняем размер клавиатуры
)

keyboard_stop_image_unique_configured = ReplyKeyboardMarkup(
    keyboard=keyboard_stop_image_unique,
    resize_keyboard=True,  # меняем размер клавиатуры
)