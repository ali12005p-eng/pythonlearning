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

# أنماط القصة
user_modes = {}

# 🔊 الصوت
async def text_to_voice(text: str, user_id: int):
    filename = f"/tmp/{user_id}_{uuid.uuid4().hex}.mp3"

    voice = "ar-EG-ShakirNeural"

    communicate = edge_tts.Communicate(text, voice)
    await communicate.save(filename)

    return filename


async def send_voice_later(text, user_id, message):
    try:
        voice_file = await text_to_voice(text, user_id)
        await message.answer_voice(FSInputFile(voice_file))
        os.remove(voice_file)
    except:
        pass


# 🎮 قائمة الانطباع + العشوائي
def story_modes():
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(text="🌿 هدوء", callback_data="mode_calm"),
                InlineKeyboardButton(text="🧭 مغامرة", callback_data="mode_adventure")
            ],
            [
                InlineKeyboardButton(text="⚔️ قتال", callback_data="mode_fight"),
                InlineKeyboardButton(text="😱 رعب", callback_data="mode_horror")
            ],
            [
                InlineKeyboardButton(text="🏰 فانتازيا", callback_data="mode_fantasy"),
                InlineKeyboardButton(text="🔮 غموض", callback_data="mode_mystery")
            ],
            [
                InlineKeyboardButton(text="🎲 قصة عشوائية", callback_data="mode_random")
            ]
        ]
    )


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
        "🎮 اضغط بدء القصة لاختيار نوع العالم.",
        reply_markup=main_menu()
    )


# 🎮 اختيار نوع القصة
@dp.callback_query(F.data == "start_story")
async def start_story(callback: CallbackQuery):

    await callback.message.answer(
        "🎮 اختر نوع القصة التي تريدها:",
        reply_markup=story_modes()
    )

    await callback.answer()


# 🎲 اختيار الانطباع
@dp.callback_query(F.data.startswith("mode_"))
async def set_mode(callback: CallbackQuery):

    user_id = callback.from_user.id
    mode = callback.data.replace("mode_", "")

    import random

    modes_text = {
        "calm": "قصة هادئة مليئة بالسلام والاستكشاف.",
        "adventure": "مغامرة مليئة بالأحداث المشوقة.",
        "fight": "عالم قتال وحروب وصراعات قوية.",
        "horror": "عالم رعب مظلم وخطير.",
        "fantasy": "عالم فانتازيا وسحر وملوك.",
        "mystery": "عالم غامض مليء بالأسرار.",
    }

    if mode == "random":
        mode = random.choice(list(modes_text.keys()))

    user_modes[user_id] = mode

    user_sessions[user_id] = [
        f"ابدأ لعبة RPG بنوع: {modes_text.get(mode)}",
        "عرّف العالم ودور اللاعب وابدأ أول مشهد حسب هذا الطابع."
    ]

    user_states[user_id] = {
        "status": "playing",
        "score": 0
    }

    await callback.message.answer("⏳ جاري إنشاء القصة حسب اختيارك...")

    try:
        response = await generate_story("\n".join(user_sessions[user_id]))

        user_sessions[user_id].append(f"Bot: {response}")

        await callback.message.answer(
            response,
            reply_markup=main_menu()
        )

        await callback.message.answer("🔊 جاري إرسال القصة بصوت... 🎧")

        asyncio.create_task(
            send_voice_later(response, user_id, callback.message)
        )

    except Exception as e:
        await callback.message.answer(f"❌ خطأ: {e}")

    await callback.answer()


# 🔄 قصة جديدة
@dp.callback_query(F.data == "new_story")
async def new_story(callback: CallbackQuery):

    user_id = callback.from_user.id

    user_sessions[user_id] = [
        "ابدأ لعبة RPG جديدة مختلفة تماماً عن السابقة."
    ]

    user_states[user_id] = {
        "status": "playing",
        "score": 0
    }

    await callback.message.answer("🔄 تم إنشاء قصة جديدة...\n⏳ انتظر قليلاً.")

    try:
        response = await generate_story("\n".join(user_sessions[user_id]))

        user_sessions[user_id].append(f"Bot: {response}")

        await callback.message.answer(
            response,
            reply_markup=main_menu()
        )

        await callback.message.answer("🔊 جاري إرسال القصة بصوت... 🎧")

        asyncio.create_task(
            send_voice_later(response, user_id, callback.message)
        )

    except Exception as e:
        await callback.message.answer(f"❌ خطأ: {e}")

    await callback.answer()


# 💬 التفاعل داخل القصة
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

        text_lower = response.lower()

        if "نجحت" in text_lower or "فزت" in text_lower:
            state["score"] += 1

        if "خسرت" in text_lower or "فشل" in text_lower:
            state["score"] -= 1

        if state["score"] >= 3:
            response += "\n\n🏆 *أنت تقترب من أسطورة عظيمة...*"

        if state["score"] <= -2:
            response += "\n\n⚠️ *الأحداث أصبحت أصعب... لكن القصة مستمرة.*"

        user_states[user_id] = state

        user_sessions[user_id].append(f"Bot: {response}")

        await message.answer(
            response,
            reply_markup=main_menu()
        )

        await message.answer("🔊 جاري إرسال القصة بصوت... 🎧")

        asyncio.create_task(
            send_voice_later(response, user_id, message)
        )

    except Exception as e:
        await message.answer(f"❌ خطأ: {e}")
