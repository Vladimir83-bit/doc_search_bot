import os
import asyncio
from aiogram import F, types
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup

from bot.core.loader import dp, bot
from bot.core.config import Config
from bot.utils.database import get_user, update_user_activity, increment_documents_count, increment_searches_count
from bot.utils.logger import logger

# Импортируем ваши парсеры
from bot.utils.document_parser import DocumentParser
from bot.utils.file_storage import FileStorage

# Машина состояний для поиска
class SearchStates(StatesGroup):
    waiting_for_search_query = State()

# Клавиатура для личных сообщений
def create_main_keyboard():
    keyboard = types.ReplyKeyboardMarkup(
        keyboard=[
            [types.KeyboardButton(text="🔍 Поиск в документах")],
            [types.KeyboardButton(text="📁 Список документов")],
            [types.KeyboardButton(text="📊 Моя статистика")],
            [types.KeyboardButton(text="❌ Удалить все документы")]
        ],
        resize_keyboard=True
    )
    return keyboard

@dp.message(Command("start"))
async def send_welcome(message: types.Message):
    """Обработчик команд /start"""
    try:
        # Регистрируем пользователя в БД
        user = await get_user(message.from_user.id, message.from_user.username, message.from_user.full_name)
        await update_user_activity(message.from_user.id)
        
        welcome_text = (
            "📚 Бот для поиска в документах\n\n"
            "Отправьте мне документы в форматах:\n"
            "- TXT (текст)\n"
            "- PDF\n"
            "- DOCX (Word)\n"
            "- XLSX (Excel)\n\n"
            "После загрузки используйте кнопки ниже для поиска."
        )
        
        await message.answer(welcome_text, reply_markup=create_main_keyboard())
        logger.info(f"User {message.from_user.id} started bot")
    except Exception as e:
        logger.error(f"Error in send_welcome: {e}")
        await message.answer("❌ Произошла ошибка при запуске")

# ✅ СЮДА ДОБАВЬТЕ ВАШИ СУЩЕСТВУЮЩИЕ ФУНКЦИИ:
# - handle_document
# - list_documents  
# - clear_documents
# - handle_search
# - process_search_query

# Временно добавим заглушки чтобы бот запустился
@dp.message(F.document)
async def handle_document(message: types.Message):
    await message.answer("📄 Функция загрузки документов будет добавлена скоро!")

@dp.message(F.text == "🔍 Поиск в документах")
async def handle_search(message: types.Message, state: FSMContext):
    await message.answer("🔍 Функция поиска будет добавлена скоро!")
    await state.set_state(SearchStates.waiting_for_search_query)

@dp.message(F.text == "📁 Список документов")
async def list_documents(message: types.Message):
    await message.answer("📂 Функция списка документов будет добавлена скоро!")

@dp.message(F.text == "❌ Удалить все документы")
async def clear_documents(message: types.Message):
    await message.answer("🗑️ Функция удаления документов будет добавлена скоро!")