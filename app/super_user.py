from aiogram import Router, F
from aiogram.types import Message, CallbackQuery, InputFile
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import StatesGroup, State
import app.database.requests as db


# File for handles commands from super users


class SuperUserStates(StatesGroup):
    main_menu = State()
    add_user = State()
    add_super_user = State()
    delete_user = State()
    delete_super_user = State()
    give_super_user_permission = State()


router_super_users = Router()


@router_super_users.callback_query(F.data == "go_to_super")
async def give_permission(callback: CallbackQuery, state: FSMContext):
    data = await state.get_data()
    phone_number = data.get("phone_number")
    if await db.check_registered_user(phone_number):
        await db.delete_user(phone_number)
    await db.delete_super_user(phone_number)
    await db.insert_super_user(phone_number, True)
    await callback.message.answer("Теперь Вам доступны возможности суперпользователя")
    await state.set_state(SuperUserStates.main_menu)
    await callback.message.answer(menu_text())


def menu_text() -> str:
    return ("Выберите действие:\n"
            "/add_user - Добавить пользователя\n"
            "/add_super_user - Добавить суперпользователя\n"
            "/delete_user - Удалить пользователя\n"
            "/delete_super_user - Удалить суперпользователя\n"
            "/get_table - Получить таблицу с данными и ответами партнёров в формате xlsx")


@router_super_users.message(F.text == '/menu')
async def go_to_menu(message: Message, state: FSMContext):
    await state.set_state(SuperUserStates.main_menu)
    await message.answer(menu_text())


@router_super_users.message(F.text == "/add_user")
async def process_data_add_user(message: Message, state: FSMContext):
    await message.answer("Введите номер телефона пользователя, которого хотите добавить, либо /menu, "
                                  "чтобы отменить действие")
    await state.set_state(SuperUserStates.add_user)


@router_super_users.message(SuperUserStates.add_user)
async def add_user(message: Message, state: FSMContext):
    if await db.check_registered_user(message.text) or await db.check_unregistered_user(message.text):
        await message.answer(f"Пользователь с номером телефона {message.text} уже существует")
    else:
        await db.insert_unregistered_user(message.text)
        await message.answer(f"Пользователь с номером телефона {message.text} успешно добавлен")
    await state.set_state(SuperUserStates.main_menu)
    await message.answer(menu_text())


@router_super_users.message(F.text == "/add_super_user")
async def process_data_add_super_user(message: Message, state: FSMContext):
    await message.answer("Введите номер телефона суперпользователя, которого хотите добавить, либо /menu, "
                                  "чтобы отменить действие")
    await state.set_state(SuperUserStates.add_super_user)


@router_super_users.message(SuperUserStates.add_super_user)
async def add_super_user(message: Message, state: FSMContext):
    if await db.check_super_user(message.text):
        await message.answer(f"Суперпользователь с номером телефона {message.text} уже существует")
    else:
        await db.insert_super_user(message.text, False)
        await message.answer(f"Суперпользователь с номером телефона {message.text} успешно добавлен")
    await state.set_state(SuperUserStates.main_menu)
    await message.answer(menu_text())


@router_super_users.message(F.text == "/delete_user")
async def process_data_delete_user(message: Message, state: FSMContext):
    await message.answer("Введите номер телефона пользователя, которого хотите удалить, либо /menu, "
                                  "чтобы отменить действие")
    await state.set_state(SuperUserStates.delete_user)


@router_super_users.message(SuperUserStates.delete_user)
async def delete_user(message: Message, state: FSMContext):
    if await db.check_registered_user(message.text):
        await db.delete_user(message.text)
        await message.answer(f"Пользователь с номером телефона {message.text} успешно удалён")
    elif await db.check_unregistered_user(message.text):
        await db.delete_unregistered_user(message.text)
        await message.answer(f"Пользователь с номером телефона {message.text} успешно удалён")
    else:
        await message.answer(f"Номера телефона {message.text} нет в базе данных пользователей")
    await state.set_state(SuperUserStates.main_menu)
    await message.answer(menu_text())


@router_super_users.message(F.text == "/delete_super_user")
async def process_data_delete__super_user(message: Message, state: FSMContext):
    await message.answer("Введите номер телефона суперпользователя, которого хотите удалить, либо /menu, "
                                  "чтобы отменить действие")
    await state.set_state(SuperUserStates.delete_super_user)


@router_super_users.message(SuperUserStates.delete_super_user)
async def delete_super_user(message: Message, state: FSMContext):
    if await db.check_super_user(message.text):
        await db.delete_super_user(message.text)
        await message.answer(f"Суперпользователь с номером телефона {message.text} успешно удалён")
    else:
        await message.answer(f"Номера телефона {message.text} нет в базе данных суперпользователей")
    await state.set_state(SuperUserStates.main_menu)
    await message.answer(menu_text())


@router_super_users.message(F.text == '/get_table')
async def get_table(message: Message, state: FSMContext):
    await db.create_exel_file()
    with open('app/documents/Партнёры.xlsx', 'rb') as doc:
        await message.answer(InputFile(doc))
    await state.set_state(SuperUserStates.main_menu)
    await message.answer(menu_text())
