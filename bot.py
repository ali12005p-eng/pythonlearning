from aiogram import Bot, Dispatcher
from aiogram.types import Message
from aiogram.filters import CommandStart
from ai import generate_story
import os

BOT_TOKEN = os.getenv("BOT_TOKEN")

bot = Bot(token=BOT_TOKEN)
dp = Dispatcher()

# 🧠 ذاكرة بسيطة لكل مستخدم
user_sessions = {}

@dp.message(CommandStart())
async def start(message: Message):
    user_sessions[message.from_user.id] = []

    await message.answer(
        "🎮 أهلاً بك في لعبة السيناريو!\n\n"
        "اكتب أي شيء لنبدأ القصة..."
    )

@dp.message()
async def handle_message(message: Message):
    user_id = message.from_user.id
    user_text = message.text

    # إذا المستخدم جديد
    if user_id not in user_sessions:
        user_sessions[user_id] = []

    # نخزن الحوار
    user_sessions[user_id].append(f"User: {user_text}")

    history = "\n".join(user_sessions[user_id])

    await message.answer("⏳ جاري متابعة السيناريو...")

    try:
        response = await generate_story(history)

        # نخزن رد البوت حتى يكمل نفس القصة
        user_sessions[user_id].append(f"Bot: {response}")

        await message.answer(response)

    except Exception as e:
        await message.answer(f"❌ خطأ: {e}")
