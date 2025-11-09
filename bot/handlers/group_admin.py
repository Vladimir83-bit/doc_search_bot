from aiogram import F, types
from aiogram.filters import Command, CommandObject
from bot.core.loader import dp, bot
from bot.utils.logger import logger
import re

# Мат-фильтр
BLACKLIST_WORDS = ['плохое_слово1', 'плохое_слово2']  # Замени на реальные слова

@dp.message(F.chat.type.in_({"group", "supergroup"}))
async def message_filter(message: types.Message):
    """Фильтр сообщений в группе"""
    if not message.text:
        return
    
    # Проверка на мат
    for word in BLACKLIST_WORDS:
        if word in message.text.lower():
            await message.delete()
            warning = await message.answer(
                f"⚠️ Сообщение от {message.from_user.mention} удалено за нарушение правил!"
            )
            logger.info(f"Deleted message from {message.from_user.id} in group {message.chat.id}")
            # Удаляем предупреждение через 5 секунд
            await asyncio.sleep(5)
            await warning.delete()
            break

# Команды администрирования
@dp.message(Command("warn"))
async def warn_user(message: types.Message, command: CommandObject):
    """Выдать предупреждение пользователю"""
    if not await check_admin_rights(message):
        return
    
    if message.reply_to_message:
        user = message.reply_to_message.from_user
        await message.answer(f"⚠️ Пользователю {user.mention} выдано предупреждение!")
    else:
        await message.answer("❌ Ответьте на сообщение пользователя для выдачи предупреждения")

@dp.message(Command("mute"))
async def mute_user(message: types.Message, command: CommandObject):
    """Замутить пользователя"""
    if not await check_admin_rights(message):
        return
    
    if message.reply_to_message:
        # Логика мута (ограничение на отправку сообщений)
        await message.answer("🔇 Пользователь замьючен на 10 минут")
    else:
        await message.answer("❌ Ответьте на сообщение пользователя")

async def check_admin_rights(message: types.Message) -> bool:
    """Проверка прав администратора"""
    try:
        member = await bot.get_chat_member(message.chat.id, message.from_user.id)
        return member.status in ['administrator', 'creator']
    except Exception as e:
        logger.error(f"Admin check error: {e}")
        return False

# Игры и активности
@dp.message(Command("quiz"))
async def start_quiz(message: types.Message):
    """Начать викторину в группе"""
    quiz_text = (
        "🎯 **Викторина**\n\n"
        "Вопрос: Какой язык программирования мы используем для этого бота?\n\n"
        "Варианты:\n"
        "A) JavaScript\n"
        "B) Python\n" 
        "C) Java\n"
        "D) C++\n\n"
        "Ответьте с буквой правильного ответа!"
    )
    await message.answer(quiz_text)

@dp.message(F.text.in_(["A", "B", "C", "D"]))
async def check_quiz_answer(message: types.Message):
    """Проверка ответа на викторину"""
    if message.text.upper() == "B":
        await message.answer(f"🎉 Правильно! {message.from_user.mention} получает +1 очко!")
    else:
        await message.answer("❌ Неправильно! Попробуйте еще раз.")