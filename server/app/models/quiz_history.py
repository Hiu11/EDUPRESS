from sqlalchemy import Column, Integer, String, DateTime, Float
from datetime import datetime
from app.db.base import Base

class QuizHistory(Base):
    __tablename__ = "quiz_history"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(String, index=True) # Fake user id for now
    course_id = Column(String, index=True)
    score = Column(Integer)
    total = Column(Integer)
    topic = Column(String)
    max_streak = Column(Integer)
    created_at = Column(DateTime, default=datetime.utcnow)
