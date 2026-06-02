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

# =========================
# 👑 إشعار الدخول فقط (كما هو)
# =========================

ADMIN_ID = 8613698275  # غيّرها

# =========================
# 🎮 بيانات النظام (بدون تغيير)
# =========================

user_sessions = {}
user_states = {}
user_modes = {}
user_gender = {}

# =========================
# 🔊 الصوت (فقط تم التعديل هنا)
# =========================

async def text_to_voice(text: str, user_id: int):
    filename = f"/tmp/{user_id}_{uuid.uuid4().hex}.mp3"

    # 🔥 صوت فصيح + أفخم
    voice = "ar-SA-HamedNeural"

    communicate = edge_tts.Communicate(
        text,
        voice,
        rate="-15%"  # بطء خفيف للفهم
    )

    await communicate.save(filename)

    return filename


async def send_voice_later(text, user_id, message):
    try:
        file = await text_to_voice(text, user_id)
        await message.answer_voice(FSInputFile(file))
        os.remove(file)
    except:
        pass


# =========================
# 🎮 القوائم (بدون تغيير)
# =========================

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
            [InlineKeyboardButton(text="🎮 بدء القصة", callback_data="start_story")],
            [InlineKeyboardButton(text="🔄 قصة جديدة", callback_data="new_story")],
            [InlineKeyboardButton(text="👤 Developer: Ali Hussein", url="https://t.me/alw_sh313")]
        ]
    )


def gender_menu():
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(text="👨 ذكر", callback_data="gender_male"),
                InlineKeyboardButton(text="👩 أنثى", callback_data="gender_female")
            ]
        ]
    )


# =========================
# 🎭 الترحيب (بدون تغيير)
# =========================

@dp.message(CommandStart())
async def start(message: Message):

    try:
        await bot.send_message(
            ADMIN_ID,
            f"🔔 دخول مستخدم:\nID: {message.from_user.id}\n@{message.from_user.username}"
        )
    except:
        pass

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


# =========================
# 🎮 باقي النظام (بدون تغيير)
# =========================

@dp.callback_query(F.data == "start_story")
async def start_story(callback: CallbackQuery):

    await callback.message.answer(
        "👤 اختر جنس شخصيتك:",
        reply_markup=gender_menu()
    )

    await callback.answer()


@dp.callback_query(F.data.startswith("gender_"))
async def set_gender(callback: CallbackQuery):

    uid = callback.from_user.id
    gender = callback.data.replace("gender_", "")

    user_gender[uid] = gender

    await callback.message.answer(
        "🎮 اختر نوع القصة:",
        reply_markup=story_modes()
    )

    await callback.answer()


@dp.callback_query(F.data.startswith("mode_"))
async def set_mode(callback: CallbackQuery):

    uid = callback.from_user.id
    mode = callback.data.replace("mode_", "")

    modes_text = {
        "calm": "هدوء",
        "adventure": "مغامرة",
        "fight": "قتال",
        "horror": "رعب",
        "fantasy": "فانتازيا",
        "mystery": "غموض"
    }

    if mode == "random":
        mode = random.choice(list(modes_text.keys()))

    gender = user_gender.get(uid, "غير محدد")

    user_sessions[uid] = [
        f"جنس الشخصية: {gender}",
        f"نوع القصة: {modes_text.get(mode)}",
        "ابدأ القصة وعرّف العالم ودور اللاعب"
    ]

    user_states[uid] = {"score": 0}

    await callback.message.answer("⏳ جاري إنشاء القصة...")

    response = await generate_story("\n".join(user_sessions[uid]))

    user_sessions[uid].append(f"Bot: {response}")

    await callback.message.answer(response, reply_markup=main_menu())
    await callback.message.answer("🔊 جاري إرسال الصوت...")

    asyncio.create_task(send_voice_later(response, uid, callback.message))

    await callback.answer()


@dp.callback_query(F.data == "new_story")
async def new_story(callback: CallbackQuery):

    uid = callback.from_user.id

    user_sessions[uid] = [
        "ابدأ قصة جديدة مختلفة تماماً"
    ]

    user_states[uid] = {"score": 0}

    await callback.message.answer("🔄 جاري إنشاء قصة جديدة...")

    response = await generate_story("\n".join(user_sessions[uid]))

    user_sessions[uid].append(f"Bot: {response}")

    await callback.message.answer(response, reply_markup=main_menu())
    await callback.message.answer("🔊 جاري إرسال الصوت...")

    asyncio.create_task(send_voice_later(response, uid, callback.message))

    await callback.answer()


@dp.message()
async def handle_message(message: Message):

    uid = message.from_user.id
    text = message.text

    if uid not in user_sessions:
        await message.answer("اضغط بدء القصة أولاً", reply_markup=main_menu())
        return

    user_sessions[uid].append(f"User: {text}")

    response = await generate_story("\n".join(user_sessions[uid]))

    user_sessions[uid].append(f"Bot: {response}")

    await message.answer(response, reply_markup=main_menu())
    await message.answer("🔊 جاري إرسال الصوت...")

    asyncio.create_task(send_voice_later(response, uid, message))
