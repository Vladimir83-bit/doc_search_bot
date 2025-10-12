import asyncio
import logging
from bot.core.loader import bot, dp
from bot.core.config import Config
from bot.utils.logger import setup_logger

# Импортируем обработчики
from bot.handlers import private, common

# Настройка логирования
logger = setup_logger()

async def main():
    """Главная функция запуска бота"""
    logger.info("Запуск улучшенной версии бота...")
    
    # Удаляем вебхук и запускаем поллинг
    await bot.delete_webhook(drop_pending_updates=True)
    logger.info("Бот успешно запущен и готов к работе!")
    await dp.start_polling(bot)

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        logger.info("Бот остановлен пользователем")
    except Exception as e:
        logger.error(f"Критическая ошибка при запуске: {e}")