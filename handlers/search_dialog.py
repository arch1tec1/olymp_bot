"""Поиск организатором диалога с участником."""
import sys
import os
from aiogram import F, types, Router
from aiogram.fsm.context import FSMContext
from aiogram.fsm.storage.base import StorageKey
from sqlalchemy import select

sys.path.append(os.path.join(os.path.dirname(__file__), '..'))
from config import (
    AdminPanel,
    UserState,
    bot,
    dp,
    active_dialogs,
    ADMIN_IDS,
)
from keyboards import get_admin_panel_kb, get_admin_dialog_kb
from models import User, async_session


search = Router()


@search.message(AdminPanel.waiting_for_user_search)
async def process_username_search(message: types.Message, state: FSMContext):
    username_input = message.text.strip().replace("@", "")

    async with async_session() as session:
        # Ищем пользователя по username
        result = await session.execute(
            select(User).where(User.username == username_input)
        )
        user = result.scalar()

    if not user:
        await message.answer(
            "❌ Пользователь с таким username не найден в базе бота.",
            reply_markup=get_admin_panel_kb(),
        )
        await state.clear()
        return

    active_dialogs[user.telegram_id] = message.from_user.id

    await state.set_state(AdminPanel.in_dialog)
    await state.update_data(dialog_user_id=user.telegram_id)

    try:
        user_key = StorageKey(
            bot_id=bot.id, chat_id=user.telegram_id, user_id=user.telegram_id
        )
        user_state = FSMContext(storage=dp.storage, key=user_key)

        await user_state.set_state(UserState.in_dialog_with_admin)

        await bot.send_message(
            user.telegram_id,
            "🔔 <b>С вами связывается организатор.</b>\n"
            "Диалог с организатором:",
            parse_mode="HTML",
        )
    except Exception as e:
        print(f"DEBUG: Не удалось переключить стейт юзера: {e}")

    await message.answer(
        f"Диалог с участником @{username_input} начат.\n"
        "Все ваши сообщения будут пересылаться ему.",
        reply_markup=get_admin_dialog_kb(),
    )


@search.message(F.text == "👤 Общение с участником")
async def start_dialog_search(message: types.Message, state: FSMContext):
    if message.from_user.id not in ADMIN_IDS:
        return
    await state.set_state(AdminPanel.waiting_for_user_search)
    await message.answer(
        "Введите @username пользователя для связи:",
        reply_markup=types.ReplyKeyboardRemove(),
    )
