import logging
import os

from aiogram import Bot, Dispatcher, Router
from aiogram.fsm.state import State, StatesGroup
from aiogram.fsm.storage.memory import MemoryStorage
from dotenv import load_dotenv

from middlewares import MediaGroupMiddleware

load_dotenv()
API_TOKEN = os.getenv("API_TOKEN")

logging.basicConfig(level=logging.INFO)

bot = Bot(token=API_TOKEN)
dp = Dispatcher(storage=MemoryStorage())
router = Router()

router.message.middleware(MediaGroupMiddleware(latency=0.5))
dp.include_router(router)

# { user_id_автора: [ [(admin_id, message_id), ...], [...] ] }
active_alerts: dict[int, list[list[tuple[int, int]]]] = {}
# { user_id_участника: admin_id_организатора }
active_dialogs: dict[int, int] = {}

SCHOOLS = [
    "Школа №1",
    "Лицей №5",
    "Гимназия №12",
    "МГУ",
    "МГТУ им. Баумана",
]

GRADES = (
    [f"{i} класс" for i in range(1, 12)] +
    [f"{i} курс" for i in range(1, 5)]
    )


# FSM
class Registration(StatesGroup):
    full_name = State()
    phone = State()
    school = State()
    grade = State()
    email = State()
    confirm = State()


class Report(StatesGroup):
    offender_username = State()
    description = State()
    proof = State()
    last_bot_msg_id = State()


class Support(StatesGroup):
    waiting_for_message = State()
    last_bot_msg_id = State()


class AdminPanel(StatesGroup):
    waiting_for_broadcast_content = State()
    waiting_for_user_search = State()
    in_dialog = State()


class UserState(StatesGroup):
    in_dialog_with_admin = State()


async def try_delete(bot: Bot, chat_id: int, message_id: int):
    try:
        await bot.delete_message(chat_id=chat_id, message_id=message_id)
    except Exception:
        pass
