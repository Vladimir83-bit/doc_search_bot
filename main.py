import asyncio
from bot.core.loader import bot, dp
from bot.core.config import Config
from bot.utils.logger import logger
from bot.utils.database import create_tables
from bot.middlewares.errors import setup_error_handling

# Импортируем обработчики
from bot.handlers import private, common

async def main():
    """Главная функция запуска бота"""
    logger.info("Запуск бота...")
    
    # Создаем таблицы БД
    create_tables()
    logger.info("База данных инициализирована")
    
    # Настройка обработки ошибок
    setup_error_handling(dp)
    
    # Удаляем вебхук и запускаем поллинг
    await bot.delete_webhook(drop_pending_updates=True)
    logger.info("✅ Бот успешно запущен!")
    
    await dp.start_polling(bot)

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        logger.info("Бот остановлен пользователем")
    except Exception as e:
        logger.error(f"Критическая ошибка при запуске: {e}")