import secrets
from aiogram import Router, F
from aiogram.types import Message, CallbackQuery, BufferedInputFile
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import StatesGroup, State
import app.database.requests as db

codes = ["000000"]


# File for handles commands from super users


class SuperUserStates(StatesGroup):
    main_menu = State()
    add_user = State()
    add_super_user = State()
    delete_user = State()
    delete_super_user = State()
    give_super_user_permission = State()
    check_code = State()


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
    else:
        await callback.message.answer("Пожалуйста, введите шестизначный код подтверждения, полученный от одного из "
                                      "суперпользователей")
        await state.set_state(SuperUserStates.check_code)
        await state.update_data(phone_number=phone_number)


def menu_text() -> str:
    return ("Выберите действие:\n"
            "/add_user - Добавить пользователя\n"
            "/add_super_user - Добавить суперпользователя\n"
            "/delete_user - Удалить пользователя\n"
            "/delete_super_user - Удалить суперпользователя\n"
            "/get_table - Получить таблицу с данными и ответами партнёров в формате xlsx\n"
            "/generate_code - Сгенерировать код подтверждения для нового суперпользователя")


@router_super_users.message(F.text == '/menu')
async def go_to_menu(message: Message, state: FSMContext):
    await state.set_state(SuperUserStates.main_menu)
    await message.answer(menu_text())


@router_super_users.message(F.text == '/generate_code')
async def generate_code(message: Message, state: FSMContext):
    code = secrets.randbelow(10 ** 6)
    codes.append(str(code))
    await state.set_state(SuperUserStates.main_menu)
    await message.answer(f"Код подтверждения, созданный вами: {code}. Покажите его суперпользователю, которого хотите "
                         f"добавить")
    await message.answer(menu_text())


@router_super_users.message(SuperUserStates.check_code)
async def check_code(message: Message, state: FSMContext):
    user_code = message.text
    if user_code in codes:
        data = await state.get_data()
        phone_number = data.get("phone_number")
        await db.delete_super_user(phone_number)
        await db.insert_super_user(phone_number, True)
        codes.remove(user_code)
        await message.answer("Код верный. Теперь Вам доступны возможности суперпользователя")
        await state.set_state(SuperUserStates.main_menu)
        await message.answer(menu_text())
    else:
        await message.answer("Неверный код. Пожалуйста, попробуйте ввести его ещё раз")
        await state.set_state(SuperUserStates.check_code)


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
    file_path = 'app/documents/Партнёры.xlsx'
    with open(file_path, 'rb') as doc:
        bytes_read = doc.read()
        table = BufferedInputFile(bytes_read, filename='Партнёры.xlsx')
        await message.answer_document(table)
    await state.set_state(SuperUserStates.main_menu)
    await message.answer(menu_text())
