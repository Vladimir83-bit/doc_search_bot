from PyPDF2 import PdfReader
from docx import Document
import pandas as pd
import os
import re

class DocumentParser:
    """Класс для извлечения текста из разных форматов документов"""
    
    @staticmethod
    def parse_text(file_path):
        """Чтение обычных текстовых файлов (.txt)"""
        try:
            # Пробуем разные кодировки
            encodings = ['utf-8', 'cp1251', 'windows-1251', 'latin-1']
            for encoding in encodings:
                try:
                    with open(file_path, 'r', encoding=encoding) as f:
                        return f.read()
                except UnicodeDecodeError:
                    continue
            # Если ни одна кодировка не подошла, читаем как бинарный
            with open(file_path, 'rb') as f:
                return f.read().decode('utf-8', errors='ignore')
        except Exception as e:
            print(f"Ошибка чтения TXT: {e}")
            return ""

    @staticmethod
    def parse_pdf(file_path):
        """Извлечение текста из PDF"""
        text = ""
        try:
            reader = PdfReader(file_path)
            # Ограничим количество страниц для больших файлов
            max_pages = min(50, len(reader.pages))
            for i in range(max_pages):
                page = reader.pages[i]
                text += page.extract_text() or ""
        except Exception as e:
            print(f"Ошибка чтения PDF: {e}")
        return text

    @staticmethod
    def parse_docx(file_path):
        """Чтение документов Word"""
        try:
            doc = Document(file_path)
            full_text = []
            for para in doc.paragraphs:
                full_text.append(para.text)
            return '\n'.join(full_text)
        except Exception as e:
            print(f"Ошибка чтения DOCX: {e}")
            return ""

    @staticmethod
    def parse_excel(file_path):
        """Обработка Excel файлов"""
        try:
            # Читаем все листы
            excel_file = pd.ExcelFile(file_path)
            all_sheets_text = []
            
            for sheet_name in excel_file.sheet_names:
                df = pd.read_excel(file_path, sheet_name=sheet_name)
                sheet_text = f"--- Лист: {sheet_name} ---\n{df.to_string()}\n"
                all_sheets_text.append(sheet_text)
                
            return '\n'.join(all_sheets_text)
        except Exception as e:
            print(f"Ошибка чтения Excel: {e}")
            return ""

    @classmethod
    def parse_file(cls, file_path):
        """Автоматическое определение типа файла и его обработка"""
        if not os.path.exists(file_path):
            return ""
            
        # Проверяем расширение файла
        ext = os.path.splitext(file_path)[1].lower()
        
        if ext == '.txt':
            return cls.parse_text(file_path)
        elif ext == '.pdf':
            return cls.parse_pdf(file_path)
        elif ext == '.docx':
            return cls.parse_docx(file_path)
        elif ext in ('.xlsx', '.xls'):
            return cls.parse_excel(file_path)
        else:
            print(f"Неподдерживаемый формат: {ext}")
            return ""

    @staticmethod
    def find_with_context(text, query, context_size=100):
        """Найти запрос в тексте и вернуть контекст"""
        try:
            text_lower = text.lower()
            query_lower = query.lower()
            
            # Находим все вхождения запроса
            positions = []
            start = 0
            while True:
                pos = text_lower.find(query_lower, start)
                if pos == -1:
                    break
                positions.append(pos)
                start = pos + 1
            
            if not positions:
                return "Совпадение не найдено"
            
            # Берем первое вхождение и его контекст
            first_pos = positions[0]
            
            # Вычисляем границы контекста
            start_context = max(0, first_pos - context_size)
            end_context = min(len(text), first_pos + len(query) + context_size)
            
            # Извлекаем контекст
            context = text[start_context:end_context]
            
            # Добавляем указатель на найденный текст
            query_start_in_context = first_pos - start_context
            query_end_in_context = query_start_in_context + len(query)
            
            # Форматируем вывод с подсветкой
            before_match = context[:query_start_in_context]
            match_text = context[query_start_in_context:query_end_in_context]
            after_match = context[query_end_in_context:]
            
            # Если контекст обрезан в начале, добавляем "..."
            if start_context > 0:
                before_match = "..." + before_match
            
            # Если контекст обрезан в конце, добавляем "..."
            if end_context < len(text):
                after_match = after_match + "..."
            
            formatted_context = f"{before_match}>>> {match_text.upper()} <<<{after_match}"
            
            return formatted_context.strip()
            
        except Exception as e:
            print(f"Ошибка поиска контекста: {e}")
            return "Ошибка при извлечении контекста"
    
    @staticmethod
    def find_all_matches(text, query, max_matches=3, context_size=80):
        """Найти все вхождения запроса с контекстом"""
        try:
            text_lower = text.lower()
            query_lower = query.lower()
            
            matches = []
            start = 0
            match_count = 0
            
            while match_count < max_matches:
                pos = text_lower.find(query_lower, start)
                if pos == -1:
                    break
                
                # Вычисляем границы контекста
                start_context = max(0, pos - context_size)
                end_context = min(len(text), pos + len(query) + context_size)
                
                # Извлекаем контекст
                context = text[start_context:end_context]
                
                # Добавляем указатель на найденный текст
                query_start_in_context = pos - start_context
                query_end_in_context = query_start_in_context + len(query)
                
                # Форматируем вывод
                before_match = context[:query_start_in_context]
                match_text = context[query_start_in_context:query_end_in_context]
                after_match = context[query_end_in_context:]
                
                # Добавляем многоточия если обрезано
                if start_context > 0:
                    before_match = "..." + before_match
                if end_context < len(text):
                    after_match = after_match + "..."
                
                formatted_match = f"{before_match}>>> {match_text.upper()} <<<{after_match}"
                matches.append(formatted_match.strip())
                
                match_count += 1
                start = pos + 1
            
            return matches
            
        except Exception as e:
            print(f"Ошибка поиска всех совпадений: {e}")
            return ["Ошибка при поиске совпадений"]