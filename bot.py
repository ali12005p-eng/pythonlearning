from aiogram import Bot, Dispatcher, F
from aiogram.types import Message, InlineKeyboardMarkup, InlineKeyboardButton, CallbackQuery
from aiogram.filters import CommandStart
from ai import generate_story
import os

BOT_TOKEN = os.getenv("BOT_TOKEN")

bot = Bot(token=BOT_TOKEN)
dp = Dispatcher()

# ذاكرة المستخدمين
user_sessions = {}

def main_menu():
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(
                    text="🎮 بدء القصة",
                    callback_data="start_story"
                )
            ],
            [
                InlineKeyboardButton(
                    text="🔄 قصة جديدة",
                    callback_data="new_story"
                )
            ]
        ]
    )

@dp.message(CommandStart())
async def start(message: Message):
    await message.answer(
        "🎭 أهلاً بك في لعبة السيناريوهات التفاعلية!\n\n"
        "اضغط على زر (بدء القصة) للبدء.",
        reply_markup=main_menu()
    )

@dp.callback_query(F.data == "start_story")
async def start_story(callback: CallbackQuery):

    user_id = callback.from_user.id

    # 🔥 بداية قصة مع شرح العالم ودور اللاعب
    user_sessions[user_id] = [
        "ابدأ لعبة RPG جديدة واشرح العالم ودور اللاعب وهدفه ثم ابدأ أول مشهد."
    ]

    await callback.message.edit_text(
        "⏳ جاري إنشاء القصة..."
    )

    try:
        response = await generate_story(
            "\n".join(user_sessions[user_id])
        )

        user_sessions[user_id].append(f"Bot: {response}")

        await callback.message.answer(
            response,
            reply_markup=main_menu()
        )

    except Exception as e:
        await callback.message.answer(
            f"❌ خطأ: {e}"
        )

    await callback.answer()

@dp.callback_query(F.data == "new_story")
async def new_story(callback: CallbackQuery):

    user_id = callback.from_user.id

    # 🔥 قصة جديدة مع نفس الفكرة (شرح + بداية)
    user_sessions[user_id] = [
        "ابدأ لعبة RPG جديدة مختلفة تماماً عن السابقة واشرح العالم ودور اللاعب وهدفه ثم ابدأ أول مشهد."
    ]

    await callback.message.answer(
        "🔄 تم إنشاء قصة جديدة...\n⏳ انتظر قليلاً."
    )

    try:
        response = await generate_story(
            "\n".join(user_sessions[user_id])
        )

        user_sessions[user_id].append(f"Bot: {response}")

        await callback.message.answer(
            response,
            reply_markup=main_menu()
        )

    except Exception as e:
        await callback.message.answer(
            f"❌ خطأ: {e}"
        )

    await callback.answer()

@dp.message()
async def handle_message(message: Message):

    user_id = message.from_user.id
    user_text = message.text

    if user_id not in user_sessions:
        await message.answer(
            "🎮 اضغط على (بدء القصة) أولاً.",
            reply_markup=main_menu()
        )
        return

    # حفظ تفاعل اللاعب
    user_sessions[user_id].append(f"User: {user_text}")

    history = "\n".join(user_sessions[user_id])

    try:
        response = await generate_story(history)

        user_sessions[user_id].append(f"Bot: {response}")

        await message.answer(
            response,
            reply_markup=main_menu()
        )

    except Exception as e:
        await message.answer(
            f"❌ خطأ: {e}"
        )
