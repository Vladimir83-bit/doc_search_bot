from aiogram import Bot
from config import Config

async def delete_webhook():
    bot = Bot(token=Config.TOKEN)
    await bot.delete_webhook()
    print("✅ Вебхук удален!")
    await bot.session.close()

if __name__ == '__main__':
    import asyncio
    asyncio.run(delete_webhook())