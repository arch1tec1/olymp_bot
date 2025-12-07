"""Рассылка сообщений участникам."""
import sys
import os
import asyncio
from aiogram import F, types, Router
from aiogram.fsm.context import FSMContext
from sqlalchemy import select

sys.path.append(os.path.join(os.path.dirname(__file__), '..'))
from config import AdminPanel, bot, ADMIN_IDS
from keyboards import get_admin_panel_kb
from models import User, async_session


broad = Router()


@broad.message(F.text == "📢 Разослать всем")
async def start_broadcast(message: types.Message, state: FSMContext):
    """Реакция на нажатие кнопки и ввод сообщения."""

    if message.from_user.id not in ADMIN_IDS:
        return
    await state.set_state(AdminPanel.waiting_for_broadcast_content)
    await message.answer(
        "Отправьте сообщение (текст, фото, файл), которое "
        "нужно разослать всем участникам.",
        reply_markup=types.ReplyKeyboardRemove(),
    )


@broad.message(AdminPanel.waiting_for_broadcast_content)
async def process_broadcast(message: types.Message, state: FSMContext):
    """Начало рассылки сообщений участникам."""

    async with async_session() as session:
        users_result = await session.execute(select(User.telegram_id))
        users_ids = users_result.scalars().all()

    count = 0
    await message.answer("⏳ Начинаю рассылку...")

    for user_id in users_ids:
        try:
            await bot.copy_message(
                chat_id=user_id,
                from_chat_id=message.chat.id,
                message_id=message.message_id,
            )
            count += 1
            await asyncio.sleep(0.05)
        except Exception:
            pass

    await message.answer(
        f"✅ Рассылка завершена. Отправлено пользователям: {count}",
        reply_markup=get_admin_panel_kb(),
    )
    await state.clear()
