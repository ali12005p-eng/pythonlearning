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
# 👑 إشعار دخول
# =========================

ADMIN_ID = 8613698275

# =========================
# 🎮 بيانات النظام
# =========================

user_sessions = {}
user_states = {}
user_modes = {}
user_gender = {}
user_xp = {}
user_level = {}

# =========================
# 🎬 مؤثر سينمائي
# =========================

def cinematic_text(text: str) -> str:
    text = text.replace(".", ". ..")
    text = text.replace("،", "، ..")
    text = text.replace("!", "! ..")
    text = text.replace("؟", "؟ ..")
    return text


# =========================
# 🎭 تحديد المزاج
# =========================

def detect_mood(text: str) -> str:
    text = text.lower()

    if "قتل" in text or "سيف" in text or "هجوم" in text:
        return "fight"

    if "خوف" in text or "ظلام" in text or "صرخة" in text:
        return "horror"

    if "رحلة" in text or "طريق" in text or "سفر" in text:
        return "adventure"

    if "سر" in text or "غامض" in text:
        return "mystery"

    return "calm"


# =========================
# 🎼 الموسيقى
# =========================

def get_music_by_mood(mood: str) -> str:
    music_map = {
        "fight": "https://example.com/music/fight.mp3",
        "horror": "https://example.com/music/horror.mp3",
        "adventure": "https://example.com/music/adventure.mp3",
        "mystery": "https://example.com/music/mystery.mp3",
        "calm": "https://example.com/music/calm.mp3"
    }
    return music_map.get(mood, music_map["calm"])


async def send_music(text, message):
    try:
        mood = detect_mood(text)
        music_url = get_music_by_mood(mood)

        await message.answer_audio(
            audio=music_url,
            caption="🎬 موسيقى سينمائية حسب المشهد"
        )
    except:
        pass


# =========================
# 🔊 الصوت
# =========================

async def text_to_voice(text: str, user_id: int):
    filename = f"/tmp/{user_id}_{uuid.uuid4().hex}.mp3"

    mood = detect_mood(text)

    voice = "ar-SA-HamedNeural"
    rate = "-15%"

    if mood == "fight":
        rate = "+5%"
    elif mood == "horror":
        rate = "-25%"
    elif mood == "mystery":
        rate = "-20%"
    elif mood == "adventure":
        rate = "-10%"

    communicate = edge_tts.Communicate(
        cinematic_text(text),
        voice,
        rate=rate
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
# 🎮 القوائم
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
# 🎭 START (تم التعديل فقط هنا)
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

    # =========================
    # 📸 تم إضافة الصورة فقط هنا
    # =========================
    photo = FSInputFile("C684B819-55BE-496C-84F0-FCEF39A0DF10.PNG")

    await message.answer_photo(
        photo=photo,
        caption=(
            "━━━━━━━━━━━━━━━━━━\n"
            "🎭✨ أهلاً بك في عالم السيناريوهات التفاعلية ✨🎭\n"
            "⚔️ هنا لا توجد قصة مكتوبة مسبقاً… بل أنت من يصنع المصير\n\n"
            "🌍 عالم حي يتغير مع كل قرار تتخذه\n"
            "🧠 شخصيات تتذكرك… وأحداث تتطور معك\n"
            "🔥 نجاحك يصنع أسطورتك… وخسارتك تصنع بداية جديدة\n\n"
            "🎮 هل لديك الجرأة لبدء الرحلة؟\n"
            "اضغط (بدء القصة) الآن وابدأ مغامرتك\n"
            "━━━━━━━━━━━━━━━━━━"
        ),
        reply_markup=main_menu()
    )


# =========================
# باقي الكود بدون تغيير
# =========================

@dp.callback_query(F.data == "start_story")
async def start_story(callback: CallbackQuery):
    await callback.message.answer("👤 اختر الجنس:", reply_markup=gender_menu())
    await callback.answer()


@dp.callback_query(F.data.startswith("gender_"))
async def set_gender(callback: CallbackQuery):

    uid = callback.from_user.id
    gender = callback.data.replace("gender_", "")

    user_gender[uid] = gender

    await callback.message.answer("🎮 اختر نوع القصة:", reply_markup=story_modes())
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
        "ابدأ القصة"
    ]

    user_states[uid] = {"score": 0}

    if uid not in user_xp:
        user_xp[uid] = 0

    if uid not in user_level:
        user_level[uid] = 1

    await callback.message.answer("⏳ جاري إنشاء القصة...")

    response = await generate_story("\n".join(user_sessions[uid]))

    user_sessions[uid].append(f"Bot: {response}")

    await callback.message.answer(response, reply_markup=main_menu())
    await callback.message.answer("🔊 جاري الصوت...")

    asyncio.create_task(send_voice_later(response, uid, callback.message))
    asyncio.create_task(send_music(response, callback.message))

    await callback.answer()


@dp.callback_query(F.data == "new_story")
async def new_story(callback: CallbackQuery):

    uid = callback.from_user.id

    user_sessions[uid] = ["ابدأ قصة جديدة"]
    user_states[uid] = {"score": 0}

    await callback.message.answer("🔄 جاري القصة...")

    response = await generate_story("\n".join(user_sessions[uid]))

    user_sessions[uid].append(f"Bot: {response}")

    await callback.message.answer(response, reply_markup=main_menu())
    await callback.message.answer("🔊 جاري الصوت...")

    asyncio.create_task(send_voice_later(response, uid, callback.message))
    asyncio.create_task(send_music(response, callback.message))

    await callback.answer()


@dp.message()
async def handle_message(message: Message):

    uid = message.from_user.id
    text = message.text

    if uid not in user_sessions:
        await message.answer("اضغط بدء القصة", reply_markup=main_menu())
        return

    user_sessions[uid].append(f"User: {text}")

    user_xp[uid] = user_xp.get(uid, 0) + random.randint(5, 15)

    level_up_text = ""

    new_level = (user_xp[uid] // 100) + 1

    if uid not in user_level:
        user_level[uid] = 1

    if new_level > user_level[uid]:
        user_level[uid] = new_level
        level_up_text = f"\n\n🎉 ترقية مستوى!\n⭐ المستوى: {new_level}"

    response = await generate_story("\n".join(user_sessions[uid]))

    stats = f"""
━━━━━━━━━━━━━━
⭐ المستوى: {user_level[uid]}
✨ الخبرة: {user_xp[uid]} XP
━━━━━━━━━━━━━━
"""

    user_sessions[uid].append(f"Bot: {response}")

    await message.answer(
        response + level_up_text + stats,
        reply_markup=main_menu()
    )

    await message.answer("🔊 جاري الصوت...")

    asyncio.create_task(send_voice_later(response, uid, message))
    asyncio.create_task(send_music(response, message))
