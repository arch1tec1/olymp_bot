"""Взаимодействие участника с организаторами."""
import sys
import os
from aiogram import F, types, Router

sys.path.append(os.path.join(os.path.dirname(__file__), '..'))
from keyboards import get_organizer_kb


call = Router()


@call.message(F.text == "🔔 Связь с организаторами")
async def contact_menu(message: types.Message):
    """Выбор пичины для связи с организаторами."""

    await message.answer(
        "Выберите категорию:",
        reply_markup=get_organizer_kb()
        )
