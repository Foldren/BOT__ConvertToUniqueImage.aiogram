import glob
from hashlib import md5
from os import remove
from random import randint
from config import TEMP_FILES_DIR


class EditorTools:
    @staticmethod
    async def get_new_random_filename(file_path: str) -> str:
        """Рандомная генерация имени с последующим хешированием"""
        alphabet = 'qwertyuiopasdfghjklzxcvbnm'
        digits = '123456789'

        num_digits = len(digits)
        num_alphabet = len(alphabet)

        name = ''

        for digit in digits:
            num = randint(0, num_digits - 1)
            name += digits[num] + digit

        for abc in alphabet:
            num = randint(0, num_alphabet - 1)
            name += alphabet[num] + abc

        name = bytes(name, encoding='utf-8')

        hash_name = md5(name)

        extension = file_path[file_path.rfind("."):]
        dir_path = file_path[:file_path.rfind("\\")] + "\\"

        finish_name = dir_path + hash_name.hexdigest() + extension

        return finish_name

    @staticmethod
    async def remove_temp_video_files():
        for file_path in glob.glob(f"{TEMP_FILES_DIR}/video/*.mp4"):
            try:
                remove(file_path)
            except:
                pass

    @staticmethod
    async def remove_temp_photo_files():
        for file_path in glob.glob(f"{TEMP_FILES_DIR}/photo/*.png"):
            try:
                remove(file_path)
            except:
                pass
