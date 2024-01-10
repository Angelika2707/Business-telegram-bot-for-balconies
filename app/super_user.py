from aiogram import Router
from aiogram.types import Message
from aiogram.filters import CommandStart

# File for handles commands from super users

router_super_users = Router()


@router_super_users.message(commands=['example'])
async def start_command(message: Message):
    await message.answer("super user")
