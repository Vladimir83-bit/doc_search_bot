import os

class Config:
    # Основные настройки бота
    TOKEN = "7562511884:AAGdhqnv3Gn3cgxD4IxsNGrROS1j1DKFNY0"  # ⚠️ ЗАМЕНИТЕ НА ВАШ ТОКЕН
    
    # Настройки документов
    DOCS_FOLDER = 'docs'
    MAX_FILE_SIZE = 10 * 1024 * 1024  # 10MB
    ALLOWED_EXTENSIONS = ['.txt', '.pdf', '.docx', '.xlsx']
    
    # Настройки базы данных
    DATABASE_URL = "sqlite:///./bot.db"