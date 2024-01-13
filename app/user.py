from aiogram import Router
from aiogram.types import Message
import app.database.requests as db
from aiogram.filters import CommandStart

# File for handles commands from users

router_users = Router()


@router_users.message(CommandStart())
async def start_command(message: Message):
    await message.answer("Hello World!")
