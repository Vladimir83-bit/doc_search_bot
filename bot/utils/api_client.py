import aiohttp
import logging

logger = logging.getLogger(__name__)

async def get_random_fact():
    """Получение случайного факта с внешнего API"""
    try:
        async with aiohttp.ClientSession() as session:
            async with session.get("https://uselessfacts.jsph.pl/api/v2/facts/random") as response:
                if response.status == 200:
                    data = await response.json()
                    return data.get('text', 'Факт не найден')
    except Exception as e:
        logger.error(f"Ошибка API: {e}")
        return "Не удалось получить факт"