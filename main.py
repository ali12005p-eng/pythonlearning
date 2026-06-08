import asyncio

from bot import dp, bot
from database import init_db


async def main():

    init_db()

    print("Bot is running...")

    await dp.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(main())
