"""Участник пишет организатору."""
import sys
import os
from aiogram import types, Router
from aiogram.fsm.context import FSMContext

sys.path.append(os.path.join(os.path.dirname(__file__), '..'))
from config import UserState, active_dialogs, bot
from keyboards import get_admin_dialog_kb


user_to_admin = Router()


@user_to_admin.message(UserState.in_dialog_with_admin)
async def user_message_proxy(message: types.Message, state: FSMContext):
    """Проксирование сообщений участника админу."""

    user_id = message.from_user.id

    target_admin_id = active_dialogs.get(user_id)

    if not target_admin_id:
        await message.answer(
            "Связь прервана. Ожидайте сообщения от организатора."
            )
        await state.clear()
        return

    prefix = f"<b>Участник (@{message.from_user.username}):</b> "

    try:
        if message.text:
            await bot.send_message(
                target_admin_id,
                f"{prefix}{message.text}",
                parse_mode="HTML",
                reply_markup=get_admin_dialog_kb(),
            )
        elif message.photo:
            if message.caption:
                caption = f"{prefix}{message.caption}"
            else:
                prefix
            await bot.send_photo(
                target_admin_id,
                message.photo[-1].file_id,
                caption=caption,
                parse_mode="HTML",
                reply_markup=get_admin_dialog_kb(),
            )
        elif message.document:
            if message.caption:
                caption = f"{prefix}{message.caption}"
            else:
                prefix
            await bot.send_document(
                target_admin_id,
                message.document.file_id,
                caption=caption,
                parse_mode="HTML",
                reply_markup=get_admin_dialog_kb(),
            )
        else:
            await message.answer("Тип сообщения не поддерживается.")
    except Exception as e:
        print(f"DEBUG: Ошибка пересылки админу: {e}")
