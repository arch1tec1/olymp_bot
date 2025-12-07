"""Система отправки сообщений о помощи."""
import sys
import os
from aiogram import F, types, Router
from aiogram.fsm.context import FSMContext
from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup

sys.path.append(os.path.join(os.path.dirname(__file__), '...'))
from config import Support, bot, active_alerts, try_delete, ADMIN_IDS
from keyboards import get_main_kb


user_help = Router()


@user_help.callback_query(F.data == "contact_support")
async def start_support(callback: types.CallbackQuery, state: FSMContext):
    """Ввод описания проблемы участника."""

    await state.set_state(Support.waiting_for_message)

    await callback.message.edit_text(
        "Опишите вашу проблему одним сообщением, "
        "и организатор ответит вам здесь.",
        reply_markup=None,
    )

    await state.update_data(last_bot_msg_id=callback.message.message_id)
    await callback.answer()


@user_help.message(Support.waiting_for_message)
async def forward_to_admin(message: types.Message, state: FSMContext):
    """Рассылка сообщений о проблемах организаторам."""
    data = await state.get_data()

    user_text = message.text
    admin_msg = (
        f"🆘 <b>ВОПРОС В ПОДДЕРЖКУ</b>\n"
        f"От: ID {message.from_user.id} (@{message.from_user.username})\n\n"
        f"Текст:\n{user_text}"
    )

    kb = InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(
                    text="💬 Ответить пользователю",
                    callback_data=f"reply_{message.from_user.id}",
                )
            ]
        ]
    )

    sent_messages_info = []

    for admin_id in ADMIN_IDS:
        try:
            sent_msg = await bot.send_message(
                chat_id=admin_id,
                text=admin_msg, parse_mode="HTML",
                reply_markup=kb
            )
            sent_messages_info.append((admin_id, sent_msg.message_id))
        except Exception:
            pass

    if sent_messages_info:
        if message.from_user.id not in active_alerts:
            active_alerts[message.from_user.id] = []

        active_alerts[message.from_user.id].append(sent_messages_info)

    if "last_bot_msg_id" in data:
        await try_delete(bot, message.chat.id, data["last_bot_msg_id"])

    await try_delete(bot, message.chat.id, message.message_id)

    await state.clear()
    await message.answer(
        "Сообщение отправлено. Ожидайте ответа в этом чате.",
        reply_markup=get_main_kb(message.from_user.id),
    )
