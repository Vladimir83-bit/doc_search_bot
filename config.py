import os

class Config:
    # Получите токен у @BotFather в Telegram
    TOKEN = '7562511884:AAGdhqnv3Gn3cgxD4IxsNGrROS1j1DKFNY0'
    
    # Папка для хранения документов
    DOCS_FOLDER = 'docs'
    
    # Максимальный размер файла (10 МБ)
    MAX_FILE_SIZE = 10 * 1024 * 1024
    
    # Разрешенные расширения файлов
    ALLOWED_EXTENSIONS = ['.txt', '.pdf', '.docx', '.xlsx']
    
    # ID разрешенных пользователей (можно получить у @userinfobot)
    ALLOWED_USERS = [123456789]  # Замените на ваш ID