import traceback
from asyncio import Task, sleep
import ffmpeg
import moviepy.editor as mp
from aiogram.fsm.context import FSMContext
from aiogram.fsm.storage.base import StorageKey
from aiogram.types import Message, FSInputFile
from aiogram import Bot
from buttons import keyboard_start_image_unique_configured
from config import FFMPEG_PATH, IS_LOCAL, TEMP_FILES_DIR, ACTIVE_USERS_STORAGE
from tools.editor_tools import EditorTools


class UniqueVideo(EditorTools):
    __slots__ = {}

    async def run_get_unique_video_save_coroutine(self, file_id, bot_object: Bot, message: Message, state: FSMContext):
        task_obj = Task(self.get_unique_video(file_id, bot_object, message, state))
        await ACTIVE_USERS_STORAGE.set_data(
            bot=bot_object,
            key=StorageKey(bot_id=bot_object.id, chat_id=message.chat.id, user_id=message.from_user.id),
            data={"task_obj": task_obj}
        )

    async def get_unique_video(self, file_id, bot_object: Bot, message: Message, state: FSMContext):
        file_path = f"{TEMP_FILES_DIR}\\video\\{file_id}.mp4" if IS_LOCAL else f"{TEMP_FILES_DIR}\\video\\{file_id}.mp4"
        new_file_path = await self.get_new_random_filename(file_path)

        try:
            message_user = message
            message = await message.answer('Начинаю уникализацию...\n\n🟩◻◻◻◻◻◻◻◻◻')
            await bot_object.download(file=file_id, destination=file_path)
            await message.edit_text('Изменяем данные...\n\n🟩🟩🟩◻◻◻◻◻◻◻')

            clip = (mp.VideoFileClip(file_path))
            clip1 = clip.subclip(0, 10)
            width = clip1.w - 2
            height = clip.h - 2

            await message.edit_text(
                'Вносим изменения в видео...\nИногда это может занимать несколько минут (если подключено несколько пользователей)\n\n🟩🟩🟩🟩🟩🟩🟩🟩◻◻')

            proccess_ffmpeg = await self.set_stream_spec_filter(height, width, file_path, new_file_path)

            await ACTIVE_USERS_STORAGE.set_data(
                bot=bot_object,
                key=StorageKey(bot_id=bot_object.id, chat_id=message_user.chat.id, user_id=message_user.from_user.id),
                data={"ffmpeg_proccess": proccess_ffmpeg}
            )

            while proccess_ffmpeg.poll() != 0:  # Ждем пока завершится процесс и проверяем на остановку
                await sleep(0.3)

            await message.edit_text('Готово!\nОтправляем видео...\n\n🟩🟩🟩🟩🟩🟩🟩🟩🟩🟩')

            await message.answer_video(video=FSInputFile(new_file_path),
                                       reply_markup=keyboard_start_image_unique_configured)
            await self.remove_temp_video_files()
            await state.clear()
            await message.edit_text('Готово!')

        except Exception as e:
            print(e.args)
            traceback.print_exc()
            await state.clear()
            await self.remove_temp_video_files()
            await message.answer('Возникла неизвестная ошибка. Попробуйте повторить уникализацию',
                                 reply_markup=keyboard_start_image_unique_configured)

    @staticmethod
    async def set_stream_spec_filter(height, width, file_path, new_file_path):
        stream = ffmpeg.input(file_path)
        audio = stream.audio.filter("aecho", 0.8, 0.9, 1000, 0.3)
        stream = ffmpeg.filter(stream, "scale", width, height)
        stream = ffmpeg.filter(stream, "colorcorrect", 0.001)
        stream = ffmpeg.filter(stream, 'eq', contrast=0.9, brightness=0.01, saturation=1.1, gamma=0.9)
        stream = ffmpeg.output(stream, audio, new_file_path)
        return ffmpeg.run_async(stream_spec=stream, cmd=FFMPEG_PATH, pipe_stdin=True)
