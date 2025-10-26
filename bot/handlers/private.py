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

@dp.message(F.document)
async def handle_document(message: types.Message):
    """Обработчик загрузки документов - РЕАЛЬНАЯ ЗАГРУЗКА"""
    try:
        document = message.document
        
        # Проверяем размер файла
        if document.file_size > Config.MAX_FILE_SIZE:
            await message.answer("❌ Файл слишком большой (максимум 10МБ)")
            return
        
        # Проверяем расширение
        file_ext = os.path.splitext(document.file_name)[1].lower()
        if file_ext not in Config.ALLOWED_EXTENSIONS:
            await message.answer(f"❌ Неподдерживаемый формат. Разрешены: {', '.join(Config.ALLOWED_EXTENSIONS)}")
            return
        
        # Скачиваем файл
        file_info = await bot.get_file(document.file_id)
        downloaded_file = await bot.download_file(file_info.file_path)
        file_data = downloaded_file.read()
        
        # Сохраняем файл
        saved_path = FileStorage.save_file(document.file_id, document.file_name, file_data)
        
        if saved_path:
            await message.answer(f"✅ Документ '{document.file_name}' успешно загружен!")
            await increment_documents_count(message.from_user.id)
            logger.info(f"User {message.from_user.id} uploaded {document.file_name}")
        else:
            await message.answer("❌ Ошибка при сохранении файла")
            
    except Exception as e:
        logger.error(f"Error handling document: {e}")
        await message.answer("❌ Ошибка при обработке документа")

@dp.message(F.text == "🔍 Поиск в документах")
async def handle_search(message: types.Message, state: FSMContext):
    """Начало поиска в документах"""
    # Проверяем есть ли документы
    docs = FileStorage.get_all_docs()
    if not docs:
        await message.answer("📂 Сначала загрузите документы для поиска!")
        return
        
    await message.answer("🔍 Введите поисковый запрос:")
    await state.set_state(SearchStates.waiting_for_search_query)

@dp.message(SearchStates.waiting_for_search_query)
async def process_search_query(message: types.Message, state: FSMContext):
    """Обработка поискового запроса - РЕАЛЬНЫЙ ПОИСК"""
    try:
        query = message.text.lower().strip()
        
        if not query:
            await message.answer("❌ Введите непустой запрос для поиска")
            await state.clear()
            return
        
        docs = FileStorage.get_all_docs()
        
        if not docs:
            await message.answer("📂 Документы не найдены. Сначала загрузите документы!")
            await state.clear()
            return
        
        found_results = []
        
        # Ищем в каждом документе
        for doc_name in docs:
            doc_path = os.path.join(Config.DOCS_FOLDER, doc_name)
            
            # Извлекаем текст из документа
            text = DocumentParser.parse_file(doc_path)
            
            if text and query in text.lower():
                # Нашли совпадение - добавляем в результаты
                found_results.append(doc_name)
        
        # Формируем ответ
        if found_results:
            results_text = "\n".join([f"• {doc}" for doc in found_results])
            response = (
                f"🔍 Найдено в {len(found_results)} документах:\n\n"
                f"{results_text}\n\n"
                f"💡 Запрос: '{query}'"
            )
        else:
            response = f"❌ По запросу '{query}' ничего не найдено"
        
        await message.answer(response)
        await increment_searches_count(message.from_user.id)
        logger.info(f"User {message.from_user.id} searched for '{query}', found {len(found_results)} results")
        
    except Exception as e:
        logger.error(f"Search error: {e}")
        await message.answer("❌ Ошибка при выполнении поиска")
    
    await state.clear()

@dp.message(F.text == "📁 Список документов")
async def list_documents(message: types.Message):
    """Показать список документов"""
    try:
        docs = FileStorage.get_all_docs()
        
        if docs:
            docs_list = "\n".join([f"• {doc}" for doc in docs[:10]])  # первые 10 документов
            text = f"📂 Ваши документы ({len(docs)}):\n\n{docs_list}"
            if len(docs) > 10:
                text += f"\n\n... и еще {len(docs) - 10} документов"
        else:
            text = "📂 У вас пока нет документов"
            
        await message.answer(text)
    except Exception as e:
        logger.error(f"Error listing documents: {e}")
        await message.answer("❌ Ошибка при получении списка документов")

@dp.message(F.text == "❌ Удалить все документы")
async def clear_documents(message: types.Message):
    """Удалить все документы"""
    try:
        if FileStorage.clear_all_docs():
            await message.answer("🗑️ Все документы удалены!")
            logger.info(f"User {message.from_user.id} cleared all documents")
        else:
            await message.answer("❌ Ошибка при удалении документов")
    except Exception as e:
        logger.error(f"Error clearing documents: {e}")
        await message.answer("❌ Ошибка при удалении документов")

# Добавим обработчик для любых текстовых сообщений
@dp.message(F.text)
async def handle_text_messages(message: types.Message):
    """Обработчик любых текстовых сообщений"""
    if message.text not in ["🔍 Поиск в документах", "📁 Список документов", "📊 Моя статистика", "❌ Удалить все документы"]:
        await message.answer("🤖 Используйте кнопки ниже для работы с ботом!")