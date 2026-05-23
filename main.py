import os
import json
import asyncio
from aiogram import Bot, Dispatcher, F
from aiogram.enums import ChatMemberStatus
from aiogram.filters import CommandStart, Command
from aiogram.types import (
    Message,
    InlineKeyboardMarkup,
    InlineKeyboardButton,
    CallbackQuery
)
from aiogram.client.default import DefaultBotProperties
from aiogram import Router

BOT_TOKEN = os.getenv("BOT_TOKEN")
ADMIN_ID = int(os.getenv("ADMIN_ID", "0"))

CHANNELS_FILE = "channels.json"

router = Router()

def load_channels():
    if not os.path.exists(CHANNELS_FILE):
        return []

    with open(CHANNELS_FILE, "r", encoding="utf-8") as f:
        return json.load(f)

def save_channels(channels):
    with open(CHANNELS_FILE, "w", encoding="utf-8") as f:
        json.dump(channels, f, ensure_ascii=False, indent=4)

async def check_subscription(bot: Bot, user_id: int):
    channels = load_channels()

    for channel in channels:
        try:
            member = await bot.get_chat_member(channel, user_id)

            if member.status not in [
                ChatMemberStatus.MEMBER,
                ChatMemberStatus.ADMINISTRATOR,
                ChatMemberStatus.CREATOR
            ]:
                return False

        except:
            return False

    return True

def subscribe_keyboard():
    channels = load_channels()

    buttons = []

    for channel in channels:
        username = channel.replace("@", "")
        buttons.append([
            InlineKeyboardButton(
                text=f"اشترك بـ {channel}",
                url=f"https://t.me/{username}"
            )
        ])

    buttons.append([
        InlineKeyboardButton(
            text="✅ تحقق",
            callback_data="check_sub"
        )
    ])

    return InlineKeyboardMarkup(inline_keyboard=buttons)

@router.message(CommandStart())
async def start(message: Message, bot: Bot):

    subscribed = await check_subscription(bot, message.from_user.id)

    if not subscribed:
        await message.answer(
            "🌟 اهلاً بك\n\n"
            "يجب الاشتراك بالقنوات التالية أولاً:",
            reply_markup=subscribe_keyboard()
        )
        return

    await message.answer(
        "🎉 اهلاً بك في البوت\n"
        "تم التحقق من اشتراكك بنجاح."
    )

@router.callback_query(F.data == "check_sub")
async def verify_subscription(callback: CallbackQuery, bot: Bot):

    subscribed = await check_subscription(bot, callback.from_user.id)

    if subscribed:
        await callback.message.edit_text(
            "✅ تم التحقق من اشتراكك بنجاح."
        )
    else:
        await callback.answer(
            "❌ لم تشترك بعد.",
            show_alert=True
        )

@router.message(Command("panel"))
async def admin_panel(message: Message):

    if message.from_user.id != ADMIN_ID:
        return

    channels = load_channels()

    text = "⚙️ لوحة الادمن\n\n"

    if channels:
        text += "📢 القنوات الحالية:\n"
        for ch in channels:
            text += f"- {ch}\n"
    else:
        text += "لا توجد قنوات مضافة.\n"

    text += (
        "\n\n➕ إضافة قناة:\n"
        "/addchannel @channel\n\n"
        "➖ حذف قناة:\n"
        "/removechannel @channel"
    )

    await message.answer(text)

@router.message(Command("addchannel"))
async def add_channel(message: Message):

    if message.from_user.id != ADMIN_ID:
        return

    args = message.text.split()

    if len(args) < 2:
        await message.answer("❌ استخدم:\n/addchannel @channel")
        return

    channel = args[1]

    channels = load_channels()

    if channel in channels:
        await message.answer("⚠️ القناة مضافة مسبقاً.")
        return

    channels.append(channel)
    save_channels(channels)

    await message.answer(f"✅ تمت إضافة {channel}")

@router.message(Command("removechannel"))
async def remove_channel(message: Message):

    if message.from_user.id != ADMIN_ID:
        return

    args = message.text.split()

    if len(args) < 2:
        await message.answer("❌ استخدم:\n/removechannel @channel")
        return

    channel = args[1]

    channels = load_channels()

    if channel not in channels:
        await message.answer("❌ القناة غير موجودة.")
        return

    channels.remove(channel)
    save_channels(channels)

    await message.answer(f"✅ تم حذف {channel}")

@router.message(F.chat.type.in_({"group", "supergroup"}))
async def force_sub(message: Message, bot: Bot):

    try:
        member = await bot.get_chat_member(
            message.chat.id,
            message.from_user.id
        )

        if member.status in [
            ChatMemberStatus.ADMINISTRATOR,
            ChatMemberStatus.CREATOR
        ]:
            return
    except:
        pass

    subscribed = await check_subscription(bot, message.from_user.id)

    if not subscribed:

        try:
            await message.delete()

            await message.answer(
                f"🚫 {message.from_user.full_name}\n"
                "يجب الاشتراك بالقنوات أولاً.",
                reply_markup=subscribe_keyboard()
            )
        except:
            pass

async def main():

    bot = Bot(
        token=BOT_TOKEN,
        default=DefaultBotProperties(parse_mode="HTML")
    )

    dp = Dispatcher()
    dp.include_router(router)

    print("Bot Started...")

    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
