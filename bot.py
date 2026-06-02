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
# 🔥 بيانات النظام
# =========================

ADMIN_ID = 8613698275  # غيّرها

user_sessions = {}
user_states = {}
user_modes = {}
user_gender = {}
blocked_users = set()

# 👑 وضع الأدمن
admin_state = {}  # broadcast / ban / unban


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
        file = await text_to_voice(text, user_id)
        await message.answer_voice(FSInputFile(file))
        os.remove(file)
    except:
        pass


# =========================
# 🎮 القوائم
# =========================

def main_menu():
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text="🎮 بدء القصة", callback_data="start_story")],
            [InlineKeyboardButton(text="🔄 قصة جديدة", callback_data="new_story")]
        ]
    )


def admin_panel():
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text="🚫 حظر مستخدم", callback_data="ban_mode")],
            [InlineKeyboardButton(text="✅ إلغاء حظر", callback_data="unban_mode")],
            [InlineKeyboardButton(text="📢 إذاعة", callback_data="broadcast_mode")]
        ]
    )


# =========================
# 🎭 ترحيب (كما طلبت EXACT)
# =========================

@dp.message(CommandStart())
async def start(message: Message):

    await bot.send_message(
        ADMIN_ID,
        f"🔔 دخول مستخدم:\nID: {message.from_user.id}\n@{message.from_user.username}"
    )

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
# 👑 لوحة الأدمن
# =========================

@dp.message(F.text == "/admin")
async def admin(message: Message):
    if message.from_user.id != ADMIN_ID:
        return

    await message.answer("👑 لوحة الأدمن:", reply_markup=admin_panel())


# =========================
# 🚫 اختيار وضع الحظر
# =========================

@dp.callback_query(F.data == "ban_mode")
async def ban_mode(callback: CallbackQuery):
    if callback.from_user.id != ADMIN_ID:
        return

    admin_state[ADMIN_ID] = "ban"
    await callback.message.answer("أرسل ID المستخدم للحظر الآن")
    await callback.answer()


# =========================
# ✅ إلغاء الحظر
# =========================

@dp.callback_query(F.data == "unban_mode")
async def unban_mode(callback: CallbackQuery):
    if callback.from_user.id != ADMIN_ID:
        return

    admin_state[ADMIN_ID] = "unban"
    await callback.message.answer("أرسل ID المستخدم لإلغاء الحظر")
    await callback.answer()


# =========================
# 📢 الإذاعة (FIX الحقيقي)
# =========================

@dp.callback_query(F.data == "broadcast_mode")
async def broadcast_mode(callback: CallbackQuery):
    if callback.from_user.id != ADMIN_ID:
        return

    admin_state[ADMIN_ID] = "broadcast"
    await callback.message.answer("📢 أرسل الرسالة الآن للإذاعة لجميع المستخدمين")
    await callback.answer()


# =========================
# 💬 معالجة الرسائل (FIX كامل للأدمن)
# =========================

@dp.message()
async def handle_message(message: Message):

    uid = message.from_user.id

    # 🚫 تنفيذ أوامر الأدمن أولاً (IMPORTANT FIX)
    if uid == ADMIN_ID and ADMIN_ID in admin_state:

        mode = admin_state[ADMIN_ID]

        # 🚫 حظر مستخدم
        if mode == "ban":
            blocked_users.add(int(message.text))
            await message.answer("🚫 تم الحظر")
            admin_state.pop(ADMIN_ID)
            return

        # ✅ إلغاء الحظر
        if mode == "unban":
            blocked_users.discard(int(message.text))
            await message.answer("✅ تم إلغاء الحظر")
            admin_state.pop(ADMIN_ID)
            return

        # 📢 إذاعة
        if mode == "broadcast":
            for user_id in user_sessions.keys():
                try:
                    await bot.send_message(user_id, f"📢 إعلان:\n\n{message.text}")
                except:
                    pass

            await message.answer("✅ تم إرسال الإذاعة")
            admin_state.pop(ADMIN_ID)
            return

    # 🚫 منع المحظورين
    if uid in blocked_users:
        return

    # 🎮 بداية القصة
    if uid not in user_sessions:
        await message.answer("اضغط بدء القصة أولاً", reply_markup=main_menu())
        return

    user_sessions[uid].append(f"User: {message.text}")

    response = await generate_story("\n".join(user_sessions[uid]))

    user_sessions[uid].append(f"Bot: {response}")

    await message.answer(response, reply_markup=main_menu())
    await message.answer("🔊 جاري إرسال الصوت...")

    asyncio.create_task(send_voice_later(response, uid, message))


# =========================
# 🚫 الحظر (يدوي عبر النظام الجديد)
# =========================

@dp.callback_query(F.data == "ban")
async def ban(callback: CallbackQuery):
    if callback.from_user.id != ADMIN_ID:
        return
    await callback.answer()
