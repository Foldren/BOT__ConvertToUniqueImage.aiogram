from aiogram.fsm.context import FSMContext
from aiogram.fsm.storage.base import StorageKey
from aiogram.types import Message
from aiogram import Router
from aiogram.filters import Text
from config import ACTIVE_USERS_STORAGE
from buttons import keyboard_stop_image_unique_configured, keyboard_start_image_unique_configured
from states.unique_image_video import StepsUniqueImageVideo
from aiogram import Bot
from tools.get_unique_photo import UniquePhoto
from tools.get_unique_video import UniqueVideo
from tools.editor_tools import EditorTools

router = Router()


@router.message(Text(text='🌄 Уникализировать медиа 📷'))
async def start_unique(message: Message, state: FSMContext):
    """Начало уникализации. Пользователю предоставляется выбор фото или видео"""
    await state.clear()
    await state.set_state(StepsUniqueImageVideo.load_image_video)
    await message.answer('Отправьте фото или видео файлом или просто перенесите в чат\n\n'
                         '⚠️ Обратите внимание на то, что в Telegram есть ограничение на размер файла'
                         ' Файл не должен превышать 20 МБ⚠️\n\n'
                         'Если хотите остановить операцию, то воспользуйтесь кнопкой ниже',
                         reply_markup=keyboard_stop_image_unique_configured)


@router.message(Text(text='❌ Остановить'))
async def stop_proccess_unique(message: Message, state: FSMContext, bot_object: Bot):
    data = await ACTIVE_USERS_STORAGE.get_data(
        bot=bot_object,
        key=StorageKey(bot_id=bot_object.id, chat_id=message.chat.id, user_id=message.from_user.id)
    )

    if 'task_obj' in data:
        print("[USER]: STOP UNIQUE")
        data['task_obj'].cancel()

    if 'ffmpeg_proccess' in data:
        print("[USER]: STOP FFMPEG")
        data['ffmpeg_proccess'].kill()

    await EditorTools.remove_temp_video_files()
    await EditorTools.remove_temp_photo_files()
    await state.clear()
    await message.answer(
        'Операция прервана. Для работы с новым медиафайлом нажмите кнопку (🌄 Уникализировать медиа 📷)',
        reply_markup=keyboard_start_image_unique_configured)


@router.message(StepsUniqueImageVideo.load_image_video)
async def proccess_unique_file(message: Message, state: FSMContext, bot_object: Bot):
    if message.photo:
        file_id = message.photo[-1].file_id
        await UniquePhoto().run_get_unique_photo_save_coroutine(file_id, bot_object, message, state)

    elif message.video:
        file_id = message.video.file_id
        await UniqueVideo().run_get_unique_video_save_coroutine(file_id, bot_object, message, state)

    elif message.document:
        if message.document.mime_type[:5] == 'image':
            file_id = message.document.file_id
            await UniquePhoto().run_get_unique_photo_save_coroutine(file_id, bot_object, message, state)
        elif message.document.mime_type[:5] == 'video':
            file_id = message.document.file_id
            await UniqueVideo().run_get_unique_video_save_coroutine(file_id, bot_object, message, state)
        else:
            await message.answer('Ожидалось фото или видео🤷‍♂️\n\
                                  Попробуйте еще раз.')

    else:
        await message.answer('Ожидалось фото или видео🤷‍♂️\n\
                              Попробуйте еще раз или приостановите операцию при помощи кнопки (❌ Остановить)')

