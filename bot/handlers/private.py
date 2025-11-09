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
from bot.utils.document_parser import DocumentParser
from bot.utils.file_storage import FileStorage
from bot.utils.search_settings import search_settings
from bot.utils.api_client import api_client

# Машина состояний для поиска
class SearchStates(StatesGroup):
    waiting_for_search_query = State()

# Полная клавиатура со всем функционалом
def create_main_keyboard():
    keyboard = types.ReplyKeyboardMarkup(
        keyboard=[
            [
                types.KeyboardButton(text="🔍 Поиск"),
                types.KeyboardButton(text="📁 Документы"), 
                types.KeyboardButton(text="📊 Статистика"),
                types.KeyboardButton(text="⚙️ Настройки")
            ],
            [
                types.KeyboardButton(text="🎯 Умный поиск"),
                types.KeyboardButton(text="🌐 Переводчик"),
                types.KeyboardButton(text="🗑️ Удалить всё"),
                types.KeyboardButton(text="❓ Помощь")
            ],
            [
                types.KeyboardButton(text="📰 Новости"),
                types.KeyboardButton(text="🌤️ Погода"),
                types.KeyboardButton(text="🎭 Развлечения")
            ]
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
            "**Основные функции:**\n"
            "• Загрузка документов (TXT, PDF, DOCX, XLSX)\n"  
            "• Поиск текста в документах\n"
            "• Просмотр статистики и настроек\n"
            "• Новости, погода и развлечения\n\n"
            "💡 **Используйте кнопки ниже для навигации**"
        )
        
        await message.answer(welcome_text, reply_markup=create_main_keyboard())
        logger.info(f"User {message.from_user.id} started bot")
    except Exception as e:
        logger.error(f"Error in send_welcome: {e}")
        await message.answer("❌ Произошла ошибка при запуске")

# ОБРАБОТЧИКИ КНОПОК ПЕРВОЙ СТРОКИ
@dp.message(F.text == "🔍 Поиск")
async def handle_search(message: types.Message, state: FSMContext):
    """Начало поиска в документах"""
    docs = FileStorage.get_all_docs()
    if not docs:
        await message.answer("📂 Сначала загрузите документы для поиска!")
        return
        
    await message.answer("🔍 Введите поисковый запрос:")
    await state.set_state(SearchStates.waiting_for_search_query)

@dp.message(F.text == "📁 Документы")
async def list_documents(message: types.Message):
    """Показать список документов"""
    try:
        docs = FileStorage.get_all_docs()
        
        if docs:
            docs_list = "\n".join([f"• {doc}" for doc in docs[:10]])
            text = f"📂 Ваши документы ({len(docs)}):\n\n{docs_list}"
            if len(docs) > 10:
                text += f"\n\n... и еще {len(docs) - 10} документов"
        else:
            text = "📂 У вас пока нет документов"
            
        await message.answer(text)
    except Exception as e:
        logger.error(f"Error listing documents: {e}")
        await message.answer("❌ Ошибка при получении списка документов")

@dp.message(F.text == "📊 Статистика")
async def stats_button(message: types.Message):
    """Обработчик кнопки статистики"""
    try:
        user = await get_user(message.from_user.id)
        
        stats_text = (
            f"📊 Ваша статистика:\n"
            f"👤 Пользователь: {user.full_name}\n"
            f"📅 Зарегистрирован: {user.created_at.strftime('%d.%m.%Y')}\n"
            f"📄 Загружено документов: {user.documents_uploaded}\n"
            f"🔍 Выполнено поисков: {user.searches_performed}\n"
            f"🕒 Последняя активность: {user.last_activity.strftime('%H:%M %d.%m.%Y')}"
        )
        
        await message.answer(stats_text)
        logger.info(f"User {message.from_user.id} checked stats via button")
    except Exception as e:
        logger.error(f"Error showing stats from button: {e}")
        await message.answer("❌ Не удалось загрузить статистику")

@dp.message(F.text == "⚙️ Настройки")
async def settings_menu(message: types.Message):
    """Меню настроек поиска"""
    settings = search_settings.get_all_settings()
    
    settings_text = (
        "⚙️ **Настройки поиска**\n\n"
        f"📏 **Размер контекста:** {settings['context_size']} символов\n"
        f"📄 **Макс. совпадений на файл:** {settings['max_matches_per_file']}\n"
        f"🔍 **Тип поиска:** {settings['search_type']}\n\n"
        "**Команды для изменения:**\n"
        "`/context 150` - размер контекста\n"
        "`/matches 5` - макс. совпадений\n"
        "`/search_type fuzzy` - тип поиска"
    )
    
    await message.answer(settings_text, parse_mode="Markdown")

# ОБРАБОТЧИКИ КНОПОК ВТОРОЙ СТРОКИ
@dp.message(F.text == "🎯 Умный поиск")
async def smart_search_menu(message: types.Message):
    """Меню умного поиска"""
    menu_text = (
        "🎯 **Умный поиск**\n\n"
        "Для использования отправьте команду:\n\n"
        "**Нечеткий поиск** (с учетом опечаток):\n"
        "`/fuzzy ваш запрос`\n\n"
        "**Булев поиск** (с операторами):\n"
        "`/boolean запрос and другой`\n"
        "`/boolean запрос or другой`\n"
        "`/boolean запрос not исключение`"
    )
    await message.answer(menu_text)

@dp.message(F.text == "🌐 Переводчик")
async def translate_menu(message: types.Message):
    """Меню переводчика"""
    menu_text = (
        "🌐 **Переводчик**\n\n"
        "**Перевод текста:**\n"
        "`/translate en ваш текст` - на английский\n"
        "`/translate de ваш текст` - на немецкий\n\n"
        "**Поиск синонимов:**\n"
        "`/synonyms слово`\n\n"
        "**Дополнительно:**\n"
        "`/weather город` - погода\n"
        "`/news тема` - новости"
    )
    await message.answer(menu_text)

@dp.message(F.text == "🗑️ Удалить всё")
async def clear_documents(message: types.Message):
    """Удаление всех документов"""
    try:
        docs = FileStorage.get_all_docs()
        if not docs:
            await message.answer("📂 Нет документов для удаления.")
            return
            
        if FileStorage.clear_all_docs():
            await message.answer("🗑️ Все документы удалены!")
            logger.info(f"User {message.from_user.id} cleared all documents")
        else:
            await message.answer("❌ Ошибка при удалении документов")
    except Exception as e:
        logger.error(f"Error clearing documents: {e}")
        await message.answer("❌ Ошибка при удалении документов")

@dp.message(F.text == "❓ Помощь")
async def help_command(message: types.Message):
    """Помощь по боту"""
    help_text = (
        "❓ **Помощь по боту**\n\n"
        "**Основные команды:**\n"
        "`/search` - поиск в документах\n"
        "`/list` - список документов\n"
        "`/stats` - статистика\n"
        "`/settings` - настройки\n\n"
        "**Умный поиск:**\n"
        "`/fuzzy запрос` - нечеткий поиск\n"
        "`/boolean запрос` - булев поиск\n\n"
        "**Переводчик:**\n"
        "`/translate en текст` - перевод\n"
        "`/synonyms слово` - синонимы\n\n"
        "**Настройки:**\n"
        "`/context 150` - размер контекста\n"
        "`/matches 5` - макс. совпадений\n"
        "`/search_type fuzzy` - тип поиска\n\n"
        "💡 **Просто используйте кнопки ниже для быстрого доступа!**"
    )
    await message.answer(help_text)

# ОБРАБОТЧИКИ КНОПОК ТРЕТЬЕЙ СТРОКИ (API ФУНКЦИИ)
@dp.message(F.text == "📰 Новости")
async def news_command(message: types.Message):
    """Получить последние новости"""
    try:
        await message.answer("📰 Загружаю последние новости...")
        news = await api_client.get_news("technology")
        await message.answer(news, disable_web_page_preview=True)
    except Exception as e:
        logger.error(f"News error: {e}")
        await message.answer("❌ Не удалось загрузить новости")

@dp.message(F.text == "🌤️ Погода")
async def weather_command(message: types.Message):
    """Получить погоду"""
    try:
        await message.answer("🌤️ Загружаю данные о погоде...")
        weather = await api_client.get_weather("Москва")
        await message.answer(weather)
    except Exception as e:
        logger.error(f"Weather error: {e}")
        await message.answer("❌ Не удалось загрузить погоду")

@dp.message(F.text == "🎭 Развлечения")
async def entertainment_command(message: types.Message):
    """Развлекательные функции"""
    try:
        # Случайный факт
        fact = await api_client.get_random_fact()
        
        # Отправляем мем
        await message.answer_photo(
            photo="https://i.imgur.com/1Bc7Y7s.jpeg",  # Замени на свою ссылку
            caption=f"{fact}\n\n😂 Вот мем для настроения!"
        )
    except Exception as e:
        logger.error(f"Entertainment error: {e}")
        await message.answer("❌ Ошибка при загрузке развлечений")

# ОБРАБОТЧИКИ РАЗНЫХ ТИПОВ КОНТЕНТА
@dp.message(F.photo)
async def handle_photo(message: types.Message):
    """Обработка фотографий"""
    try:
        # Сохраняем информацию о фото в лог
        photo_info = (
            f"📸 Получено фото от {message.from_user.full_name}\n"
            f"Размер: {message.photo[-1].file_size} байт\n"
            f"ID файла: {message.photo[-1].file_id}"
        )
        logger.info(f"Photo received from {message.from_user.id}: {message.photo[-1].file_id}")
        
        await message.answer(
            f"{photo_info}\n\n"
            "Классное фото! Могу его проанализировать или сохранить."
        )
        
        # Можно отправить ответное фото
        await message.answer_photo(
            photo="https://i.imgur.com/1Bc7Y7s.jpeg",  # Замени на свою ссылку
            caption="Вот мой ответный мем! 😊"
        )
    except Exception as e:
        logger.error(f"Photo handling error: {e}")
        await message.answer("❌ Ошибка при обработке фото")

@dp.message(F.sticker)
async def handle_sticker(message: types.Message):
    """Обработка стикеров"""
    try:
        sticker_info = (
            f"😊 Стикер от {message.from_user.full_name}\n"
            f"ID набора: {message.sticker.set_name}\n"
            f"Эмодзи: {message.sticker.emoji}"
        )
        logger.info(f"Sticker received from {message.from_user.id}: {message.sticker.file_id}")
        
        await message.answer(sticker_info)
        
        # Отправляем ответный стикер
        await message.answer_sticker(
            sticker="CAACAgIAAxkBAAIBMWgAApV2AAE1lAAAAAEAAgMAA3dJwAACBCkAAwABgUo",  # Замени на ID своего стикера
            reply_to_message_id=message.message_id
        )
    except Exception as e:
        logger.error(f"Sticker handling error: {e}")
        await message.answer("😊 Крутой стикер! К сожалению, не могу отправить ответный стикер.")

@dp.message(F.video)
async def handle_video(message: types.Message):
    """Обработка видео"""
    try:
        video_info = (
            f"🎥 Видео от {message.from_user.full_name}\n"
            f"Длительность: {message.video.duration} сек\n"
            f"Размер: {message.video.file_size} байт\n"
            f"Разрешение: {message.video.width}x{message.video.height}"
        )
        logger.info(f"Video received from {message.from_user.id}: {message.video.file_id}")
        
        await message.answer(
            f"{video_info}\n\n"
            "Видео получено! Могу его проанализировать или сохранить метаданные."
        )
    except Exception as e:
        logger.error(f"Video handling error: {e}")
        await message.answer("❌ Ошибка при обработке видео")

@dp.message(F.voice)
async def handle_voice(message: types.Message):
    """Обработка голосовых сообщений"""
    try:
        voice_info = (
            f"🎤 Голосовое сообщение от {message.from_user.full_name}\n"
            f"Длительность: {message.voice.duration} сек\n"
            f"Размер: {message.voice.file_size} байт"
        )
        logger.info(f"Voice received from {message.from_user.id}: {message.voice.file_id}")
        
        await message.answer(
            f"{voice_info}\n\n"
            "Голосовое сообщение получено! К сожалению, пока не умею распознавать речь."
        )
    except Exception as e:
        logger.error(f"Voice handling error: {e}")
        await message.answer("❌ Ошибка при обработке голосового сообщения")

@dp.message(F.animation)
async def handle_gif(message: types.Message):
    """Обработка GIF-анимаций"""
    try:
        gif_info = (
            f"🎬 GIF от {message.from_user.full_name}\n"
            f"Длительность: {message.animation.duration} сек\n"
            f"Размер: {message.animation.file_size} байт"
        )
        logger.info(f"GIF received from {message.from_user.id}: {message.animation.file_id}")
        
        await message.answer(
            f"{gif_info}\n\n"
            "Крутая GIF-анимация! Сохранил информацию о ней."
        )
    except Exception as e:
        logger.error(f"GIF handling error: {e}")
        await message.answer("❌ Ошибка при обработке GIF")

# КОМАНДЫ ДЛЯ ОТПРАВКИ РАЗНОГО КОНТЕНТА
@dp.message(Command("meme"))
async def send_meme(message: types.Message):
    """Отправить мем"""
    try:
        await message.answer_photo(
            photo="https://i.imgur.com/1Bc7Y7s.jpeg",  # Замени на реальную ссылку
            caption="😂 Вот свежий мем для тебя! Надеюсь, поднимет настроение!"
        )
        logger.info(f"Sent meme to {message.from_user.id}")
    except Exception as e:
        logger.error(f"Meme sending error: {e}")
        await message.answer("❌ Не удалось отправить мем")

@dp.message(Command("sticker"))
async def send_sticker(message: types.Message):
    """Отправить стикер"""
    try:
        await message.answer_sticker(
            sticker="CAACAgIAAxkBAAIBMWgAApV2AAE1lAAAAAEAAgMAA3dJwAACBCkAAwABgUo",  # Замени на ID своего стикера
            reply_to_message_id=message.message_id
        )
        logger.info(f"Sent sticker to {message.from_user.id}")
    except Exception as e:
        logger.error(f"Sticker sending error: {e}")
        await message.answer("❌ Не удалось отправить стикер")

@dp.message(Command("gif"))
async def send_gif(message: types.Message):
    """Отправить GIF"""
    try:
        await message.answer_animation(
            animation="https://media.giphy.com/media/3o7aCTPPm4OHfRLSH6/giphy.gif",  # Замени на свою ссылку
            caption="🎬 Вот крутая GIF-анимация!"
        )
        logger.info(f"Sent GIF to {message.from_user.id}")
    except Exception as e:
        logger.error(f"GIF sending error: {e}")
        await message.answer("❌ Не удалось отправить GIF")

# ТЕКСТОВЫЕ КОМАНДЫ ДЛЯ БЫСТРОГО ДОСТУПА
@dp.message(Command("search"))
async def search_command(message: types.Message, state: FSMContext):
    await handle_search(message, state)

@dp.message(Command("list"))
async def list_command(message: types.Message):
    await list_documents(message)

@dp.message(Command("stats"))
async def stats_command(message: types.Message):
    await stats_button(message)

@dp.message(Command("settings"))
async def settings_command(message: types.Message):
    await settings_menu(message)

@dp.message(Command("help"))
async def help_text_command(message: types.Message):
    await help_command(message)

@dp.message(Command("news"))
async def news_text_command(message: types.Message):
    await news_command(message)

@dp.message(Command("weather"))
async def weather_text_command(message: types.Message):
    await weather_command(message)

# СУЩЕСТВУЮЩИЕ ОБРАБОТЧИКИ (без изменений)
@dp.message(F.document)
async def handle_document(message: types.Message):
    """Обработчик загрузки документов"""
    try:
        document = message.document
        
        if document.file_size > Config.MAX_FILE_SIZE:
            await message.answer("❌ Файл слишком большой (максимум 10МБ)")
            return
        
        file_ext = os.path.splitext(document.file_name)[1].lower()
        if file_ext not in Config.ALLOWED_EXTENSIONS:
            await message.answer(f"❌ Неподдерживаемый формат. Разрешены: {', '.join(Config.ALLOWED_EXTENSIONS)}")
            return
        
        file_info = await bot.get_file(document.file_id)
        downloaded_file = await bot.download_file(file_info.file_path)
        file_data = downloaded_file.read()
        
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

@dp.message(SearchStates.waiting_for_search_query)
async def process_search_query(message: types.Message, state: FSMContext):
    """Обработка поискового запроса"""
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
        
        context_size = search_settings.get_setting('context_size')
        max_matches = search_settings.get_setting('max_matches_per_file')
        
        found_results = []
        total_matches = 0
        
        for doc_name in docs:
            doc_path = os.path.join(Config.DOCS_FOLDER, doc_name)
            text = DocumentParser.parse_file(doc_path)
            
            if text and query in text.lower():
                matches = DocumentParser.find_all_matches(text, query, max_matches=max_matches, context_size=context_size)
                
                if matches:
                    found_results.append({
                        'filename': doc_name,
                        'matches': matches,
                        'match_count': len(matches)
                    })
                    total_matches += len(matches)
        
        if found_results:
            response = f"🔍 Найдено {total_matches} совпадений в {len(found_results)} документах:\n\n"
            
            for result in found_results:
                response += f"📄 **{result['filename']}** ({result['match_count']} совпадений)\n"
                
                for i, match in enumerate(result['matches'], 1):
                    response += f"**Совпадение {i}:**\n"
                    response += f"```\n{match}\n```\n"
                
                response += "\n"
            
            response += f"💡 Запрос: '{query}'\n"
            response += f"⚙️ Настройки: контекст {context_size} симв., макс. {max_matches} совпад./файл"
            
            if len(response) > 4000:
                response = f"🔍 Найдено {total_matches} совпадений в {len(found_results)} документах:\n\n"
                
                for result in found_results[:2]:
                    response += f"📄 **{result['filename']}** ({result['match_count']} совпадений)\n"
                    
                    for i, match in enumerate(result['matches'][:3], 1):
                        response += f"**Совпадение {i}:**\n"
                        response += f"```\n{match[:150]}...\n```\n"
                    
                    response += "\n"
                
                if len(found_results) > 2:
                    response += f"💡 Показаны первые 2 из {len(found_results)} файлов\n"
                
                response += f"💡 Запрос: '{query}'\n"
                response += f"⚙️ Настройки: контекст {context_size} симв., макс. {max_matches} совпад./файл"
                
        else:
            response = f"❌ По запросу '{query}' ничего не найдено"
        
        await message.answer(response, parse_mode="Markdown")
        await increment_searches_count(message.from_user.id)
        logger.info(f"User {message.from_user.id} searched for '{query}', found {total_matches} matches in {len(found_results)} files")
        
    except Exception as e:
        logger.error(f"Search error: {e}")
        await message.answer("❌ Ошибка при выполнении поиска")
    
    await state.clear()

# КОМАНДЫ НАСТРОЕК
@dp.message(Command("context"))
async def set_context_size(message: types.Message):
    """Установка размера контекста"""
    try:
        parts = message.text.split()
        if len(parts) != 2:
            await message.answer("❌ Использование: `/context 150`")
            return
        
        size = int(parts[1])
        if size < 50 or size > 500:
            await message.answer("❌ Размер контекста должен быть от 50 до 500 символов")
            return
        
        if search_settings.set_setting('context_size', size):
            await message.answer(f"✅ Размер контекста изменен на {size} символов")
        else:
            await message.answer("❌ Ошибка сохранения настроек")
            
    except ValueError:
        await message.answer("❌ Укажите число: `/context 150`")
    except Exception as e:
        logger.error(f"Context setting error: {e}")
        await message.answer("❌ Ошибка при изменении настроек")

@dp.message(Command("matches"))
async def set_max_matches(message: types.Message):
    """Установка максимального количества совпадений"""
    try:
        parts = message.text.split()
        if len(parts) != 2:
            await message.answer("❌ Использование: `/matches 5`")
            return
        
        matches = int(parts[1])
        if matches < 1 or matches > 50:
            await message.answer("❌ Количество совпадений должно быть от 1 до 50")
            return
        
        if search_settings.set_setting('max_matches_per_file', matches):
            await message.answer(f"✅ Макс. совпадений изменено на {matches}")
        else:
            await message.answer("❌ Ошибка сохранения настроек")
            
    except ValueError:
        await message.answer("❌ Укажите число: `/matches 5`")
    except Exception as e:
        logger.error(f"Matches setting error: {e}")
        await message.answer("❌ Ошибка при изменении настроек")

@dp.message(Command("search_type"))
async def set_search_type(message: types.Message):
    """Установка типа поиска"""
    try:
        parts = message.text.split()
        if len(parts) != 2:
            await message.answer("❌ Использование: `/search_type exact|fuzzy|boolean`")
            return
        
        search_type = parts[1].lower()
        if search_type not in ['exact', 'fuzzy', 'boolean']:
            await message.answer("❌ Доступные типы: exact, fuzzy, boolean")
            return
        
        if search_settings.set_setting('search_type', search_type):
            await message.answer(f"✅ Тип поиска изменен на '{search_type}'")
        else:
            await message.answer("❌ Ошибка сохранения настроек")
            
    except Exception as e:
        logger.error(f"Search type setting error: {e}")
        await message.answer("❌ Ошибка при изменении настроек")

# Обработчик для любых текстовых сообщений
@dp.message(F.text)
async def handle_text_messages(message: types.Message):
    """Обработчик любых текстовых сообщений"""
    if message.text not in ["🔍 Поиск", "📁 Документы", "📊 Статистика", "⚙️ Настройки",
                          "🎯 Умный поиск", "🌐 Переводчик", "🗑️ Удалить всё", "❓ Помощь",
                          "📰 Новости", "🌤️ Погода", "🎭 Развлечения"]:
        await message.answer("🤖 Используйте кнопки ниже для работы с ботом!", reply_markup=create_main_keyboard())