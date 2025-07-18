import os
from config import Config

class FileStorage:
    """Класс для работы с файлами на диске"""
    
    @staticmethod
    def save_file(file_id, file_name, file_data):
        """Сохранение загруженного файла"""
        try:
            # Создаем папку, если ее нет
            if not os.path.exists(Config.DOCS_FOLDER):
                os.makedirs(Config.DOCS_FOLDER)
            
            # Полный путь к файлу
            file_path = os.path.join(Config.DOCS_FOLDER, file_name)
            
            # Сохраняем файл
            with open(file_path, 'wb') as f:
                f.write(file_data)
            
            return file_path
        except Exception as e:
            print(f"Ошибка сохранения файла: {e}")
            return None

    @staticmethod
    def get_all_docs():
        """Получение списка всех документов"""
        try:
            if not os.path.exists(Config.DOCS_FOLDER):
                return []
                
            return [f for f in os.listdir(Config.DOCS_FOLDER) 
                   if os.path.splitext(f)[1].lower() in Config.ALLOWED_EXTENSIONS]
        except Exception as e:
            print(f"Ошибка чтения списка файлов: {e}")
            return []

    @staticmethod
    def clear_all_docs():
        """Удаление всех документов"""
        try:
            for filename in os.listdir(Config.DOCS_FOLDER):
                file_path = os.path.join(Config.DOCS_FOLDER, filename)
                os.remove(file_path)
            return True
        except Exception as e:
            print(f"Ошибка удаления файлов: {e}")
            return False