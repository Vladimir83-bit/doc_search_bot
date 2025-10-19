from aiogram import F, types
from aiogram.filters import Command
from bot.core.loader import dp
from bot.utils.database import get_user
from bot.utils.logger import logger

@dp.message(Command("stats"))
async def show_stats(message: types.Message):
    """Показать статистику пользователя"""
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
        logger.info(f"User {message.from_user.id} checked stats")
    except Exception as e:
        logger.error(f"Error showing stats: {e}")
        await message.answer("❌ Не удалось загрузить статистику")

@dp.message(Command("id"))
async def show_user_id(message: types.Message):
    """Показать ID пользователя"""
    await message.answer(f"🆔 Ваш ID: `{message.from_user.id}`", parse_mode="Markdown")

@dp.message(Command("help"))
async def show_help(message: types.Message):
    """Показать справку"""
    help_text = (
        "📚 **Доступные команды:**\n\n"
        "/start - Начать работу\n"
        "/help - Показать справку\n"
        "/stats - Показать статистику\n"
        "/id - Показать ваш ID\n\n"
        "**Основные функции:**\n"
        "• Загружайте документы (TXT, PDF, DOCX, XLSX)\n"
        "• Ищите текст в документах\n"
        "• Просматривайте список документов"
    )
    await message.answer(help_text)

@dp.message(F.text == "📊 Моя статистика")
async def stats_button(message: types.Message):
    """Обработчик кнопки статистики"""
    await show_stats(message)