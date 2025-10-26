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