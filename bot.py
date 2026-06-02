from aiogram import Bot, Dispatcher, F
from aiogram.types import Message, InlineKeyboardMarkup, InlineKeyboardButton, CallbackQuery, FSInputFile
from aiogram.filters import CommandStart
from ai import generate_story
import os
import uuid
import asyncio
import edge_tts
import random

BOT_TOKEN = os.getenv("BOT_TOKEN")

bot = Bot(token=BOT_TOKEN)
dp = Dispatcher()

user_sessions = {}
user_states = {}
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


# ✨ تشكيل أقوى للنص (نسخة مطورة)
def full_diacritics(text: str) -> str:
    replacements = {
        "انت": "أَنْتَ",
        "أنت": "أَنْتَ",
        "قصة": "قِصَّةٌ",
        "العالم": "الْعَالَمُ",
        "عالم": "عَالَمٌ",
        "الملك": "الْمَلِكُ",
        "ملك": "مَلِكٌ",
        "سيف": "سَيْفٌ",
        "مغامرة": "مُغَامَرَةٌ",
        "رعب": "رُعْبٌ",
        "قرار": "قَرَارٌ",
        "أحداث": "أَحْدَاثٌ",
        "بطل": "بَطَلٌ",
        "قوي": "قَوِيٌّ",
        "غامض": "غَامِضٌ"
    }

    # محاولة تحسين تشكيل الجمل
    for k, v in replacements.items():
        text = text.replace(k, v)

    return text


# 🎮 اختيار الأنماط
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
                InlineKeyboardButton(text="🎮 بدء القصة", callback_data="start_story")
            ],
            [
                InlineKeyboardButton(text="🔄 قصة جديدة", callback_data="new_story")
            ],
            [
                InlineKeyboardButton(
                    text="👤 Developer: Ali Hussein",
                    url="https://t.me/alw_sh313"
                )
            ]
        ]
    )


# 🎭 ترحيب أفخم (جديد)
@dp.message(CommandStart())
async def start(message: Message):
    await message.answer(
        "🎭━━━━━━━━━━━━━━━━━━🎭\n"
        "✨ أهلاً بك في *عالم السيناريوهات التفاعلية* ✨\n"
        "🎮 لعبة لا تعتمد على الحظ… بل على قراراتك أنت!\n\n"
        "🌍 ستدخل عالماً حيّاً يتغير مع كل كلمة تكتبها\n"
        "⚔️ ستواجه أحداثاً، مخاطر، ومصائر مجهولة\n"
        "🎯 وكل قرار منك يصنع نهايتك الخاصة\n\n"
        "🧠 هل أنت مستعد لتكون بطل القصة؟\n"
        "🎮 اضغط (بدء القصة) وابدأ رحلتك الآن\n"
        "🎭━━━━━━━━━━━━━━━━━━🎭",
        reply_markup=main_menu()
    )


# 🎮 بدء القصة
@dp.callback_query(F.data == "start_story")
async def start_story(callback: CallbackQuery):

    await callback.message.answer(
        "🎮 اختر نوع القصة التي تريدها:",
        reply_markup=story_modes()
    )

    await callback.answer()


# 🎲 اختيار النمط
@dp.callback_query(F.data.startswith("mode_"))
async def set_mode(callback: CallbackQuery):

    user_id = callback.from_user.id
    mode = callback.data.replace("mode_", "")

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

    user_states[user_id] = {"status": "playing", "score": 0}

    await callback.message.answer("⏳ جاري إنشاء القصة...")

    try:
        response = await generate_story("\n".join(user_sessions[user_id]))

        response = full_diacritics(response)

        user_sessions[user_id].append(f"Bot: {response}")

        await callback.message.answer(response, reply_markup=main_menu())
        await callback.message.answer("🔊 جاري إرسال القصة بصوت... 🎧")

        asyncio.create_task(send_voice_later(response, user_id, callback.message))

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

    user_states[user_id] = {"status": "playing", "score": 0}

    await callback.message.answer("🔄 تم إنشاء قصة جديدة...\n⏳ انتظر قليلاً.")

    try:
        response = await generate_story("\n".join(user_sessions[user_id]))

        response = full_diacritics(response)

        user_sessions[user_id].append(f"Bot: {response}")

        await callback.message.answer(response, reply_markup=main_menu())
        await callback.message.answer("🔊 جاري إرسال القصة بصوت... 🎧")

        asyncio.create_task(send_voice_later(response, user_id, callback.message))

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
            "🎭━━━━━━━━━━━━━━━━━━🎭\n"
            "✨ أهلاً بك في *عالم السيناريوهات التفاعلية* ✨\n"
            "🎮 اضغط (بدء القصة) لتبدأ مغامرتك\n"
            "🎭━━━━━━━━━━━━━━━━━━🎭",
            reply_markup=main_menu()
        )
        return

    user_sessions[user_id].append(f"User: {user_text}")

    history = "\n".join(user_sessions[user_id])
    state = user_states.get(user_id, {"status": "playing", "score": 0})

    try:
        response = await generate_story(history)

        response = full_diacritics(response)

        text_lower = response.lower()

        if "نجحت" in text_lower or "فزت" in text_lower:
            state["score"] += 1

        if "خسرت" in text_lower or "فشل" in text_lower:
            state["score"] -= 1

        user_states[user_id] = state
        user_sessions[user_id].append(f"Bot: {response}")

        await message.answer(response, reply_markup=main_menu())
        await message.answer("🔊 جاري إرسال القصة بصوت... 🎧")

        asyncio.create_task(send_voice_later(response, user_id, message))

    except Exception as e:
        await message.answer(f"❌ خطأ: {e}")
