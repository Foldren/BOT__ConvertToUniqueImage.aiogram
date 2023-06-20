import asyncio
import logging
from aiogram import Bot, Dispatcher
from source.handlers import create_unique_image, start_bot
from config import TOKEN


# Запуск процесса поллинга новых апдейтов
async def main():
    # Включаем логирование, чтобы не пропустить важные сообщения
    logging.basicConfig(level=logging.INFO)
    # Объект бота
    bot = Bot(token=TOKEN)
    # Диспетчер
    dp = Dispatcher()
    dp.include_routers(start_bot.router, create_unique_image.router)
    await bot.delete_webhook(drop_pending_updates=True)
    await dp.start_polling(bot, bot_object=bot)


if __name__ == "__main__":
    asyncio.run(main())
