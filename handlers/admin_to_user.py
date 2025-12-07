"""Организатор пишет участнику."""
import sys
import os
from aiogram import types, Router
from aiogram.fsm.context import FSMContext
from aiogram.fsm.storage.base import StorageKey

sys.path.append(os.path.join(os.path.dirname(__file__), '..'))
from config import AdminPanel, active_dialogs, bot, dp
from keyboards import get_admin_panel_kb


admin_to_user = Router()


@admin_to_user.message(AdminPanel.in_dialog)
async def admin_message_proxy(message: types.Message, state: FSMContext):
    """Проксирование сообщений админа участнику, чистка после конца диалога."""

    data = await state.get_data()
    user_id = data.get("dialog_user_id")

    if message.text == "❌ Закончить диалог":
        if user_id in active_dialogs:
            del active_dialogs[user_id]

        await state.clear()
        await message.answer(
            "Диалог завершен.",
            reply_markup=get_admin_panel_kb()
        )

        if user_id:
            try:
                user_key = StorageKey(
                    bot_id=bot.id,
                    chat_id=user_id, user_id=user_id
                    )
                user_ctx = FSMContext(storage=dp.storage, key=user_key)
                await user_ctx.clear()

                await bot.send_message(
                    user_id,
                    "🔕 <b>Диалог с организатором завершен.</b>",
                    parse_mode="HTML",
                )
            except Exception:
                pass
        return

    if user_id:
        try:
            prefix = "<b>Организатор:</b> "
            if message.text:
                await bot.send_message(
                    user_id, f"{prefix}{message.text}", parse_mode="HTML"
                )
            elif message.photo:
                if message.caption:
                    caption = f"{prefix}{message.caption}"
                else:
                    prefix

                await bot.send_photo(
                    user_id,
                    message.photo[-1].file_id,
                    caption=caption,
                    parse_mode="HTML",
                )
            elif message.document:
                if message.caption:
                    caption = f"{prefix}{message.caption}"
                else:
                    prefix
                await bot.send_document(
                    user_id,
                    message.document.file_id,
                    caption=caption,
                    parse_mode="HTML",
                )
            else:
                await message.answer("Тип сообщения не поддерживается.")
        except Exception:
            await message.answer(
                "Ошибка доставки (возможно пользователь заблокировал бота)."
            )
