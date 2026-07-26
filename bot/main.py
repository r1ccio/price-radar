import asyncio
import os
import logging
from aiogram import Bot, Dispatcher, types
from aiogram.filters import CommandStart

logging.basicConfig(level=logging.INFO)

TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")

bot = Bot(token=TOKEN)
dp = Dispatcher()

@dp.message(CommandStart())
async def handle_start(message: types.Message):

    await message.answer(
        "Hello! I am Price Radar Bot!\n\n"
        "Soon I will learn to recieve links from you and send them into system for tracking"
    )

async def main():
    logging.info("Launching Telegram-bot...")
    await dp.start_polling(bot)

if __name__ == '__main__':
    asyncio.run(main())
