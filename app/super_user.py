from aiogram import Router
from aiogram.types import Message
import app.database.requests as db
from aiogram.filters import Command

# File for handles commands from super users

router_super_users = Router()


@router_super_users.message(Command("example"))
async def start_command(message: Message):
    await message.answer("super user")
