import logging
from aiogram import Bot, Dispatcher, types
from aiogram.types import ReplyKeyboardMarkup, KeyboardButton, InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.utils import executor
from aiogram.dispatcher.filters.state import State, StatesGroup
from aiogram.contrib.fsm_storage.memory import MemoryStorage
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters import Text
from dotenv import load_dotenv
import os

load_dotenv()

BOT_TOKEN = os.getenv("BOT_TOKEN")
ADMIN_ID = int(os.getenv("ADMIN_ID"))

logging.basicConfig(level=logging.INFO)

bot = Bot(token=BOT_TOKEN)
dp = Dispatcher(bot, storage=MemoryStorage())

class Form(StatesGroup):
    action = State()
    amount = State()

start_kb = ReplyKeyboardMarkup(resize_keyboard=True)
start_kb.add(KeyboardButton("💰 Депозит"), KeyboardButton("📤 Вывод"))

@dp.message_handler(commands=['start'])
async def start(message: types.Message):
    await message.answer("Привет! Что вы хотите сделать?", reply_markup=start_kb)

@dp.message_handler(Text(equals=["💰 Депозит", "📤 Вывод"]))
async def choose_action(message: types.Message, state: FSMContext):
    await state.update_data(action=message.text)
    await message.answer("Введите сумму в USD:")
    await Form.amount.set()

@dp.message_handler(state=Form.amount)
async def get_amount(message: types.Message, state: FSMContext):
    data = await state.get_data()
    action = data['action']
    amount = message.text
    username = message.from_user.username or "Без username"
    user_id = message.from_user.id

    action_text = "ДЕПОЗИТ" if action == "💰 Депозит" else "ВЫВОД"

    msg = f"📬 Новая заявка на {action_text}\n👤 Игрок: @{username} (ID: {user_id})\n💵 Сумма: ${amount}"

    buttons = InlineKeyboardMarkup().add(
        InlineKeyboardButton("✅ Подтвердить", callback_data="confirm"),
        InlineKeyboardButton("❌ Отклонить", callback_data="decline")
    )

    await bot.send_message(ADMIN_ID, msg, reply_markup=buttons)
    await message.answer("Ваша заявка отправлена кассиру. Ожидайте подтверждения.")
    await state.finish()

@dp.callback_query_handler(Text(equals=["confirm", "decline"]))
