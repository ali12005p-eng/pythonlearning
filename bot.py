from aiogram import Bot, Dispatcher, F
from aiogram.types import Message, InlineKeyboardMarkup, InlineKeyboardButton, CallbackQuery, FSInputFile
from aiogram.filters import CommandStart
from ai import generate_story
import os
import uuid
import asyncio
import edge_tts

BOT_TOKEN = os.getenv("BOT_TOKEN")

bot = Bot(token=BOT_TOKEN)
dp = Dispatcher()

# ذاكرة المستخدمين
user_sessions = {}

# نظام الحالة (فوز/خسارة)
user_states = {}

# 🔊 صوت احترافي قوي
async def text_to_voice(text: str, user_id: int):
    filename = f"/tmp/{user_id}_{uuid.uuid4().hex}.mp3"

    # 🔥 صوت رجالي قوي وحاد
    voice = "ar-EG-ShakirNeural"

    communicate = edge_tts.Communicate(text, voice)
    await communicate.save(filename)

    return filename


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
            ],
            [
                InlineKeyboardButton(
                    text="👤 Developer: Ali Hussein",
                    url="https://t.me/alw_sh313"
                )
            ]
        ]
    )


@dp.message(CommandStart())
async def start(message: Message):
    await message.answer(
        "🎭 ━━━ لعبة السيناريو التفاعلية ━━━ 🎭\n\n"
        "👋 أهلاً بك أيها اللاعب...\n\n"
        "🌍 أنت على وشك دخول عالم مليء بالقرارات، المخاطر، والمفاجآت.\n"
        "كل كلمة تكتبها ستؤثر على مجرى القصة بشكل مباشر.\n\n"
        "🎮 دورك:\n"
        "ستكون أنت بطل القصة، وتتحكم بمصيرك بالكامل.\n\n"
        "⚡ هدفك:\n"
        "اتخذ القرارات الصحيحة، واصنع نهايتك الخاصة داخل هذا العالم.\n\n"
        "📌 ملاحظة:\n"
        "لا توجد إجابات صحيحة أو خاطئة... فقط نتائج مختلفة.\n\n"
        "━━━━━━━━━━━━━━━━━━━━\n"
        "اضغط على (🎮 بدء القصة) لبدء مغامرتك الأولى.",
        reply_markup=main_menu()
    )


@dp.callback_query(F.data == "start_story")
async def start_story(callback: CallbackQuery):

    user_id = callback.from_user.id

    user_sessions[user_id] = [
        "ابدأ لعبة RPG جديدة واشرح العالم ودور اللاعب وهدفه ثم ابدأ أول مشهد."
    ]

    user_states[user_id] = {
        "status": "playing",
        "score": 0
    }

    await callback.message.edit_text("⏳ جاري إنشاء القصة...")

    try:
        response = await generate_story(
            "\n".join(user_sessions[user_id])
        )

        user_sessions[user_id].append(f"Bot: {response}")

        voice_file = await text_to_voice(response, user_id)

        await callback.message.answer(
            response,
            reply_markup=main_menu()
        )

        await callback.message.answer_voice(
            FSInputFile(voice_file)
        )

        os.remove(voice_file)

    except Exception as e:
        await callback.message.answer(f"❌ خطأ: {e}")

    await callback.answer()


@dp.callback_query(F.data == "new_story")
async def new_story(callback: CallbackQuery):

    user_id = callback.from_user.id

    user_sessions[user_id] = [
        "ابدأ لعبة RPG جديدة مختلفة تماماً عن السابقة واشرح العالم ودور اللاعب وهدفه ثم ابدأ أول مشهد."
    ]

    user_states[user_id] = {
        "status": "playing",
        "score": 0
    }

    await callback.message.answer("🔄 تم إنشاء قصة جديدة...\n⏳ انتظر قليلاً.")

    try:
        response = await generate_story(
            "\n".join(user_sessions[user_id])
        )

        user_sessions[user_id].append(f"Bot: {response}")

        voice_file = await text_to_voice(response, user_id)

        await callback.message.answer(
            response,
            reply_markup=main_menu()
        )

        await callback.message.answer_voice(
            FSInputFile(voice_file)
        )

        os.remove(voice_file)

    except Exception as e:
        await callback.message.answer(f"❌ خطأ: {e}")

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

    user_sessions[user_id].append(f"User: {user_text}")

    history = "\n".join(user_sessions[user_id])

    state = user_states.get(user_id, {"status": "playing", "score": 0})

    try:
        response = await generate_story(history)

        # 🎯 نظام الفوز والخسارة بدون إنهاء القصة
        text_lower = response.lower()

        if "نجحت" in text_lower or "فزت" in text_lower:
            state["score"] += 1

        if "خسرت" in text_lower or "فشل" in text_lower:
            state["score"] -= 1

        if state["score"] >= 3:
            response += "\n\n🏆 *تشعر أنك تقترب من أسطورة عظيمة داخل هذا العالم...*"

        if state["score"] <= -2:
            response += "\n\n⚠️ *الأحداث أصبحت أصعب عليك، لكن القصة مستمرة...*"

        user_states[user_id] = state

        user_sessions[user_id].append(f"Bot: {response}")

        voice_file = await text_to_voice(response, user_id)

        await message.answer(
            response,
            reply_markup=main_menu()
        )

        await message.answer_voice(
            FSInputFile(voice_file)
        )

        os.remove(voice_file)

    except Exception as e:
        await message.answer(f"❌ خطأ: {e}")
