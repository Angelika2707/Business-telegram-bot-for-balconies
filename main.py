import asyncio
from config import TOKEN
from app.user import router_users
from aiogram import Bot, Dispatcher
from app.super_user import router_super_users
from app.database.models import create_database


# Starts the bot and creates a database

async def main():
    await create_database()

    bot = Bot(TOKEN)
    dp = Dispatcher()
    dp.include_routers(router_users, router_super_users)
    await dp.start_polling(bot)


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("Exit")
