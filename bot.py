from aiogram import Bot, Dispatcher, F
from aiogram.types import (
    Message,
    InlineKeyboardMarkup,
    InlineKeyboardButton,
    CallbackQuery,
    FSInputFile
)
from aiogram.filters import CommandStart

from ai import generate_story, generate_summary

from database import (
    init_db,
    user_exists,
    create_user,
    get_user,
    update_history,
    update_summary,
    update_xp_level,
    get_message_count,
    update_message_count,
    set_voice
)

import os
import uuid
import asyncio
import edge_tts
import random

BOT_TOKEN = os.getenv("BOT_TOKEN")

bot = Bot(token=BOT_TOKEN)
dp = Dispatcher()

init_db()

ADMIN_ID = 8613698275


# =========================
# حفظ مؤقت أثناء إنشاء الشخصية
# =========================

user_gender = {}
user_story_type = {}
waiting_name = {}


# =========================
# مؤثر سينمائي
# =========================

def cinematic_text(text: str) -> str:
    text = text.replace(".", ". ..")
    text = text.replace("،", "، ..")
    text = text.replace("!", "! ..")
    text = text.replace("؟", "؟ ..")
    return text


# =========================
# تحديد المزاج
# =========================

def detect_mood(text: str) -> str:

    text = text.lower()

    if "قتل" in text or "سيف" in text or "هجوم" in text:
        return "fight"

    if "خوف" in text or "ظلام" in text or "صرخة" in text:
        return "horror"

    if "رحلة" in text or "سفر" in text:
        return "adventure"

    if "سر" in text or "غامض" in text:
        return "mystery"

    return "calm"


# =========================
# صوت
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

        user = get_user(user_id)

        if not user:
            return

        voice_enabled = bool(user[8])

        if not voice_enabled:
            return

        file = await text_to_voice(text, user_id)

        await message.answer_voice(
            FSInputFile(file)
        )

        os.remove(file)

    except:
        pass


# =========================
# القوائم
# =========================

def gender_menu():

    return InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(
                    text="👨 ذكر",
                    callback_data="gender_male"
                ),
                InlineKeyboardButton(
                    text="👩 أنثى",
                    callback_data="gender_female"
                )
            ]
        ]
    )


def story_modes():

    return InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(
                    text="🌿 هدوء",
                    callback_data="mode_calm"
                ),
                InlineKeyboardButton(
                    text="🧭 مغامرة",
                    callback_data="mode_adventure"
                )
            ],
            [
                InlineKeyboardButton(
                    text="⚔️ قتال",
                    callback_data="mode_fight"
                ),
                InlineKeyboardButton(
                    text="😱 رعب",
                    callback_data="mode_horror"
                )
            ],
            [
                InlineKeyboardButton(
                    text="🏰 فانتازيا",
                    callback_data="mode_fantasy"
                ),
                InlineKeyboardButton(
                    text="🔮 غموض",
                    callback_data="mode_mystery"
                )
            ]
        ]
    )


def main_menu():

    return InlineKeyboardMarkup(
        inline_keyboard=[

            [
                InlineKeyboardButton(
                    text="🎭 شخصيتي",
                    callback_data="my_character"
                )
            ],

            [
                InlineKeyboardButton(
                    text="📖 ملخص القصة",
                    callback_data="story_summary"
                )
            ],

            [
                InlineKeyboardButton(
                    text="🔊 تشغيل/إيقاف الصوت",
                    callback_data="toggle_voice"
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
    # =========================
# START
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

    if user_exists(message.from_user.id):

        user = get_user(message.from_user.id)

        await message.answer(
            f"🎭 مرحباً بعودتك {user[1]}\n\n"
            f"قصتك ما زالت مستمرة داخل عالم {user[3]}",
            reply_markup=main_menu()
        )

        return

    photo = FSInputFile(
        "C684B819-55BE-496C-84F0-FCEF39A0DF10.PNG"
    )

    await message.answer_photo(
        photo=photo,
        caption=(
            "🎭 أهلاً بك في عالم السيناريوهات التفاعلية\n\n"
            "⚠️ تنبيه مهم\n\n"
            "بعد إنشاء شخصيتك لن تستطيع:\n"
            "• تغيير الاسم\n"
            "• تغيير الجنس\n"
            "• تغيير نوع العالم\n\n"
            "وستعيش بهذه الشخصية طوال رحلتك."
        )
    )

    await message.answer(
        "👤 اختر جنس الشخصية:",
        reply_markup=gender_menu()
    )


# =========================
# اختيار الجنس
# =========================

@dp.callback_query(F.data.startswith("gender_"))
async def choose_gender(callback: CallbackQuery):

    uid = callback.from_user.id

    gender = callback.data.replace(
        "gender_",
        ""
    )

    user_gender[uid] = gender

    await callback.message.answer(
        "🌍 اختر نوع العالم:"
    )

    await callback.message.answer(
        "اختر نوع قصتك:",
        reply_markup=story_modes()
    )

    await callback.answer()


# =========================
# اختيار العالم
# =========================

@dp.callback_query(F.data.startswith("mode_"))
async def choose_mode(callback: CallbackQuery):

    uid = callback.from_user.id

    mode = callback.data.replace(
        "mode_",
        ""
    )

    names = {
        "calm": "هدوء",
        "adventure": "مغامرة",
        "fight": "قتال",
        "horror": "رعب",
        "fantasy": "فانتازيا",
        "mystery": "غموض"
    }

    user_story_type[uid] = names.get(
        mode,
        mode
    )

    waiting_name[uid] = True

    await callback.message.answer(
        "✍️ اكتب اسم شخصيتك الآن:"
    )

    await callback.answer()


# =========================
# إنشاء الشخصية
# =========================

@dp.message()
async def create_character(message: Message):

    uid = message.from_user.id

    if uid not in waiting_name:
        return

    character_name = message.text.strip()

    if len(character_name) < 2:

        await message.answer(
            "❌ الاسم قصير جداً"
        )

        return

    create_user(
        user_id=uid,
        character_name=character_name,
        gender=user_gender[uid],
        story_type=user_story_type[uid]
    )

    waiting_name.pop(uid)

    await message.answer(
        "⏳ يتم إنشاء عالمك الخاص..."
    )

    response = await generate_story(
        character_name,
        user_gender[uid],
        user_story_type[uid],
        "",
        "",
        "بداية القصة"
    )

    update_history(
        uid,
        response
    )

    await message.answer(
        response,
        reply_markup=main_menu()
    )

    asyncio.create_task(
        send_voice_later(
            response,
            uid,
            message
        )
    )
    # =========================
# شخصيتي
# =========================

@dp.callback_query(F.data == "my_character")
async def my_character(callback: CallbackQuery):

    user = get_user(
        callback.from_user.id
    )

    if not user:
        await callback.answer()
        return

    text = (
        f"🎭 معلومات الشخصية\n\n"
        f"👤 الاسم: {user[1]}\n"
        f"⚧ الجنس: {user[2]}\n"
        f"🌍 العالم: {user[3]}\n\n"
        f"⭐ المستوى: {user[4]}\n"
        f"✨ الخبرة: {user[5]} XP"
    )

    await callback.message.answer(text)

    await callback.answer()


# =========================
# ملخص القصة
# =========================

@dp.callback_query(F.data == "story_summary")
async def story_summary_handler(
    callback: CallbackQuery
):

    user = get_user(
        callback.from_user.id
    )

    if not user:
        await callback.answer()
        return

    summary = user[6]

    if not summary:
        summary = "لا يوجد ملخص بعد."

    await callback.message.answer(
        f"📖 ملخص القصة\n\n{summary}"
    )

    await callback.answer()


# =========================
# تشغيل وإيقاف الصوت
# =========================

@dp.callback_query(F.data == "toggle_voice")
async def toggle_voice(callback: CallbackQuery):

    user = get_user(
        callback.from_user.id
    )

    if not user:
        await callback.answer()
        return

    current = bool(user[8])

    set_voice(
        callback.from_user.id,
        not current
    )

    if current:
        text = "🔇 تم إيقاف الصوت"
    else:
        text = "🔊 تم تشغيل الصوت"

    await callback.message.answer(text)

    await callback.answer()


# =========================
# متابعة القصة
# =========================

@dp.message()
async def continue_story(message: Message):

    uid = message.from_user.id

    if uid in waiting_name:
        return

    if not user_exists(uid):
        return

    user = get_user(uid)

    character_name = user[1]
    gender = user[2]
    story_type = user[3]

    level = user[4]
    xp = user[5]

    summary = user[6] or ""
    history = user[7] or ""

    player_action = message.text

    xp += random.randint(5, 15)

    new_level = (xp // 100) + 1

    level_up_text = ""

    if new_level > level:
        level = new_level

        level_up_text = (
            f"\n\n🎉 ترقية مستوى!\n"
            f"⭐ المستوى الجديد: {level}"
        )

    response = await generate_story(
        character_name,
        gender,
        story_type,
        summary,
        history,
        player_action
    )

    history_lines = history.split("\n")

    history_lines.append(
        f"اللاعب: {player_action}"
    )

    history_lines.append(
        f"القصة: {response}"
    )

    history_lines = history_lines[-20:]

    new_history = "\n".join(
        history_lines
    )

    update_history(
        uid,
        new_history
    )

    update_xp_level(
        uid,
        xp,
        level
    )

    count = get_message_count(uid)

    count += 1

    update_message_count(
        uid,
        count
    )

    # تحديث الملخص كل 10 رسائل

    if count % 10 == 0:

        try:

            new_summary = await generate_summary(
                summary,
                new_history
            )

            update_summary(
                uid,
                new_summary
            )

        except:
            pass

    stats = (
        f"\n\n━━━━━━━━━━━━━━\n"
        f"⭐ المستوى: {level}\n"
        f"✨ الخبرة: {xp} XP\n"
        f"━━━━━━━━━━━━━━"
    )

    await message.answer(
        response +
        level_up_text +
        stats,
        reply_markup=main_menu()
    )

    asyncio.create_task(
        send_voice_later(
            response,
            uid,
            message
        )
    )
