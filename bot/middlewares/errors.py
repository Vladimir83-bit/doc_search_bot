import logging
import traceback
from aiogram import Dispatcher
from aiogram.types import ErrorEvent
from bot.utils.logger import logger

async def global_error_handler(event: ErrorEvent):
    """Глобальный обработчик ошибок"""
    logger.error(f"Ошибка: {event.exception}")
    logger.error(f"Трассировка: {traceback.format_exc()}")
    
    # Пытаемся отправить сообщение пользователю
    try:
        if hasattr(event.update, 'message') and event.update.message:
            await event.update.message.answer(
                "😔 Произошла непредвиденная ошибка. Попробуйте позже или обратитесь к администратору."
            )
    except Exception as e:
        logger.error(f"Не удалось отправить сообщение об ошибке: {e}")
    
    return True

def setup_error_handling(dp: Dispatcher):
    dp.errors.register(global_error_handler)