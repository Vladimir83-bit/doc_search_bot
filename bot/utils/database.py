from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from models.user import User, Base
from bot.core.config import Config
import datetime

# Создаем движок БД
engine = create_engine(Config.DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def create_tables():
    """Создание таблиц в базе данных"""
    Base.metadata.create_all(bind=engine)

def get_db():
    """Получение сессии базы данных"""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

async def get_user(user_id: int, username: str = None, full_name: str = None):
    """Получить или создать пользователя"""
    with SessionLocal() as session:
        user = session.query(User).filter(User.user_id == str(user_id)).first()
        if not user:
            user = User(
                user_id=str(user_id),
                username=username,
                full_name=full_name
            )
            session.add(user)
            session.commit()
            session.refresh(user)
        return user

async def update_user_activity(user_id: int):
    """Обновить время последней активности"""
    with SessionLocal() as session:
        user = session.query(User).filter(User.user_id == str(user_id)).first()
        if user:
            user.last_activity = datetime.datetime.utcnow()
            session.commit()

async def increment_documents_count(user_id: int):
    """Увеличить счетчик загруженных документов"""
    with SessionLocal() as session:
        user = session.query(User).filter(User.user_id == str(user_id)).first()
        if user:
            user.documents_uploaded += 1
            session.commit()

async def increment_searches_count(user_id: int):
    """Увеличить счетчик поисков"""
    with SessionLocal() as session:
        user = session.query(User).filter(User.user_id == str(user_id)).first()
        if user:
            user.searches_performed += 1
            session.commit()

async def get_user_stats(user_id: int):
    """Получить статистику пользователя"""
    with SessionLocal() as session:
        user = session.query(User).filter(User.user_id == str(user_id)).first()
        if user:
            return {
                'documents_uploaded': user.documents_uploaded,
                'searches_performed': user.searches_performed,
                'created_at': user.created_at,
                'last_activity': user.last_activity
            }
        return None