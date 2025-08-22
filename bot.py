import os
import telebot
from telebot import types
from config import Config
from file_storage import FileStorage
from document_parser import DocumentParser


bot = telebot.TeleBot(Config.TOKEN)

def create_main_keyboard():
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    markup.add(types.KeyboardButton("🔍 Поиск в документах"))
    markup.add(types.KeyboardButton("📁 Список документов"))
    markup.add(types.KeyboardButton("❌ Удалить все документы"))
    return markup

@bot.message_handler(commands=['start', 'help'])
def send_welcome(message):
    
    welcome_text = (
        "📚 Бот для поиска в документах\n\n"
        "Отправьте мне документы в форматах:\n"
        "- TXT (текст)\n"
        "- PDF\n"
        "- DOCX (Word)\n"
        "- XLSX (Excel)\n\n"
        "После загрузки используйте кнопки ниже для поиска."
    )
    
    bot.send_message(message.chat.id, welcome_text, 
                    reply_markup=create_main_keyboard())

@bot.message_handler(content_types=['document'])
def handle_document(message):
    
    try:
    
        if message.document.file_size > Config.MAX_FILE_SIZE:
            bot.reply_to(message, 
                        f"⚠ Файл слишком большой. Максимум: {Config.MAX_FILE_SIZE//1024//1024}MB")
            return
            
        
        file_name = message.document.file_name
        file_ext = os.path.splitext(file_name)[1].lower()
        
        if file_ext not in Config.ALLOWED_EXTENSIONS:
            bot.reply_to(message, 
                        f"⚠ Неподдерживаемый формат. Разрешенные: {', '.join(Config.ALLOWED_EXTENSIONS)}")
            return
            
        
        file_info = bot.get_file(message.document.file_id)
        file_data = bot.download_file(file_info.file_path)
        
        
        saved_path = FileStorage.save_file(message.document.file_id, file_name, file_data)
        
        if saved_path:
            bot.reply_to(message, f"✅ Документ '{file_name}' успешно загружен!")
        else:
            bot.reply_to(message, "❌ Ошибка при сохранении файла")
            
    except Exception as e:
        bot.reply_to(message, f"❌ Произошла ошибка: {str(e)}")

@bot.message_handler(func=lambda m: m.text == "📁 Список документов")
def list_documents(message):
    """Показ списка всех загруженных документов"""
    docs = FileStorage.get_all_docs()
    
    if docs:
        response = "📂 Загруженные документы:\n\n" + "\n".join(f"▫ {doc}" for doc in docs)
    else:
        response = "📭 Нет загруженных документов"
        
    bot.send_message(message.chat.id, response, 
                    reply_markup=create_main_keyboard())

@bot.message_handler(func=lambda m: m.text == "❌ Удалить все документы")
def clear_documents(message):
    """Удаление всех документов"""
    if FileStorage.clear_all_docs():
        bot.send_message(message.chat.id, "✅ Все документы удалены",
                        reply_markup=create_main_keyboard())
    else:
        bot.send_message(message.chat.id, "❌ Ошибка при удалении документов")

@bot.message_handler(func=lambda m: m.text == "🔍 Поиск в документах")
def handle_search(message):
    """Запуск процесса поиска"""
    msg = bot.send_message(message.chat.id, "🔍 Введите текст для поиска:")
    bot.register_next_step_handler(msg, process_search_query)

def process_search_query(message):
    """Обработка поискового запроса"""
    search_text = message.text.lower()
    found_in = []
    
    
    for doc in FileStorage.get_all_docs():
        file_path = os.path.join(Config.DOCS_FOLDER, doc)
        content = DocumentParser.parse_file(file_path).lower()
        
        if search_text in content:
            found_in.append(doc)
    
    
    if found_in:
        response = "🔍 Найдено в документах:\n\n" + "\n".join(f"📌 {doc}" for doc in found_in)
    else:
        response = "😞 Ничего не найдено"
    
    bot.send_message(message.chat.id, response,
                    reply_markup=create_main_keyboard())

if __name__ == '__main__':
    print("🟢 Бот запущен...")
    bot.infinity_polling()