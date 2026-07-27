import asyncio
import os
import logging
import aiohttp
from aiogram import Bot, Dispatcher, F, types
from aiogram.filters import CommandStart, Command
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import StatesGroup, State

logging.basicConfig(level=logging.INFO)

TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")

INTERNAL_API_URL = os.getenv("INTERNAl_API_URL", "http://web:8000/api/v1")

bot = Bot(token=TOKEN)
dp = Dispatcher()

class AddTarget(StatesGroup):
    waiting_for_url = State()
    waiting_for_price = State()

@dp.message(CommandStart())
async def handle_start(message: types.Message):

    await message.answer(
        "Hello! I am Price Radar Bot!\n\n"
        "Soon I will learn to recieve links from you and send them into system for tracking"
    )

@dp.message(Command("add"))
async def cmd_add(message: types.Message, state: FSMContext):
    await message.answer("Send me your target link:")
    await state.set_state(AddTarget.waiting_for_url)

@dp.message(F.text.startswith("http"))
async def handle_url_directly(message: types.Message, state: FSMContext):
    await state.update_data(url=message.text)
    await message.answer("Fine! Enter target price (numbers only):")
    await state.set_state(AddTarget.waiting_for_price)

@dp.message(AddTarget.waiting_for_url)
async def process_url(message: types.Message, state: FSMContext):
    if not message.text.startswith("http"):
        await message.answer("⚠️This doesn`t look like a link. Try again")
    await state.update_data(url=message.text)
    await message.answer("Fine! Enter target price (numbers only):")
    await state.set_state(AddTarget.waiting_for_price)

@dp.message(AddTarget.waiting_for_price)
async def process_price(message: types.Message, state: FSMContext):
    try:
        target_price = float(message.text.replace(',','.'))
    except ValueError:
        await message.answer("⚠️Please, enter number only.")
        return

    user_data = await state.get_data()
    url = user_data['url']

    await message.answer("⏳Sending data to radar...")

    payload = {
        "url": url,
        "target_price": str(target_price),
        "telegram_chat_id": str(message.chat.id)
    }

    api_endpoint = f"{INTERNAL_API_URL}/targets/"

    try:
        async with aiohttp.ClientSession() as session:
            async with session.post(api_endpoint, json=payload) as response:
                if response.status == 201:
                    await message.answer(
                        f"✅ Item successfully added!\n\n"
                        f"I will text you back when price will drop to {target_price} or less"
                    )
                else:
                    error_text = await response.text()
                    await message.answer(f"❌API Error: {error_text}")
    except Exception as e:
        logging.error(f"API request failed: {e}")
        await message.answer("🔌Error connecting to the Django server")

    await state.clear()

async def main():
    logging.info("Launching Telegram-bot...")
    await dp.start_polling(bot)

if __name__ == '__main__':
    asyncio.run(main())
