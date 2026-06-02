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
# 🔥 إضافات جديدة فقط
# =========================

ADMIN_ID = 8613698275  # ⚠️ غيّرها إلى ID مالك البوت

user_sessions = {}
user_states = {}
user_modes = {}
user_gender = {}
blocked_users = set()


# =========================
# 🔊 الصوت
# =========================

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


def gender_menu():
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(text="👨 ذكر", callback_data="gender_male"),
                InlineKeyboardButton(text="👩 أنثى", callback_data="gender_female")
            ]
        ]
    )


def admin_panel():
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(text="🚫 حظر", callback_data="ban")
            ],
            [
                InlineKeyboardButton(text="✅ إلغاء الحظر", callback_data="unban")
            ],
            [
                InlineKeyboardButton(text="📢 إذاعة", callback_data="broadcast")
            ]
        ]
    )


# =========================
# 🎭 الترحيب (كما هو بدون تغيير)
# =========================

@dp.message(CommandStart())
async def start(message: Message):

    # 🔔 إشعار دخول للأدمن
    await bot.send_message(
        ADMIN_ID,
        f"🔔 مستخدم دخل البوت:\nID: {message.from_user.id}\nUsername: @{message.from_user.username}"
    )

    await message.answer(
        "🎭 أهلاً بك في لعبة السيناريوهات التفاعلية!\n\n"
        "اضغط على زر (بدء القصة) للبدء.",
        reply_markup=main_menu()
    )


# =========================
# 🚫 منع المحظورين
# =========================

def is_blocked(user_id: int):
    return user_id in blocked_users


# =========================
# 🎮 بدء القصة
# =========================

@dp.callback_query(F.data == "start_story")
async def start_story(callback: CallbackQuery):

    if is_blocked(callback.from_user.id):
        return

    await callback.message.answer(
        "👤 اختر جنس شخصيتك:",
        reply_markup=gender_menu()
    )

    await callback.answer()


# =========================
# 👤 اختيار الجنس
# =========================

@dp.callback_query(F.data.startswith("gender_"))
async def set_gender(callback: CallbackQuery):

    user_id = callback.from_user.id
    gender = callback.data.replace("gender_", "")

    user_gender[user_id] = gender

    gender_text = "ذكر شجاع" if gender == "male" else "أنثى قوية"

    await callback.message.answer(
        f"✅ شخصيتك: {gender_text}\nالآن اختر نوع القصة 👇",
        reply_markup=story_modes()
    )

    await callback.answer()


# =========================
# 🎲 اختيار النمط
# =========================

@dp.callback_query(F.data.startswith("mode_"))
async def set_mode(callback: CallbackQuery):

    if is_blocked(callback.from_user.id):
        return

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

    gender = user_gender.get(user_id, "غير محدد")

    user_modes[user_id] = mode

    user_sessions[user_id] = [
        f"جنس الشخصية: {gender}",
        f"نوع القصة: {modes_text.get(mode)}",
        "ابدأ القصة وعرّف العالم ودور اللاعب."
    ]

    user_states[user_id] = {"status": "playing", "score": 0}

    await callback.message.answer("⏳ جاري إنشاء القصة...")

    try:
        response = await generate_story("\n".join(user_sessions[user_id]))

        user_sessions[user_id].append(f"Bot: {response}")

        await callback.message.answer(response, reply_markup=main_menu())
        await callback.message.answer("🔊 جاري إرسال القصة بصوت... 🎧")

        asyncio.create_task(send_voice_later(response, user_id, callback.message))

    except Exception as e:
        await callback.message.answer(f"❌ خطأ: {e}")

    await callback.answer()


# =========================
# 🔄 قصة جديدة
# =========================

@dp.callback_query(F.data == "new_story")
async def new_story(callback: CallbackQuery):

    if is_blocked(callback.from_user.id):
        return

    user_id = callback.from_user.id

    user_sessions[user_id] = [
        "ابدأ لعبة RPG جديدة مختلفة تماماً."
    ]

    user_states[user_id] = {"status": "playing", "score": 0}

    await callback.message.answer("🔄 تم إنشاء قصة جديدة...")

    try:
        response = await generate_story("\n".join(user_sessions[user_id]))

        user_sessions[user_id].append(f"Bot: {response}")

        await callback.message.answer(response, reply_markup=main_menu())
        await callback.message.answer("🔊 جاري إرسال القصة بصوت... 🎧")

        asyncio.create_task(send_voice_later(response, user_id, callback.message))

    except Exception as e:
        await callback.message.answer(f"❌ خطأ: {e}")

    await callback.answer()


# =========================
# 💬 التفاعل داخل القصة
# =========================

@dp.message()
async def handle_message(message: Message):

    user_id = message.from_user.id

    if is_blocked(user_id):
        return

    if user_id not in user_sessions:
        await message.answer(
            "🎭 أهلاً بك في لعبة السيناريوهات التفاعلية!\n\n"
            "اضغط على زر (بدء القصة) للبدء.",
            reply_markup=main_menu()
        )
        return

    user_sessions[user_id].append(f"User: {message.text}")

    history = "\n".join(user_sessions[user_id])

    state = user_states.get(user_id, {"status": "playing", "score": 0})

    try:
        response = await generate_story(history)

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


# =========================
# 👑 لوحة الأدمن
# =========================

@dp.message(F.text == "/admin")
async def admin(message: Message):

    if message.from_user.id != ADMIN_ID:
        return

    await message.answer("👑 لوحة الأدمن:", reply_markup=admin_panel())


# =========================
# 🚫 حظر
# =========================

@dp.callback_query(F.data == "ban")
async def ban(callback: CallbackQuery):

    if callback.from_user.id != ADMIN_ID:
        return

    blocked_users.add(callback.from_user.id)

    await callback.message.answer("🚫 تم الحظر (تجريبي)")
    await callback.answer()


# =========================
# ✅ إلغاء الحظر
# =========================

@dp.callback_query(F.data == "unban")
async def unban(callback: CallbackQuery):

    if callback.from_user.id != ADMIN_ID:
        return

    blocked_users.clear()

    await callback.message.answer("✅ تم إلغاء الحظر")
    await callback.answer()


# =========================
# 📢 إذاعة (Broadcast بسيط)
# =========================

@dp.callback_query(F.data == "broadcast")
async def broadcast(callback: CallbackQuery):

    if callback.from_user.id != ADMIN_ID:
        return

    await callback.message.answer("📢 أرسل الرسالة الآن")

    @dp.message()
    async def send(message: Message):

        if message.from_user.id != ADMIN_ID:
            return

        for uid in user_sessions.keys():
            try:
                await bot.send_message(uid, f"📢 إعلان:\n\n{message.text}")
            except:
                pass

        await message.answer("✅ تم الإرسال")
