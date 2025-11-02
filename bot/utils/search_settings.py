import json
import os
from pathlib import Path

class SearchSettings:
    """Класс для управления настройками поиска"""
    
    def __init__(self):
        self.settings_file = Path("search_settings.json")
        self.default_settings = {
            'context_size': 100,
            'max_matches_per_file': 10,
            'search_type': 'exact',  # exact, fuzzy, boolean
            'auto_translate': False,
            'show_preview': True
        }
        self.settings = self.load_settings()
    
    def load_settings(self):
        """Загрузка настроек из файла"""
        try:
            if self.settings_file.exists():
                with open(self.settings_file, 'r', encoding='utf-8') as f:
                    return json.load(f)
            return self.default_settings.copy()
        except Exception:
            return self.default_settings.copy()
    
    def save_settings(self):
        """Сохранение настроек в файл"""
        try:
            with open(self.settings_file, 'w', encoding='utf-8') as f:
                json.dump(self.settings, f, ensure_ascii=False, indent=2)
            return True
        except Exception as e:
            print(f"Ошибка сохранения настроек: {e}")
            return False
    
    def get_setting(self, key, user_id=None):
        """Получение значения настройки"""
        if user_id:
            # В будущем можно сделать персональные настройки
            return self.settings.get(key, self.default_settings.get(key))
        return self.settings.get(key, self.default_settings.get(key))
    
    def set_setting(self, key, value, user_id=None):
        """Установка значения настройки"""
        self.settings[key] = value
        return self.save_settings()
    
    def get_all_settings(self):
        """Получение всех настроек"""
        return self.settings.copy()

# Глобальный экземпляр настроек
search_settings = SearchSettings()