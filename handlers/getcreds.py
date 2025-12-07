from aiogram import F, types
from sqlalchemy import select

from ..config import router
from ..models import User, async_session


@router.message(F.text == "Получить логин и пароль")
async def get_credentials(message: types.Message):
    async with async_session() as session:
        result = await session.execute(
            select(User).where(User.telegram_id == message.from_user.id)
        )
        user = result.scalar()

        if user:
            await message.answer(
                f"Ваши данные:\n"
                f"Login: `{user.login_id}`\n"
                f"Password: `{user.plain_password}`",
                parse_mode="Markdown",
            )
        else:
            await message.answer("Вы еще не зарегистрированы.")
