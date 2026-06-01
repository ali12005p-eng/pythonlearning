from aiogram import Bot, Dispatcher, types
from aiogram.filters import CommandStart
from aiogram.types import Message
from ai import generate_story
import os

BOT_TOKEN = os.getenv("BOT_TOKEN")

bot = Bot(token=BOT_TOKEN)
dp = Dispatcher()

@dp.message(CommandStart())
async def start(message: Message):
    await message.answer(
        "👋 أهلاً بك!\n\n"
        "اكتب أي كلمة ونبدي سيناريو تفاعلي 🎭"
    )

@dp.message()
async def handle_message(message: Message):
    user_text = message.text

    await message.answer("⏳ جاري توليد السيناريو...")

    try:
        response = await generate_story(user_text)
        await message.answer(response)
    except Exception as e:
        await message.answer(f"❌ صار خطأ: {e}")
