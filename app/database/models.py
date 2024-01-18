from sqlalchemy import String
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column
from sqlalchemy.ext.asyncio import AsyncAttrs, async_sessionmaker, create_async_engine
from config import SQL_ALCHEMY_DATABASE_URI

# Creating tables needed for registration in the bot

# Create an asynchronous engine using the specified database URI(config.py)
engine = create_async_engine(SQL_ALCHEMY_DATABASE_URI, echo=True)

# Create an asynchronous session factory
async_session = async_sessionmaker(engine)


# Base class for declarative models with asynchronous support
class Base(AsyncAttrs, DeclarativeBase):
    pass


# Model for Unregistered Users
class UnregisteredUsers(Base):
    __tablename__ = "Unregistered users"
    id: Mapped[int] = mapped_column(primary_key=True)
    number: Mapped[str] = mapped_column(String(20), unique=True)

    def __repr__(self):
        return f"Number phone(id={self.id!r}, number={self.name!r})"

    def __str__(self):
        return self


# Model for Registered Users
class RegisteredUsers(Base):
    __tablename__ = "Registered users"
    id: Mapped[int] = mapped_column(primary_key=True)
    number: Mapped[str] = mapped_column(String(20), unique=True)
    name: Mapped[str] = mapped_column(String(20))
    surname: Mapped[str] = mapped_column(String(20))
    patronymic: Mapped[str] = mapped_column(String(20))
    question: Mapped[str] = mapped_column(String(20))

    def __str__(self):
        return (f"User(id={self.id!r}, number={self.number!r}), name={self.name!r}, "
                f"surname={self.surname!r}, patronymic={self.patronymic!r}, question={self.question!r}")

    def __repr__(self):
        return str(self)


# Model for Registered Super Users
class RegisteredSuperUsers(Base):
    __tablename__ = "Registered super users"
    id: Mapped[int] = mapped_column(primary_key=True)
    number: Mapped[str] = mapped_column(String(20), unique=True)
    registred: Mapped[bool] = mapped_column(String(20))
    security_code: Mapped[str] = mapped_column(String(6))

    def __str__(self):
        return f"User(id={self.id!r}, number={self.number!r})"

    def __repr__(self):
        return str(self)


async def create_database():
    async with engine.begin() as connection:
        await connection.run_sync(Base.metadata.create_all)
