from aiogram import Router, F
from aiogram.fsm.state import StatesGroup, State
from aiogram.types import Message, CallbackQuery
import app.database.requests
from aiogram.filters import CommandStart, StateFilter
from aiogram.fsm.context import FSMContext
from aiogram.types import InlineKeyboardButton
from aiogram.utils.keyboard import InlineKeyboardBuilder
from app.super_user import SuperUserStates
from aiogram.types import FSInputFile
import qrcode
import img2pdf
from PyPDF2 import PageObject, PdfReader, PdfWriter
import os

# File for handles commands from users

router_users = Router()

link_to_be_send = "https://innopolis.university/"


class BotStates(StatesGroup):
    register_state = State()
    waiting_for_phone_number = State()
    waiting_for_user_data = State()
    transfer_user_data = State()
    waiting_for_answer = State()
    finish_registration = State()


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
    data = await state.get_data()
    phone_number = data.get("phone_number")
    if await app.database.requests.check_super_user(phone_number):
        continue_button = InlineKeyboardButton(text="Продолжить", callback_data="go_to_super")
        builder = InlineKeyboardBuilder()
        builder.add(continue_button)
        await callback.message.answer("У Вас есть права суперпользователя. Вы готовы продолжить регистрацию?",
                                      reply_markup=builder.as_markup())
    else:
        continue_button = InlineKeyboardButton(text="Продолжить!", callback_data="continue_reg")
        builder = InlineKeyboardBuilder()
        builder.add(continue_button)
        await callback.message.answer("Номер верный! Продолжите регистрацию", reply_markup=builder.as_markup())


@router_users.callback_query(F.data == "continue_reg")
async def continue_registration(callback: CallbackQuery, state: FSMContext):
    data = await state.get_data()
    phone_number = data.get("phone_number")

    if await app.database.requests.check_unregistered_user(phone_number):
        await app.database.requests.delete_unregistered_user(phone_number)
        await callback.message.answer("Введите Ваше ФИО")
        await state.set_state(BotStates.waiting_for_user_data)
    else:
        await callback.message.answer("Вас нет в базе данных, попросите одного из суперпользователей Вас добавить и"
                                      "затем введите /start")
        await state.clear()


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


@router_users.message(BotStates.waiting_for_answer, F.text)
async def answer_given(message: Message, state: FSMContext):
    await state.update_data(given_answer=message.text)
    yes_button = InlineKeyboardButton(text="Да", callback_data="correct_answer")
    no_button = InlineKeyboardButton(text="Нет", callback_data="incorrect_answer")
    builder = InlineKeyboardBuilder()
    builder.add(yes_button)
    builder.add(no_button)
    await message.answer("Проверьте введенный вами ответ. Всё ли верно?",
                         reply_markup=builder.as_markup())

@router_users.callback_query(F.data == "correct_answer")
async def correct_user_answer(callback: CallbackQuery, state: FSMContext):
    user_data = await state.get_data()
    await callback.message.answer(f"Ваш окончательный ответ: {user_data['given_answer']}.")
    await state.set_state(BotStates.finish_registration)

@router_users.callback_query(F.data == "incorrect_answer")
async def incorrect_user_data(callback: CallbackQuery, state: FSMContext):
    await callback.message.answer("Пожалуйста, введите ответ на вопрос ещё раз")
    await state.set_state(BotStates.waiting_for_answer)


@router_users.message(BotStates.finish_registration)
async def process_answer(message: Message, state: FSMContext):
    user_data = await state.get_data()
    answer = user_data.get("given_answer")
    phone_number = user_data.get("phone_number")
    fio = user_data.get("user_data")
    surname, name, patronymic = fio.split(" ")
    await app.database.requests.insert_user(phone_number, name, surname, patronymic, answer)
    await message.answer("Спасибо за ответ!")
    await message.answer("Отлично! Вы успешно зарегистрированы!")
    #generating qr-code
    name = f"{message.from_user.id}" + ".png"
    name_of_QR = name.encode('utf-8')
    name = f"{message.from_user.id}" + ".pdf"
    name_of_PDF = name.encode('utf-8')
    qr = qrcode.QRCode()
    qr.add_data(link_to_be_send + " [" + user_data['given_answer'] + "]")
    img = qr.make_image()
    img.save(name_of_QR)
    qr.clear()
    with open(name_of_PDF, 'wb') as f:
        f.write(img2pdf.convert(name_of_QR))

    code_pdf = FSInputFile(name, filename="QR-code.pdf")
    await message.answer_document(code_pdf, caption="В этом пдф содержится QR-код созданный специально для вашей компании")

    main_pdf = PdfReader(open('Catalog.pdf', 'rb'))  #заметки для изменений пдф файла презентации. Загрузите
    #новую презентацию под именем Catalog.pdf в общую папку бота (она будет находиться в одной папке с файлом main)
    additional_pdf = PdfReader(open(name_of_PDF, 'rb'))
    page_number = 3 #данное число - номер страницы в презентации на которую мы хотим вставить qr-код, обязательно

    additional_page = additional_pdf.pages[0]
    additional_page.trimbox.lower_left = (0, 0)
    additional_page.trimbox.upper_right = (10000, 10000)

    main_page = main_pdf.pages[page_number - 1]
    additional_page.add_transformation([1, 0, 0, 1, 1100, 0]) #последние два числа это координаты начала фотографии
    #притом второе с конца - х-координата, а последнее - у-координата. Вероятно их придется изменить в новом типе презентации
    main_page.merge_page(additional_page)
    output_pdf = PdfWriter()

    for i in range(len(main_pdf.pages)):
        if i != page_number - 1:
            output_pdf.add_page(main_pdf.pages[i])
        else:
            output_pdf.add_page(main_page)

    with open('Presentation.pdf', 'wb') as output_file:
        output_pdf.write(output_file)
    presentation = FSInputFile(name, filename="Presentation.pdf")
    await message.answer_document(presentation, caption="Данный файл является презентацией, которую вы можете использовать в работе с клиентами. Спасибо за выбор нашей компании!")
    await state.clear()
    os.remove(name_of_QR)
    os.remove(name_of_PDF)
    os.remove('Presentation.pdf')
