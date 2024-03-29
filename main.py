import os
import asyncio
from config import TOKEN
from app.user import router_users
from aiogram import Bot, Dispatcher
from app.super_user import router_super_users
from app.database.models import create_database
import app.database.requests as db


# Starts the bot and creates a database

async def main():
    await create_database()

    await db.insert_super_user("89179449416", False, "000000")  # insert super user

    bot = Bot(TOKEN)
    dp = Dispatcher()
    dp.include_routers(router_users, router_super_users)
    await dp.start_polling(bot)


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        os.remove("UsersInformation.sqlite3")
        print("Exit")
