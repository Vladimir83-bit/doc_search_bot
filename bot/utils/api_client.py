import aiohttp
import logging
import json
from bot.core.config import Config

logger = logging.getLogger(__name__)

class APIClient:
    def __init__(self):
        self.session = None
    
    async def get_session(self):
        if self.session is None:
            self.session = aiohttp.ClientSession()
        return self.session
    
    async def close(self):
        if self.session:
            await self.session.close()
    
    # Новости через NewsAPI
    async def get_news(self, category="technology"):
        """Получение новостей через NewsAPI"""
        try:
            api_key = "your_newsapi_key"  # Зарегистрируйся на newsapi.org
            url = f"https://newsapi.org/v2/top-headlines?category={category}&language=ru&apiKey={api_key}"
            
            async with aiohttp.ClientSession() as session:
                async with session.get(url) as response:
                    if response.status == 200:
                        data = await response.json()
                        articles = data.get('articles', [])[:3]  # Берем 3 статьи
                        
                        news_text = "📰 **Последние новости:**\n\n"
                        for article in articles:
                            title = article.get('title', '')
                            url = article.get('url', '')
                            news_text += f"• {title}\n{url}\n\n"
                        
                        return news_text
                    return "❌ Не удалось получить новости"
        except Exception as e:
            logger.error(f"News API error: {e}")
            return "❌ Ошибка получения новостей"
    
    # Погода через OpenWeatherMap
    async def get_weather(self, city="Москва"):
        """Получение погоды"""
        try:
            api_key = "your_openweather_key"  # Зарегистрируйся на openweathermap.org
            url = f"http://api.openweathermap.org/data/2.5/weather?q={city}&appid={api_key}&units=metric&lang=ru"
            
            async with aiohttp.ClientSession() as session:
                async with session.get(url) as response:
                    if response.status == 200:
                        data = await response.json()
                        temp = data['main']['temp']
                        description = data['weather'][0]['description']
                        return f"🌤️ Погода в {city}: {temp}°C, {description}"
                    return "❌ Не удалось получить погоду"
        except Exception as e:
            logger.error(f"Weather API error: {e}")
            return "❌ Ошибка получения погоды"
    
    # Случайные факты
    async def get_random_fact(self):
        """Получение случайного факта"""
        try:
            async with aiohttp.ClientSession() as session:
                async with session.get("https://uselessfacts.jsph.pl/api/v2/facts/random?language=ru") as response:
                    if response.status == 200:
                        data = await response.json()
                        return f"🤔 Случайный факт: {data.get('text', 'Факт не найден')}"
                    return "❌ Не удалось получить факт"
        except Exception as e:
            logger.error(f"Random fact API error: {e}")
            return "❌ Ошибка получения факта"

api_client = APIClient()