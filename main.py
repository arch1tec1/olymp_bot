"""Запуск бота."""
import asyncio
from config import dp, bot
from middlewares import MediaGroupMiddleware
from models import init_db
from handlers.main_handler import router


async def main():
    """Инициализация БД и точка входа."""

    await init_db()
    dp.include_router(router)
    dp.message.middleware(MediaGroupMiddleware(latency=0.5))
    await dp.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(main())
