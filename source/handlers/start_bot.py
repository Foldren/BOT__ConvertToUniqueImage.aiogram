from aiogram.fsm.context import FSMContext
from aiogram.filters import Command
from aiogram.types import Message
from aiogram import Router
from buttons import keyboard_start_image_unique_configured

router = Router()


# Хэндлер на команду /start
@router.message(Command(commands=["start"]))
async def start_image_unique(message: Message, state: FSMContext):
    await state.clear()
    message_text = f'👋 Привет {message.from_user.full_name}! Я бот-уникализатор, \n' \
                   'могу уникализировать видео и фотографии для вас без потери качества\n\n' \
                   '✴ К сожалению, ограничения телеграма не дают заливать файлы больше 20 мегабайт,' \
                   ' обращайте на это внимание при работе\n\n' \
                   '✴ После загрузки видео или фото вы получите уникализированную копию вашего файла\n\n' \
                   '✴ На данный момент я работаю полностью бесплатно, Вам доступен полный мой функционал\n\n' \
                   '✨Желаем приятной работы✨'
    await message.answer(message_text, reply_markup=keyboard_start_image_unique_configured)
