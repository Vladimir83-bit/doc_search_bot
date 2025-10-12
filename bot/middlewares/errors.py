import logging
import traceback
from aiogram import Dispatcher
from aiogram.types import ErrorEvent

logger = logging.getLogger(__name__)

async def global_error_handler(event: ErrorEvent):
    """Глобальный обработчик ошибок"""
    logger.error(f"Ошибка: {event.exception}\nТрассировка: {traceback.format_exc()}")
    
    # Можно отправить сообщение админу или пользователю
    try:
        await event.update.message.answer(
            "😔 Произошла непредвиденная ошибка. Попробуйте позже."
        )
    except:
        pass  # Если нельзя отправить сообщение

def setup_error_handling(dp: Dispatcher):
    dp.errors.register(global_error_handler)