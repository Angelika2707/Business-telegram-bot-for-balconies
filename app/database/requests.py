from app.database.models import UnregisteredUsers, RegisteredUsers, RegisteredSuperUsers, engine, async_session
from sqlalchemy import insert, select, delete

# functions for working with database

async def insert_super_user(phone: str) -> None:
    statement = insert(RegisteredSuperUsers).values(number=phone, registred="true")
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


async def delete_unregistered_user(phone: str) -> None:
    statement = delete(UnregisteredUsers).where(UnregisteredUsers.number == phone)
    async with engine.connect() as connection:
        await connection.execute(statement)
        await connection.commit()


async def delete_user(phone: str, name: str, surname: str, patronymic: str, question: str) -> None:
    statement = delete(RegisteredUsers).where(RegisteredUsers.number == phone, RegisteredUsers.surname == surname,
                                              RegisteredUsers.patronymic == patronymic, RegisteredUsers.question == question)
    async with engine.connect() as connection:
        await connection.execute(statement)
        await connection.commit()


async def delete_super_user(phone: str) -> None:
    statement = delete(RegisteredSuperUsers).where(RegisteredSuperUsers.number == phone)
    async with engine.connect() as connection:
        await connection.execute(statement)
        await connection.commit()
