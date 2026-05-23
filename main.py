import os
import json
import asyncio

from aiogram import Bot, Dispatcher, Router, F
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ChatMemberStatus
from aiogram.filters import CommandStart, Command
from aiogram.types import (
    Message,
    InlineKeyboardMarkup,
    InlineKeyboardButton,
    CallbackQuery
)

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


async def is_subscribed(bot: Bot, user_id: int):

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


def subscription_keyboard():

    channels = load_channels()

    buttons = []

    for channel in channels:

        username = channel.replace("@", "")

        buttons.append([
            InlineKeyboardButton(
                text=f"📢 {channel}",
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


def admin_panel_keyboard():

    keyboard = InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(
                    text="➕ إضافة قناة",
                    callback_data="add_channel"
                )
            ],
            [
                InlineKeyboardButton(
                    text="➖ حذف قناة",
                    callback_data="remove_channel"
                )
            ],
            [
                InlineKeyboardButton(
                    text="📋 عرض القنوات",
                    callback_data="show_channels"
                )
            ]
        ]
    )

    return keyboard


@router.message(CommandStart())
async def start(message: Message, bot: Bot):

    subscribed = await is_subscribed(bot, message.from_user.id)

    if not subscribed:

        await message.answer(
            "🌟 اهلاً بك عزيزي\n\n"
            "للدخول للبوت يجب الاشتراك بالقنوات التالية:",
            reply_markup=subscription_keyboard()
        )

        return

    await message.answer(
        "🎉 اهلاً بك في البوت\n"
        "تم التحقق من اشتراكك بنجاح."
    )


@router.callback_query(F.data == "check_sub")
async def check_sub(callback: CallbackQuery, bot: Bot):

    subscribed = await is_subscribed(bot, callback.from_user.id)

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
async def panel(message: Message):

    if message.from_user.id != ADMIN_ID:
        return

    await message.answer(
        "⚙️ لوحة تحكم الادمن",
        reply_markup=admin_panel_keyboard()
    )


@router.callback_query(F.data == "show_channels")
async def show_channels(callback: CallbackQuery):

    if callback.from_user.id != ADMIN_ID:
        return

    channels = load_channels()

    if not channels:
        text = "❌ لا توجد قنوات."
    else:
        text = "📋 القنوات الحالية:\n\n"

        for ch in channels:
            text += f"• {ch}\n"

    await callback.message.answer(text)


@router.callback_query(F.data == "add_channel")
async def add_channel_btn(callback: CallbackQuery):

    if callback.from_user.id != ADMIN_ID:
        return

    await callback.message.answer(
        "📥 ارسل الآن يوزر القناة.\n\n"
        "مثال:\n@mychannel"
    )


@router.callback_query(F.data == "remove_channel")
async def remove_channel_btn(callback: CallbackQuery):

    if callback.from_user.id != ADMIN_ID:
        return

    await callback.message.answer(
        "📤 ارسل يوزر القناة المراد حذفها.\n\n"
        "مثال:\n@mychannel"
    )


@router.message(F.text.startswith("@"))
async def channels_handler(message: Message):

    if message.from_user.id != ADMIN_ID:
        return

    channel = message.text.strip()

    channels = load_channels()

    if channel in channels:

        channels.remove(channel)
        save_channels(channels)

        await message.answer(
            f"➖ تم حذف القناة:\n{channel}"
        )

    else:

        channels.append(channel)
        save_channels(channels)

        await message.answer(
            f"➕ تمت إضافة القناة:\n{channel}"
        )


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

    subscribed = await is_subscribed(bot, message.from_user.id)

    if not subscribed:

        try:

            await message.delete()

            await message.answer(
                f"🚫 {message.from_user.full_name}\n"
                "يجب الاشتراك بالقنوات أولاً.",
                reply_markup=subscription_keyboard()
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
