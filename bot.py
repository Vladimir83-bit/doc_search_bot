import os
import asyncio
from aiogram import Bot, Dispatcher, types, F
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from config import Config
from file_storage import FileStorage
from document_parser import DocumentParser

# Инициализация бота
bot = Bot(token=Config.TOKEN)
dp = Dispatcher()

# Машина состояний для поиска
class SearchStates(StatesGroup):
    waiting_for_search_query = State()

# Клавиатура
def create_main_keyboard():
    keyboard = types.ReplyKeyboardMarkup(
        keyboard=[
            [types.KeyboardButton(text="🔍 Поиск в документах")],
            [types.KeyboardButton(text="📁 Список документов")],
            [types.KeyboardButton(text="❌ Удалить все документы")]
        ],
        resize_keyboard=True
    )
    return keyboard

# Обработчик /start и /help
@dp.message(Command("start", "help"))
async def send_welcome(message: types.Message):
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

# Обработчик документов
@dp.message(F.document)
async def handle_document(message: types.Message):
    try:
        # Проверка размера файла
        if message.document.file_size > Config.MAX_FILE_SIZE:
            await message.answer(f"⚠ Файл слишком большой. Максимум: {Config.MAX_FILE_SIZE//1024//1024}MB")
            return
            
        # Проверка расширения
        file_name = message.document.file_name
        file_ext = os.path.splitext(file_name)[1].lower()
        
        if file_ext not in Config.ALLOWED_EXTENSIONS:
            await message.answer(f"⚠ Неподдерживаемый формат. Разрешенные: {', '.join(Config.ALLOWED_EXTENSIONS)}")
            return
            
        # Скачивание файла
        file = await bot.get_file(message.document.file_id)
        file_data = await bot.download_file(file.file_path)
        
        # Сохранение файла
        saved_path = FileStorage.save_file(message.document.file_id, file_name, file_data.read())
        
        if saved_path:
            await message.answer(f"✅ Документ '{file_name}' успешно загружен!")
        else:
            await message.answer("❌ Ошибка при сохранении файла")
            
    except Exception as e:
        await message.answer(f"❌ Произошла ошибка: {str(e)}")

# Обработчик кнопок
@dp.message(F.text == "📁 Список документов")
async def list_documents(message: types.Message):
    docs = FileStorage.get_all_docs()
    
    if docs:
        response = "📂 Загруженные документы:\n\n" + "\n".join(f"▫ {doc}" for doc in docs)
    else:
        response = "📭 Нет загруженных документов"
        
    await message.answer(response, reply_markup=create_main_keyboard())

@dp.message(F.text == "❌ Удалить все документы")
async def clear_documents(message: types.Message):
    if FileStorage.clear_all_docs():
        await message.answer("✅ Все документы удалены", reply_markup=create_main_keyboard())
    else:
        await message.answer("❌ Ошибка при удалении документов")

@dp.message(F.text == "🔍 Поиск в документах")
async def handle_search(message: types.Message, state: FSMContext):
    await message.answer("🔍 Введите текст для поиска:")
    await state.set_state(SearchStates.waiting_for_search_query)

# Обработчик поискового запроса
@dp.message(SearchStates.waiting_for_search_query)
async def process_search_query(message: types.Message, state: FSMContext):
    search_text = message.text.lower()
    found_in = []
    
    # Поиск по всем документам
    for doc in FileStorage.get_all_docs():
        file_path = os.path.join(Config.DOCS_FOLDER, doc)
        content = DocumentParser.parse_file(file_path).lower()
        
        if search_text in content:
            found_in.append(doc)
    
    # Формирование ответа
    if found_in:
        response = "🔍 Найдено в документах:\n\n" + "\n".join(f"📌 {doc}" for doc in found_in)
    else:
        response = "😞 Ничего не найдено"
    
    await message.answer(response, reply_markup=create_main_keyboard())
    await state.clear()  # Сбрасываем состояние

# Запуск бота
async def main():
    # Принудительно удаляем вебхук
    await bot.delete_webhook(drop_pending_updates=True)
    print("🟢 Бот запущен...")
    await dp.start_polling(bot)

if __name__ == '__main__':
    asyncio.run(main())