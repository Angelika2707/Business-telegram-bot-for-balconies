from app.database.models import UnregisteredUsers, RegisteredUsers, RegisteredSuperUsers, engine, async_session
from sqlalchemy import insert, select, delete
import xlsxwriter


# functions for working with database

async def insert_super_user(phone: str, status: bool) -> None:
    statement = insert(RegisteredSuperUsers).values(number=phone, registred=status)
    async with engine.connect() as connection:
        await connection.execute(statement)
        await connection.commit()


async def insert_unregistered_user(phone: str) -> None:
    statement = insert(UnregisteredUsers).values(number=phone)
    async with engine.connect() as connection:
        await connection.execute(statement)
        await connection.commit()


async def insert_user(phone: str, name: str, surname: str, patronymic: str, question: str) -> None:
    statement = insert(RegisteredUsers).values(number=phone, name=name, surname=surname, patronymic=patronymic,
                                               question=question)
    async with engine.connect() as connection:
        await connection.execute(statement)
        await connection.commit()


async def check_unregistered_user(phone: str) -> bool:
    statement = select(UnregisteredUsers).where(UnregisteredUsers.number == phone)
    async with engine.connect() as connection:
        result = await connection.execute(statement)
        for line in result.all():
            if line[1] == phone:
                return True
        return False


async def check_registered_user(phone: str) -> bool:
    statement = select(RegisteredUsers).where(RegisteredUsers.number == phone)
    async with engine.connect() as connection:
        result = await connection.execute(statement)
        for line in result.all():
            if line[1] == phone:
                return True
        return False


async def check_super_user(phone: str) -> bool:
    statement = select(RegisteredSuperUsers).where(RegisteredSuperUsers.number == phone)
    async with engine.connect() as connection:
        result = await connection.execute(statement)
        for line in result.all():
            if line[1] == phone:
                return True
        return False


async def delete_unregistered_user(phone: str) -> None:
    statement = delete(UnregisteredUsers).where(UnregisteredUsers.number == phone)
    async with engine.connect() as connection:
        await connection.execute(statement)
        await connection.commit()


async def delete_user(phone: str) -> None:
    statement = delete(RegisteredUsers).where(RegisteredUsers.number == phone)
    async with engine.connect() as connection:
        await connection.execute(statement)
        await connection.commit()


async def delete_super_user(phone: str) -> None:
    statement = delete(RegisteredSuperUsers).where(RegisteredSuperUsers.number == phone)
    async with engine.connect() as connection:
        await connection.execute(statement)
        await connection.commit()


async def create_exel_file() -> None:
    workbook = xlsxwriter.Workbook('app/documents/Партнёры.xlsx')
    worksheet = workbook.add_worksheet("Информация")

    headers = ['Номер телефона', "Имя", "Фамилия", "Отчество", "Вопрос"]
    column = 0
    for header in headers:
        worksheet.write(0, column, header)
        column += 1

    statement = select(RegisteredUsers)
    async with engine.connect() as connection:
        result = await connection.execute(statement)
        r = 1
        for row in result.all():
            l = 0
            row = row[1:]
            for col in row:
                try:
                    worksheet.write(r, l, col)
                except IndexError:
                    pass
                l += 1
            r += 1
    try:
        workbook.close()
    except xlsxwriter.exceptions.FileCreateError as e:
        pass
