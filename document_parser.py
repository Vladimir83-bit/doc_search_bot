from PyPDF2 import PdfReader
from docx import Document
import pandas as pd
import magic
import os

class DocumentParser:
    """Класс для извлечения текста из разных форматов документов"""
    
    @staticmethod
    def parse_text(file_path):
        """Чтение обычных текстовых файлов (.txt)"""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                return f.read()
        except Exception as e:
            print(f"Ошибка чтения TXT: {e}")
            return ""

    @staticmethod
    def parse_pdf(file_path):
        """Извлечение текста из PDF"""
        text = ""
        try:
            reader = PdfReader(file_path)
            for page in reader.pages:
                text += page.extract_text() or ""
        except Exception as e:
            print(f"Ошибка чтения PDF: {e}")
        return text

    @staticmethod
    def parse_docx(file_path):
        """Чтение документов Word"""
        try:
            doc = Document(file_path)
            return '\n'.join([para.text for para in doc.paragraphs])
        except Exception as e:
            print(f"Ошибка чтения DOCX: {e}")
            return ""

    @staticmethod
    def parse_excel(file_path):
        """Обработка Excel файлов"""
        try:
            df = pd.read_excel(file_path)
            return df.to_string()
        except Exception as e:
            print(f"Ошибка чтения Excel: {e}")
            return ""

    @classmethod
    def parse_file(cls, file_path):
        """Автоматическое определение типа файла и его обработка"""
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