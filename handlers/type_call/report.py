"""Система подачи репортов."""
import sys
import os
from aiogram import F, types, Router
from aiogram.fsm.context import FSMContext
from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup
from aiogram.utils.media_group import MediaGroupBuilder
from typing import List

sys.path.append(os.path.join(os.path.dirname(__file__), '...'))
from config import Report, bot, active_alerts, try_delete, ADMIN_IDS
from keyboards import get_main_kb


user_rep = Router()


@user_rep.callback_query(F.data == "report_violation")
async def start_report(callback: types.CallbackQuery, state: FSMContext):
    """Начало составления репорта. Ввод username нарушителя."""

    await state.set_state(Report.offender_username)

    await callback.message.edit_text(
        "Введите имя пользователя нарушителя (начинается с @):",
        reply_markup=None,
    )
    await state.update_data(last_bot_msg_id=callback.message.message_id)
    await callback.answer()


@user_rep.message(Report.offender_username)
async def process_report_username(message: types.Message, state: FSMContext):
    """Ввод username и запрос описания нарушения."""

    data = await state.get_data()

    if "last_bot_msg_id" in data:
        await try_delete(bot, message.chat.id, data["last_bot_msg_id"])

    await try_delete(bot, message.chat.id, message.message_id)

    if not message.text.startswith("@"):
        msg = await message.answer
        ("❌ Имя должно начинаться с @. Попробуйте снова:")
        await state.update_data(last_bot_msg_id=msg.message_id)
        return

    await state.update_data(offender_username=message.text)
    await state.set_state(Report.description)

    msg = await message.answer("Опишите нарушение:")
    await state.update_data(last_bot_msg_id=msg.message_id)


@user_rep.message(Report.description)
async def process_report_desc(message: types.Message, state: FSMContext):
    """Запрос доказательств к репорту."""

    data = await state.get_data()

    if "last_bot_msg_id" in data:
        await try_delete(bot, message.chat.id, data["last_bot_msg_id"])
    await try_delete(bot, message.chat.id, message.message_id)

    await state.update_data(description=message.text)
    await state.set_state(Report.proof)

    msg = await message.answer(
        "Отправьте доказательства (фото, скриншот) или напишите 'нет', "
        "если доказательств нет."
    )
    await state.update_data(last_bot_msg_id=msg.message_id)


@user_rep.message(Report.proof, F.photo | F.text)
async def process_report_proof(
    message: types.Message, state: FSMContext,
    album: List[types.Message] = None
):
    """Рассылка репортов организаторам."""

    data = await state.get_data()

    report_text = (
        f"🚨 <b>НОВЫЙ РЕПОРТ</b>\n"
        f"От кого: ID {message.from_user.id} (@{message.from_user.username})\n"
        f"Нарушитель: {data['offender_username']}\n"
        f"Описание: {data['description']}"
    )

    kb = InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(
                    text="💬 Ответить автору жалобы",
                    callback_data=f"reply_{message.from_user.id}",
                )
            ]
        ]
    )

    sent_messages_info = []

    for admin_id in ADMIN_IDS:
        try:
            if album:
                media_group = MediaGroupBuilder(
                    caption="Приложенные доказательства:"
                    )
                for msg in album:
                    if msg.photo:
                        media_group.add_photo(media=msg.photo[-1].file_id)
                await bot.send_media_group(
                    chat_id=admin_id,
                    media=media_group.build()
                    )
                sent_msg = await bot.send_message(
                    chat_id=admin_id,
                    text=report_text,
                    parse_mode="HTML",
                    reply_markup=kb,
                )
                sent_messages_info.append((admin_id, sent_msg.message_id))

            elif message.photo:
                sent_msg = await bot.send_photo(
                    chat_id=admin_id,
                    photo=message.photo[-1].file_id,
                    caption=report_text,
                    parse_mode="HTML",
                    reply_markup=kb,
                )
                sent_messages_info.append((admin_id, sent_msg.message_id))

            else:
                if message.text:
                    text_proof = message.text
                else:
                    "Без доказательств"
                full_text = f"{report_text}\nДоказательства: {text_proof}"
                sent_msg = await bot.send_message(
                    chat_id=admin_id,
                    text=full_text,
                    parse_mode="HTML",
                    reply_markup=kb
                )
                sent_messages_info.append((admin_id, sent_msg.message_id))

        except Exception as e:
            print(f"Ошибка отправки админу {admin_id}: {e}")

    if sent_messages_info:
        if message.from_user.id not in active_alerts:
            active_alerts[message.from_user.id] = []
        active_alerts[message.from_user.id].append(sent_messages_info)

    if "last_bot_msg_id" in data:
        await try_delete(bot, message.chat.id, data["last_bot_msg_id"])
    if album:
        for msg in album:
            await try_delete(bot, message.chat.id, msg.message_id)
    else:
        await try_delete(bot, message.chat.id, message.message_id)

    await state.clear()

    await message.answer(
        "Ваш репорт отправлен организаторам.",
        reply_markup=get_main_kb(message.from_user.id),
    )
