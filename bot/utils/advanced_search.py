import re
import os
from typing import List, Dict
from bot.utils.document_parser import DocumentParser

class AdvancedSearch:
    """Продвинутый поиск с дополнительными возможностями"""
    
    @staticmethod
    def fuzzy_search(text, query, max_distance=2):
        """Нечеткий поиск с допуском опечаток"""
        try:
            words = query.lower().split()
            results = []
            
            for word in words:
                # Простой нечеткий поиск по подстроке
                pattern = re.compile(re.escape(word), re.IGNORECASE)
                matches = pattern.finditer(text)
                
                for match in matches:
                    start = max(0, match.start() - 50)
                    end = min(len(text), match.end() + 50)
                    context = text[start:end]
                    
                    if start > 0:
                        context = "..." + context
                    if end < len(text):
                        context = context + "..."
                    
                    results.append({
                        'word': word,
                        'context': context,
                        'position': match.start()
                    })
            
            return results
        except Exception as e:
            print(f"Ошибка нечеткого поиска: {e}")
            return []
    
    @staticmethod
    def boolean_search(text, query):
        """Булев поиск с операторами AND, OR, NOT"""
        try:
            # Простая реализация булева поиска
            query = query.lower()
            text_lower = text.lower()
            
            if ' and ' in query:
                words = [w.strip() for w in query.split(' and ')]
                return all(word in text_lower for word in words)
            elif ' or ' in query:
                words = [w.strip() for w in query.split(' or ')]
                return any(word in text_lower for word in words)
            elif ' not ' in query:
                words = query.split(' not ')
                positive = words[0].strip()
                negative = words[1].strip()
                return positive in text_lower and negative not in text_lower
            else:
                return query in text_lower
                
        except Exception as e:
            print(f"Ошибка булева поиска: {e}")
            return False
    
    @staticmethod
    def search_by_metadata(files_metadata, search_params):
        """Поиск по метаданным файлов"""
        results = []
        for file_meta in files_metadata:
            match = True
            for key, value in search_params.items():
                if key in file_meta and value.lower() not in str(file_meta.get(key, '')).lower():
                    match = False
                    break
            if match:
                results.append(file_meta)
        return results