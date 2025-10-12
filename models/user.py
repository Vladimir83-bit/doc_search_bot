from sqlalchemy import Column, Integer, String, DateTime, Boolean
from sqlalchemy.ext.declarative import declarative_base
import datetime

Base = declarative_base()

class User(Base):
    __tablename__ = "users"
    
    id = Column(Integer, primary_key=True)
    user_id = Column(String, unique=True, index=True)
    username = Column(String, nullable=True)
    full_name = Column(String)
    created_at = Column(DateTime, default=datetime.datetime.utcnow)
    last_activity = Column(DateTime, default=datetime.datetime.utcnow)
    documents_uploaded = Column(Integer, default=0)
    searches_performed = Column(Integer, default=0)
    
    def __repr__(self):
        return f"<User {self.user_id} - {self.username}>"