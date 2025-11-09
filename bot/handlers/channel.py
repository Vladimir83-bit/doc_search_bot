from aiogram import Bot, types
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from bot.core.loader import dp, bot
from bot.utils.logger import logger

class ChannelStates(StatesGroup):
    waiting_for_post = State()
    waiting_for_schedule = State()

# Для публикации в канал
@dp.message(Command("post"))
async def create_post(message: types.Message, state: FSMContext):
    """Создание поста для канала"""
    if not await is_channel_admin(message.from_user.id):
        await message.answer("❌ У вас нет прав для публикации в канал")
        return
    
    await message.answer(
        "📝 **Создание поста для канала**\n\n"
        "Отправьте сообщение которое хотите опубликовать:\n"
        "(текст, фото, документ - что угодно)"
    )
    await state.set_state(ChannelStates.waiting_for_post)

@dp.message(ChannelStates.waiting_for_post)
async def process_post(message: types.Message, state: FSMContext):
    """Обработка поста для канала"""
    try:
        channel_id = "@your_channel_username"  # Замени на username твоего канала
        
        # Копируем сообщение в канал
        await message.copy_to(channel_id)
        await message.answer("✅ Пост успешно опубликован в канале!")
        
    except Exception as e:
        logger.error(f"Channel post error: {e}")
        await message.answer("❌ Ошибка при публикации в канал")
    
    await state.clear()

async def is_channel_admin(user_id: int) -> bool:
    """Проверка прав администратора канала"""
    # Здесь должна быть логика проверки прав
    # Пока заглушка - вернем True для тестирования
    return True

# Автоматическая публикация (пример)
async def scheduled_posts():
    """Запланированные публикации"""
    try:
        channel_id = "@your_channel_username"
        
        # Пример автоматической публикации
        post_text = "📚 **Новые возможности бота!**\n\nТеперь бот умеет администрировать группы и публиковать посты в каналах! 🚀"
        
        await bot.send_message(channel_id, post_text)
        logger.info("Scheduled post published")
        
    except Exception as e:
        logger.error(f"Scheduled post error: {e}")