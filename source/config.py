from os import getcwd, environ
from aiogram.fsm.storage.memory import MemoryStorage

IS_LOCAL = "Pycharm" in getcwd()
FFMPEG_PATH = f'{getcwd()}\\source\\ffmpeg_driver\\ffmpeg-windows.exe' if IS_LOCAL else f'{getcwd()}\\ffmpeg_driver\\ffmpeg-linux'
TEMP_FILES_DIR = f"{getcwd()}\\source\\temp_files" if IS_LOCAL else f"{getcwd()}\\temp_files"
ACTIVE_USERS_STORAGE = MemoryStorage()
