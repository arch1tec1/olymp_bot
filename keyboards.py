"""Кнопки пользователей бота."""
from aiogram.types import (
    InlineKeyboardButton,
    InlineKeyboardMarkup,
    KeyboardButton,
    ReplyKeyboardMarkup,
)
from config import ADMIN_IDS


def get_main_kb(user_id: int):
    """Панель участника олимпиады."""

    buttons = [
        [KeyboardButton(text="📝 Зарегистрироваться")],
        [KeyboardButton(text="🔐 Получить логин и пароль")],
        [KeyboardButton(text="🔔 Связь с организаторами")],
    ]

    if user_id in ADMIN_IDS:
        buttons.append([KeyboardButton(text="🦾 Админ-панель")])

    return ReplyKeyboardMarkup(keyboard=buttons, resize_keyboard=True)


def get_organizer_kb():
    """В (Связь с организаторами)."""

    return InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(
                    text="👀 Сообщить о нарушении правил",
                    callback_data="report_violation",
                )
            ],
            [
                InlineKeyboardButton(
                    text="🆘 У меня проблема", callback_data="contact_support"
                )
            ],
        ]
    )


def get_admin_panel_kb():
    """Админ-панель."""

    return ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(text="📢 Разослать всем")],
            [KeyboardButton(text="👤 Общение с участником")],
            [KeyboardButton(text="⬅️ Назад в меню")],
        ],
        resize_keyboard=True,
    )


def get_admin_dialog_kb():
    """Диалог админа с участником."""

    return ReplyKeyboardMarkup(
        keyboard=[[KeyboardButton(text="❌ Закончить диалог")]],
        resize_keyboard=True
    )


def get_selection_kb(items, prefix):
    """Генератор для списка УЗ и классов/курсов обучения."""

    buttons = []
    row = []

    for item in items:
        row.append(InlineKeyboardButton(
            ext=item, callback_data=f"{prefix}_{item}")
            )
        if len(row) == 2:
            buttons.append(row)
            row = []
    if row:
        buttons.append(row)

    return InlineKeyboardMarkup(inline_keyboard=buttons)
