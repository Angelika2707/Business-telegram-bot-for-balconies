from aiogram import Router, F
from aiogram.fsm.state import StatesGroup, State
from aiogram.types import Message, CallbackQuery
import app.database.requests as db
from aiogram.filters import CommandStart, StateFilter
from aiogram.fsm.context import FSMContext
from aiogram.types import InlineKeyboardButton
from aiogram.utils.keyboard import InlineKeyboardBuilder

# File for handles commands from users

router_users = Router()


class BotStates(StatesGroup):
    register_state = State()
    waiting_for_phone_number = State()
    waiting_for_user_data = State()
    transfer_user_data = State()
    waiting_for_answer = State()


@router_users.message(StateFilter(None), CommandStart())
async def start_command(message: Message, state: FSMContext):
    register_button = InlineKeyboardButton(text="Пройти регистрацию", callback_data="register")
    builder = InlineKeyboardBuilder()
    builder.add(register_button)
    await message.answer("Для работы с ботом вам нужно пройти регистрацию!", reply_markup=builder.as_markup())
    await state.set_state(BotStates.register_state)


@router_users.callback_query(F.data == "register")
async def register_command(callback: CallbackQuery, state: FSMContext):
    await callback.message.answer("Введите свой номер телефона")
    await state.set_state(BotStates.waiting_for_phone_number)


@router_users.message(BotStates.waiting_for_phone_number)
async def process_phone_number(message: Message, state: FSMContext):
    phone_number = message.text
    await state.update_data(phone_number=phone_number)

    yes_button = InlineKeyboardButton(text="Да", callback_data="correct_number")
    no_button = InlineKeyboardButton(text="Нет", callback_data="incorrect_number")
    builder = InlineKeyboardBuilder()
    builder.add(yes_button)
    builder.add(no_button)
    await message.answer("Проверьте введенный вами номер. Верно ли вы указали данные?",
                         reply_markup=builder.as_markup())


@router_users.callback_query(F.data == "incorrect_number")
async def incorrect_phone_number(callback: CallbackQuery, state: FSMContext):
    await callback.message.answer("Номер неверный! Попробуйте ввести ещё раз")
    await state.set_state(BotStates.waiting_for_phone_number)


@router_users.callback_query(F.data == "correct_number")
async def correct_phone_number(callback: CallbackQuery, state: FSMContext):
    continue_button = InlineKeyboardButton(text="Продолжить!", callback_data="continue_reg")
    builder = InlineKeyboardBuilder()
    builder.add(continue_button)
    await callback.message.answer("Номер верный! Продолжите регистрацию", reply_markup=builder.as_markup())


@router_users.callback_query(F.data == "continue_reg")
async def continue_registration(callback: CallbackQuery, state: FSMContext):
    data = await state.get_data()
    phone_number = data.get("phone_number")

    if db.check_unregistered_user(phone_number):
        await db.delete_unregistered_user(phone_number)
        await callback.message.answer("Введите Ваше ФИО")
        await state.set_state(BotStates.waiting_for_user_data)


@router_users.message(BotStates.waiting_for_user_data)
async def get_user_data(message: Message, state: FSMContext):
    user_data = message.text
    await state.update_data(user_data=user_data)
    yes_button = InlineKeyboardButton(text="Да", callback_data="correct_data")
    no_button = InlineKeyboardButton(text="Нет", callback_data="incorrect_data")
    builder = InlineKeyboardBuilder()
    builder.add(yes_button)
    builder.add(no_button)
    await message.answer("Проверьте введенные вами данные. Всё ли вы указали верно?",
                         reply_markup=builder.as_markup())


@router_users.callback_query(F.data == "incorrect_data")
async def incorrect_user_data(callback: CallbackQuery, state: FSMContext):
    await callback.message.answer("Данные введены с ошибками! Попробуйте ввести ещё раз")
    F.data = "continue_reg"


@router_users.callback_query(F.data == "correct_data")
async def correct_user_data(callback: CallbackQuery, state: FSMContext):
    continue_button = InlineKeyboardButton(text="Продолжить!", callback_data="go_to_poll")
    builder = InlineKeyboardBuilder()
    builder.add(continue_button)
    await callback.message.answer("Данные введены верно! Продолжите регистрацию", reply_markup=builder.as_markup())


@router_users.callback_query(F.data == "go_to_poll")
async def ask_question(callback: CallbackQuery, state: FSMContext):
    await callback.message.answer("К какой вы относитесь организации (застройщик, УК  и т.д.) или основной вид вашей  деятельности (дизайнер, плиточник и т.д.)?")
    await state.set_state(BotStates.waiting_for_answer)


@router_users.message(BotStates.waiting_for_answer)
async def process_answer(message: Message, state: FSMContext):
    answer = message.text
    user_data = await state.get_data()
    phone_number = user_data.get("phone_number")
    fio = user_data.get("user_data")
    surname, name, patronymic = fio.split(" ")
    await db.insert_user(phone_number, name, surname, patronymic, answer)
    await message.answer("Спасибо за ответ!")
    await message.answer("Отлично! Вы успешно зарегистрированы!")
    await state.clear()

