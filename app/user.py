from aiogram import Router, F
from aiogram.fsm.state import StatesGroup, State
from aiogram.types import Message, CallbackQuery
import app.database.requests as db
from aiogram.filters import CommandStart, StateFilter
from aiogram.fsm.context import FSMContext
from aiogram.types import InlineKeyboardButton
from aiogram.utils.keyboard import InlineKeyboardBuilder
from aiogram.types import FSInputFile
import qrcode
import img2pdf
from PyPDF2 import PdfReader, PdfWriter
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
    await message.answer("Для работы с ботом Вам нужно пройти регистрацию!", reply_markup=builder.as_markup())
    await state.set_state(BotStates.register_state)


@router_users.callback_query(F.data == "register")
async def register_command(callback: CallbackQuery, state: FSMContext):
    await callback.message.answer("Введите свой номер телефона. Формат ввода: 8XXXXXXXXXX")
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
    await message.answer("Проверьте введенный Вами номер. Верно ли Вы указали данные?",
                         reply_markup=builder.as_markup())


@router_users.callback_query(F.data == "incorrect_number")
async def incorrect_phone_number(callback: CallbackQuery, state: FSMContext):
    await callback.message.answer("Номер неверный! Попробуйте ввести ещё раз")
    await state.set_state(BotStates.waiting_for_phone_number)


@router_users.callback_query(F.data == "correct_number")
async def correct_phone_number(callback: CallbackQuery, state: FSMContext):
    data = await state.get_data()
    phone_number = data.get("phone_number")
    if await db.check_super_user(phone_number):
        if await db.check_super_user_status(phone_number):
            await callback.message.answer("Введённый Вами номер уже принадлежит одному из зарегистрированных "
                                          "суперпользователей. Пожалуйста, нажмите /start и пройдите регистрацию с "
                                          "указанием Вашего номера телефона")
            await state.clear()
            return
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

    if await db.check_registered_user(phone_number):
        await callback.message.answer("Введённый Вами номер уже принадлежит одному из зарегистрированных пользователей. "
                                      "Пожалуйста, нажмите /start и пройдите регистрацию с указанием Вашего номера "
                                      "телефона")
        await state.clear()
        return

    if await db.check_unregistered_user(phone_number):
        await db.delete_unregistered_user(phone_number)
        await callback.message.answer("Введите Ваше ФИО (пример: Иванов Иван Иванович)")
        await state.set_state(BotStates.waiting_for_user_data)
    else:
        await callback.message.answer("Вас нет в базе данных, попросите одного из суперпользователей Вас добавить и "
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
    await message.answer("Проверьте введенные Вами данные. Всё ли Вы указали верно?",
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
    await callback.message.answer("К какой Вы относитесь организации (застройщик, УК  и т.д.) или основной вид Вашей "
                                  "деятельности (дизайнер, плиточник и т.д.)?")
    await state.set_state(BotStates.waiting_for_answer)


@router_users.message(BotStates.waiting_for_answer)
async def answer_given(message: Message, state: FSMContext):
    await state.update_data(given_answer=message.text)
    yes_button = InlineKeyboardButton(text="Да", callback_data="correct_answer")
    no_button = InlineKeyboardButton(text="Нет", callback_data="incorrect_answer")
    builder = InlineKeyboardBuilder()
    builder.add(yes_button)
    builder.add(no_button)
    await message.answer("Проверьте введенный Вами ответ. Всё ли верно?",
                         reply_markup=builder.as_markup())


@router_users.callback_query(F.data == "correct_answer")
async def correct_user_answer(callback: CallbackQuery, state: FSMContext):
    continue_button = InlineKeyboardButton(text="Продолжить", callback_data="go_to_qr_code")
    builder = InlineKeyboardBuilder()
    builder.add(continue_button)
    await callback.message.answer("Ваш ответ на вопрос принят", reply_markup=builder.as_markup())
    await state.set_state(BotStates.finish_registration)


@router_users.callback_query(F.data == "incorrect_answer")
async def incorrect_user_data(callback: CallbackQuery, state: FSMContext):
    await callback.message.answer("Пожалуйста, введите ответ на вопрос ещё раз")
    await state.set_state(BotStates.waiting_for_answer)


@router_users.callback_query(F.data == "go_to_qr_code")
async def process_answer(callback: CallbackQuery, state: FSMContext):
    user_data = await state.get_data()
    answer = user_data.get("given_answer")
    phone_number = user_data.get("phone_number")
    fio = user_data.get("user_data")
    surname, name, patronymic = fio.split(" ")
    await db.insert_user(phone_number, name, surname, patronymic, answer)
    await callback.message.answer("Спасибо за ответ!")
    await callback.message.answer("Отлично! Вы успешно зарегистрированы!")
    #generating qr-code
    name = f"{callback.message.from_user.id}" + ".png"
    name_of_QR = name.encode('utf-8')
    name = f"{callback.message.from_user.id}" + ".pdf"
    name_of_PDF = name.encode('utf-8')
    qr = qrcode.QRCode()
    qr.add_data(link_to_be_send + " [" + user_data['given_answer'] + "]")
    img = qr.make_image()
    img.save(name_of_QR)
    qr.clear()
    with open(name_of_PDF, 'wb') as f:
        f.write(img2pdf.convert(name_of_QR))

    code_pdf = FSInputFile(name, filename="QR-code.pdf")
    await callback.message.answer_document(code_pdf, caption="В этом pdf-файле содержится QR-код, созданный специально "
                                                             "для Вашей компании")

    main_file = open('Catalog.pdf', 'rb')
    main_pdf = PdfReader(main_file)  #заметки для изменений пдф файла презентации. Загрузите
    #новую презентацию под именем Catalog.pdf в общую папку бота (она будет находиться в одной папке с файлом main)
    additional_file = open(name_of_PDF, 'rb')
    additional_pdf = PdfReader(additional_file)
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

    presentation = FSInputFile("Presentation.pdf", filename="Presentation.pdf")
    await callback.message.answer_document(presentation, caption="Данный файл является презентацией, которую Вы можете "
                                                        "использовать в работе с клиентами. Спасибо за выбор нашей компании!")
    await state.clear()
    main_file.close()
    additional_file.close()
    os.remove(name_of_QR)
    os.remove(name_of_PDF)
    os.remove('Presentation.pdf')
    await callback.message.answer("Сейчас Вы являетесь *пользователем*. Если кто-то из суперпользователей сделает Вас "
                         "суперпользователем, пожалуйста, начните процесс регистрации заново, воспользовавшись "
                         "командой /start", parse_mode="Markdown")
