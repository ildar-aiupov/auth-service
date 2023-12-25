from sqlalchemy import Column, String, Integer, Boolean
from sqlalchemy.orm import relationship

from db.postgres import Base
from core.config import settings


class Role(Base):
    __tablename__ = settings.roles_tablename

    id = Column(Integer, primary_key=True, unique=True, nullable=False)
    name = Column(String(100), unique=True, nullable=False)
    can_read_limited = Column(Boolean, default=False)
    can_read_all = Column(Boolean, default=False)
    can_subscribe = Column(Boolean, default=False)
    can_manage = Column(Boolean, default=False)

    users = relationship("User", back_populates="role", passive_deletes=True)

    def __init__(
        self,
        name: str,
        can_read_limited: bool | None = None,
        can_read_all: bool | None = None,
        can_subscribe: bool | None = None,
        can_manage: bool | None = None,
    ):
        self.name = name
        self.can_read_limited = can_read_limited
        self.can_read_all = can_read_all
        self.can_subscribe = can_subscribe
        self.can_manage = can_manage

    def __repr__(self) -> str:
        return f"<Role {self.name}>"
