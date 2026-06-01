from aiogram import Bot, Dispatcher
from aiogram.types import Message
from aiogram.filters import CommandStart
from aiogram.fsm.storage.memory import MemoryStorage

from config import BOT_TOKEN
from ai import generate_story

bot = Bot(token=BOT_TOKEN)
dp = Dispatcher(storage=MemoryStorage())

user_sessions = {}

@dp.message(CommandStart())
async def start(message: Message):
    user_sessions[message.from_user.id] = []
    await message.answer("🎮 أهلاً بك في لعبة السيناريو!\nاكتب أي شيء لنبدأ القصة...")

@dp.message()
async def chat(message: Message):
    user_id = message.from_user.id

    if user_id not in user_sessions:
        user_sessions[user_id] = []

    history = user_sessions[user_id]

    history.append({"role": "user", "content": message.text})

    story = generate_story(history)

    history.append({"role": "assistant", "content": story})

    user_sessions[user_id] = history[-10:]

    await message.answer(story)
