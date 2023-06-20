import time
import random
import traceback
from asyncio import Task
import cv2
import numpy as np
import piexif
from PIL import Image as PilImage
from aiogram import Bot
from aiogram.fsm.context import FSMContext
from aiogram.fsm.storage.base import StorageKey
from aiogram.types import Message, FSInputFile
from buttons import keyboard_start_image_unique_configured
from config import IS_LOCAL, TEMP_FILES_DIR, ACTIVE_USERS_STORAGE
from tools.editor_tools import EditorTools


class UniquePhoto(EditorTools):
    __slots__ = {}

    async def run_get_unique_photo_save_coroutine(self, file_id, bot_object: Bot, message: Message, state: FSMContext):
        task_obj = Task(self.get_unique_photo(file_id, bot_object, message, state))
        await ACTIVE_USERS_STORAGE.set_data(
            bot=bot_object,
            key=StorageKey(bot_id=bot_object.id, chat_id=message.chat.id, user_id=message.from_user.id),
            data={"task_obj": task_obj}
        )

    async def get_unique_photo(self, file_id, bot_object: Bot, message: Message, state: FSMContext):
        file_path = f"{TEMP_FILES_DIR}\\photo\\{file_id}.png" if IS_LOCAL else f"{TEMP_FILES_DIR}\\photo\\{file_id}.png"
        # Рандомное имя файла (с сохранением в директорию)
        new_file_path = await self.get_new_random_filename(file_path)

        try:
            message = await message.answer('Начинаю уникализацию...\n\n🟩◻◻◻◻◻◻◻◻◻')
            await bot_object.download(file=file_id, destination=file_path)

            # Уникализируем фото путем его изменения (шум + изменение размера)
            await self.resize_photo(file_path)
            await self.noise_gauss(file_path)

            await message.edit_text(text='Получение всех необходимых данных\n\n🟩🟩🟩◻◻◻◻◻◻◻')

            # Изменение метаданных
            date = await self.random_generate_date()
            info_about_phone = await self.random_model_make_and_software()
            model = info_about_phone[0]
            make = info_about_phone[1]
            software = info_about_phone[2]
            sub_sec = await self.get_sub_sec()

            await message.edit_text(text='Начинаю изменение метаданных\n\n🟩🟩🟩🟩🟩🟩🟩◻◻◻')

            zeroth_ifd = {
                piexif.ImageIFD.BitsPerSample: 8,
                piexif.ImageIFD.ColorMap: 3,
                piexif.ImageIFD.DateTime: date,
                piexif.ImageIFD.PreviewDateTime: date,
                piexif.ImageIFD.ImageWidth: await self.get_width_photo(file_path),
                piexif.ImageIFD.ImageLength: await self.get_height_photo(file_path),
                piexif.ImageIFD.YCbCrSubSampling: await self.get_YCbCrSubSampling(),
                piexif.ImageIFD.XResolution: (72, 72),
                piexif.ImageIFD.YResolution: (72, 72),
                piexif.ImageIFD.PreviewColorSpace: await self.get_preview_color_space(),
                piexif.ImageIFD.Compression: random.randint(6, 7),
                piexif.ImageIFD.DocumentName: ' ',
                piexif.ImageIFD.SelfTimerMode: 2,
                piexif.ImageIFD.ImageDescription: 'smart',
                piexif.ImageIFD.Model: model,
                piexif.ImageIFD.Make: make,
                piexif.ImageIFD.Software: software,
                piexif.ImageIFD.SampleFormat: await self.get_sample_format(),
                piexif.ImageIFD.Predictor: await self.get_predictor(),
                piexif.ImageIFD.ResolutionUnit: await self.get_resolution_unit(),
                piexif.ImageIFD.GrayResponseUnit: await self.get_gray_response_unit()
            }
            exif_ifd = {
                piexif.ExifIFD.Gamma: (1, 1),
                piexif.ExifIFD.ExposureMode: random.randint(0, 2),
                piexif.ExifIFD.ExposureTime: await self.get_exposure_time(),
                piexif.ExifIFD.FNumber: await self.get_f_number(),
                piexif.ExifIFD.FocalLengthIn35mmFilm: await self.get_FocalLengthIn35mmFilm(),
                piexif.ExifIFD.WhiteBalance: random.randint(0, 1),
                piexif.ExifIFD.Sharpness: random.randint(0, 2),
                piexif.ExifIFD.SensingMethod: random.randint(0, 8),
                piexif.ExifIFD.ShutterSpeedValue: await self.get_shutter_speed_value(),
                piexif.ExifIFD.FocalLength: await self.get_focal_length(),
                piexif.ExifIFD.SubSecTime: sub_sec,
                piexif.ExifIFD.SubSecTimeDigitized: sub_sec,
                piexif.ExifIFD.SubSecTimeOriginal: sub_sec,
                piexif.ExifIFD.DateTimeDigitized: date,
                piexif.ExifIFD.DateTimeOriginal: date,
                piexif.ExifIFD.SensitivityType: await self.get_sensitivity_type(),
            }
            interop_ifd = {

            }
            num = random.randint(1, 3)

            if num == 1:
                author = await self.get_random_artist()
                zeroth_ifd[piexif.ImageIFD.Orientation] = await self.get_orientation()
                zeroth_ifd[piexif.ImageIFD.PhotometricInterpretation] = await self.get_photometric_interpretation()
                zeroth_ifd[piexif.ImageIFD.Artist] = author
            elif num == 2:
                zeroth_ifd[piexif.ImageIFD.FillOrder] = await self.get_fill_order()
                zeroth_ifd[piexif.ImageIFD.Threshholding] = await self.get_threshholding()
            elif num == 3:
                interop_ifd[piexif.InteropIFD.InteroperabilityIndex] = await self.get_interop_index()

            exif_dict = {"0th": zeroth_ifd, "Exif": exif_ifd, "GPS": {}, "1st": interop_ifd, "thumbnail": None}
            exif_bytes = piexif.dump(exif_dict)
            image = PilImage.open(file_path)

            await message.edit_text(text='Сохранение...\n\n🟩🟩🟩🟩🟩🟩🟩🟩🟩🟩')

            image.save(new_file_path, exif=exif_bytes)

            await message.answer_photo(photo=FSInputFile(new_file_path), reply_markup=keyboard_start_image_unique_configured)
            await self.remove_temp_photo_files()
            await state.clear()
            await message.edit_text('Готово!')

        except Exception as e:
            print(e.args)
            traceback.print_exc()
            await state.clear()
            await self.remove_temp_photo_files()
            await message.answer('Возникла неизвестная ошибка. Попробуйте повторить уникализацию',
                                 reply_markup=keyboard_start_image_unique_configured)

    #######################################################################################################################
    # Ниже описаны методы рандомной генерации exif данных и уникализации файлов
    #######################################################################################################################

    @staticmethod
    async def random_generate_date():
        """Генерация даты"""
        start = '1/1/2019 1:30 PM'
        end = '1/1/2022 4:50 AM'
        time_format = '%m/%d/%Y %I:%M %p'
        prop = random.random()

        stime = time.mktime(time.strptime(start, time_format))
        etime = time.mktime(time.strptime(end, time_format))

        ptime = stime + prop * (etime - stime)

        return time.strftime(time_format, time.localtime(ptime))

    @staticmethod
    async def random_model_make_and_software() -> list:
        """Генерация рандомного создателя и рандомной версии телефона"""
        make = ['IPHONE', 'HUAWEI', 'SAMSUNG']
        make_num = random.randint(0, len(make) - 1)
        model = None
        software = None

        if make[make_num] == 'IPHONE':
            model = ['Apple iPhone 11', 'Apple iPhone 10', 'Apple iPhone 9']
            software = ['IOS 11.2.1.3', 'IOS 12.1.1.2', 'IOS 11.0.4.5', 'IOS 7.5.21']
        elif make[make_num] == 'HUAWEI':
            model = ['HUAWEI Y6', 'HUAWEI Y9 2019', 'Huawei Y9 Prime 2019', 'Huawei P Smart 2019 3/32Gb (POT-LX1)',
                     'HUAWEI Y5p 2017']
            software = ['HiSuite']
        elif make[make_num] == 'SAMSUNG':
            model = ['Galaxy S20 FE Snapdragon', 'Galaxy S8+', 'Galaxy Note8', 'Galaxy Note8']
            software = ['samsung-software']

        model_num = random.randint(0, len(model) - 1)
        software_num = random.randint(0, len(software) - 1)

        return [model[model_num], make[make_num], software[software_num]]

    @staticmethod
    async def get_random_artist():
        artist_one = ['Donald Silva', 'Andrew Luna', 'Harry Hodges', 'Raul Peterson', 'Willie Keller', 'Allen Miller',
                      'Jesse Snyder', 'John Little', 'Jose Byrd', 'Donald Davis', 'Peter Joseph', 'Jordan Ball',
                      'James Miller',
                      'Matthew Martinez', 'Tim Jackson', 'Melvin Rodriguez', 'Troy Johnson', 'John Davis',
                      'Richard Lawrence']

        artist_two = ['Brett Hamilton', 'Eric Cannon', 'Lewis Johnston', 'Mark Stewart', 'Michael Simpson',
                      'James Brown',
                      'Oscar Parker', 'William Powers', 'Dustin Berry', 'Francis Ramos', 'Robert Davis', 'Joe Daniels',
                      'Jeffrey Strickland', 'Ben Brooks', 'John Rose', 'Reginald Cannon', 'Duane Meyer',
                      'David Gutierrez',
                      'Raymond Todd', 'Alex Gill', 'Marc Harris', 'Robert Willis', 'Ralph Moore', 'Herbert Miller',
                      'Dwayne Johnson']

        artist_three = 'Teresa Jenkins,Sherry Lawrence,Sherri Medina,Rita Patterson,Mabel Burton,Jean Taylor,Nancy Ross,' \
                       'Debra Carroll,Marion King,Evelyn Meyer,Deborah McDonald,Mary Crawford,Mary Jacobs,Nancy Rogers,' \
                       'Annie Bell,Laura Logan,Lisa Butler,Jennifer Ruiz,Laura Rodgers,Patricia Allen,Sara White,Bonnie' \
                       'Stone,Amy Olson,Ethel Stewart,Christine Knight,Joy Cannon,Carol Perkins,Anne Dixon,Laura Obrien,' \
                       'Dorothy Hernandez,Paula Wagner,Shirley Moore,Stephanie Thomas,Sarah Floyd,Judith Arnold,' \
                       'Eva Stephens,Cheryl Strickland,Michelle Cruz,Kathy Garza,Brenda Davis,Virginia Collins,Stacy Reyes,' \
                       'Shelly Houston,Deborah Harris,Sandra Rice,Lillie Alvarado,Ella Blake,Marilyn Foster,' \
                       'Beverly Ramirez,Elaine Cooper'.split(',')

        artist_four = 'Paul Cook,Howard Reynolds,Lloyd Jones,John Anderson,Victor Rodriguez,David Phillips,David Robinson,' \
                      'Jeffery Wilson,Jason Perez,Thomas Daniel,Francis Moreno,Patrick Martinez,Melvin Cain,' \
                      'Keith Jones,Norman Jones,Christopher McDonald,John Collins,Lee Russell,James Smith,' \
                      'Douglas Sanchez,Ken Day,Joel Henry,Larry Barnes,James West,Chris Rodriguez,Virgil Holt,' \
                      'Jonathan Vargas,John Price,David Kim,Phillip Christensen,James Brown,Ronald Garcia,Tony Walker,' \
                      'Greg Murphy,Edwin Smith,Charles Hodges,Johnny Fisher,Richard Mitchell,James Collins,Ricardo Butler,' \
                      'Clyde Smith,Robert Brooks,Randy Fuller,Michael Davis,Jeffrey Hughes,Carlos Smith,' \
                      'Russell James,Warren Allen,Robert Boyd,Michael Hart'.split(',')

        artist_num = random.randint(1, 4)
        artist = None

        if artist_num == 1:
            artist_num = random.randint(0, len(artist_one) - 1)
            artist = artist_one[artist_num]
        elif artist_num == 2:
            artist_num = random.randint(0, len(artist_two) - 1)
            artist = artist_two[artist_num]
        elif artist_num == 3:
            artist_num = random.randint(0, len(artist_three) - 1)
            artist = artist_three[artist_num]
        elif artist_num == 4:
            artist_num = random.randint(0, len(artist_four) - 1)
            artist = artist_four[artist_num]

        return artist

    @staticmethod
    async def get_preview_color_space():
        color = random.randint(1, 65535)
        return color

    @staticmethod
    async def get_sub_file_type():
        sub_file_type = ['Full-resolution image', 'Reduced-resolution image', 'Single page of multi-page image',
                         'Single page of multi-page reduced-resolution image', 'Transparency mask', 'Depth map',
                         'invalid', 'invalid', 'invalid', 'Single page']

        sub_file_type_num = random.randint(0, len(sub_file_type) - 1)
        return sub_file_type[sub_file_type_num]

    @staticmethod
    async def get_interop_index():
        interop_index = ['R03 - DCF option file (Adobe RGB)', 'R98 - DCF basic file (sRGB)', 'THM - DCF thumbnail file']

        interop_index_num = random.randint(0, len(interop_index) - 1)
        return interop_index[interop_index_num]

    @staticmethod
    async def get_threshholding():
        threshholding = ['No dithering or halftoning', 'Ordered dither or halftone', 'Randomized dither']

        threshholding_num = random.randint(1, len(threshholding))
        return threshholding_num

    @staticmethod
    async def get_fill_order():
        fill_order = ['Normal', 'Reversed']

        num_fill_order = random.randint(1, len(fill_order))
        return num_fill_order

    @staticmethod
    async def get_photometric_interpretation():
        # photometric_interpretation = {'WhiteIsZero': 0,
        #                               'BlackIsZero': 1,
        #                               'RGB': 2,
        #                               'RGB Palette': 3,
        #                               'Transparency Mask': 4,
        #                               'CMYK': 5,
        #                               'YCbCr': 6,
        #                               'CIELab': 8,
        #                               'ICCLab': 9}

        num_photometric_interpretation = random.randint(0, 9)
        if num_photometric_interpretation != 7:
            return num_photometric_interpretation
        return 6

    @staticmethod
    async def get_orientation():
        orientation = ['Horizontal (normal)']

        num_orientation = random.randint(0, len(orientation) - 1)
        return num_orientation

    @staticmethod
    async def get_gray_response_unit():
        gray_response_unit = [0.1, 0.001, 0.0001, 1e-05, 1e-06]

        num_gray_response_unit = random.randint(0, len(gray_response_unit) - 1)

        return num_gray_response_unit

    @staticmethod
    async def get_resolution_unit():
        resolution_unit = ['None', 'inches', 'cm']

        num_resolution_unit = random.randint(0, len(resolution_unit) - 1)
        return num_resolution_unit

    @staticmethod
    async def get_predictor():
        predictor = ['None', 'Horizontal differencing', 'Floating point', 'Horizontal difference X2',
                     'Horizontal difference X4', 'Floating point X2', 'Floating point X4']

        num_predictor = random.randint(0, len(predictor) - 1)
        return num_predictor

    @staticmethod
    async def get_sample_format():
        sample_format = ['Unsigned', 'Undefined', 'Signed', 'Complex int', 'Float', 'Complex float']
        num_sample_format = random.randint(0, len(sample_format) - 1)
        return num_sample_format

    @staticmethod
    async def get_YCbCrSubSampling():
        YCbCrSubSampling = [[1, 1], [2, 2], [2, 4], [4, 1], [1, 4]]

        YCbCrSubSampling_num = random.randint(0, len(YCbCrSubSampling) - 1)
        return YCbCrSubSampling[YCbCrSubSampling_num]

    @staticmethod
    async def get_sensitivity_type():
        sensitivity = random.randint(1, 7)
        return sensitivity

    @staticmethod
    async def get_width_photo(file_path):
        image = PilImage.open(file_path)
        return int(image.width)

    @staticmethod
    async def get_height_photo(file_path):
        image = PilImage.open(file_path)
        return int(image.height)

    @staticmethod
    async def get_exposure_time():
        num_1 = random.randint(1, 64)
        num_2 = random.randint(1, 64)
        exposure_time = (num_1, num_2)
        return exposure_time

    @staticmethod
    async def get_exposure_program():
        exposure_program = ['Program AE', 'Not Defined', 'Bulb', 'Landscape', 'Portrait', 'Action (High speed)',
                            'Creative (Slow speed)', 'Shutter speed priority AE', 'Manual']
        num_exposure_program = random.randint(0, len(exposure_program) - 1)
        return exposure_program[num_exposure_program]

    @staticmethod
    async def get_photo_gamma():
        gammas = ['black', 'white', 'grey', 'dark', 'light coloured', ' ']
        num_gammas = random.randint(0, len(gammas) - 1)
        return gammas[num_gammas]

    @staticmethod
    async def get_f_number():
        num_1 = random.randint(1, 4)
        num_2 = random.randint(1, 4)
        f_number = (num_1, num_2)
        return f_number

    @staticmethod
    async def get_FocalLengthIn35mmFilm():
        FocalLengthIn35mmFilm = random.randint(0, 35)
        return FocalLengthIn35mmFilm

    @staticmethod
    async def get_shutter_speed_value():
        num_1 = random.randint(5000, 25000)
        num_2 = random.randint(5000, 25000)
        speed = (num_1, num_2)
        return speed

    @staticmethod
    async def get_focal_length():
        num_1 = random.randint(10000, 50000)
        num_2 = random.randint(10000, 50000)
        FocalLength = (num_1, num_2)
        return FocalLength

    @staticmethod
    async def get_sub_sec():
        sub_sec = str(random.randint(14000, 150000))
        return str(sub_sec)

    @staticmethod
    async def resize_photo(file_path: str):
        """Изменение размера фото на 1 - 3 пиксель"""
        image = PilImage.open(file_path)
        pixel = random.randint(1, 3)
        if pixel == 1 or pixel == 3:
            cord = (image.width - pixel, image.height - pixel)
        else:
            cord = (image.width + pixel, image.height + pixel)
        image_resize = image.resize(cord)
        image_resize.save(file_path)

    @staticmethod
    async def noise_gauss(file_path: str):
        """Добавление шума на фотографию при помощи аддитивного шума с распределением по Гауссу"""
        image = cv2.imread(file_path)
        row, col, ch = image.shape
        mean = 0
        var = 0.1
        sigma = var ** 0.5
        gauss = np.random.normal(mean, sigma, (row, col, ch))
        gauss = gauss.reshape(row, col, ch)
        noisy = image + gauss
        cv2.imwrite(file_path, noisy)
