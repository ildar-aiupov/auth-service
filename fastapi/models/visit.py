from datetime import datetime

from sqlalchemy import Column, DateTime, String, Integer
from sqlalchemy.dialects.postgresql import UUID

from db.postgres import Base
from core.config import settings


class Visit(Base):
    __tablename__ = settings.visits_tablename

    id = Column(Integer, primary_key=True, unique=True, nullable=False)
    user_id = Column(UUID(as_uuid=True))
    action = Column(String(100))
    user_agent = Column(String(500))
    created_at = Column(DateTime, default=datetime.utcnow)

    def __init__(self, user_id: str, action: str, user_agent: str):
        self.user_id = user_id
        self.action = action
        self.user_agent = user_agent

    def __repr__(self) -> str:
        return f"<Visit {self.user_id} / {self.action} / {self.user_agent} / {self.created_at}>"
