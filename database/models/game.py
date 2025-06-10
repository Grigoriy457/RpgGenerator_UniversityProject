import datetime
from typing import Optional, List, TYPE_CHECKING
import base64

from sqlalchemy import Column, DateTime, func, LargeBinary, Integer, String, Text, Boolean, JSON, Enum, ForeignKey
from sqlalchemy.ext.hybrid import hybrid_property
from sqlalchemy.orm import Mapped, relationship

import config
from database.models.base import Base
from database.models.enums import GameGenre
if TYPE_CHECKING:
    from database.models.auth import User


class Character(Base):
    __tablename__ = "character"

    created_at: Mapped[datetime.datetime] = Column(DateTime, server_default=func.now())
    id: Mapped[int] = Column(Integer, primary_key=True)
    name: Mapped[str] = Column(String(100), nullable=False)
    avatar = Column(LargeBinary)
    description: Mapped[str] = Column(Text)
    
    game_id = Column(Integer, ForeignKey("game.id"), nullable=False)

    @hybrid_property
    def avatar_base64(self):
        return None if self.avatar is None else base64.b64encode(self.avatar).decode('utf-8')


class Rule(Base):
    __tablename__ = "rule"

    id: Mapped[int] = Column(Integer, primary_key=True)
    name: Mapped[str] = Column(String(100), nullable=False)
    description: Mapped[str] = Column(Text)
    position: Mapped[int] = Column(Integer, nullable=False, default=0)

    game_id: Mapped[int] = Column(Integer, ForeignKey("game.id", ondelete="CASCADE"), nullable=False)


class Game(Base):
    __tablename__ = "game"

    created_at: Mapped[datetime.datetime] = Column(DateTime, server_default=func.now())
    id: Mapped[int] = Column(Integer, primary_key=True)
    image: Mapped[Optional[bytes]] = Column(LargeBinary, nullable=True)
    title: Mapped[str] = Column(String(100), nullable=False)
    description: Mapped[str] = Column(Text)
    genre: Mapped[GameGenre] = Column(Enum(GameGenre))
    views: Mapped[int] = Column(Integer, nullable=False, default=0)
    copied: Mapped[int] = Column(Integer, nullable=False, default=0)
    is_public: Mapped[bool] = Column(Boolean, default=True)

    owner_id: Mapped[int] = Column(Integer, ForeignKey("user.id"), nullable=False)

    owner: Mapped["User"] = relationship("User")
    rules: Mapped[List["Rule"]] = relationship("Rule", cascade="all, delete")
    characters: Mapped[List["Character"]] = relationship("Character")

    @hybrid_property
    def image_base64(self):
        return None if self.image is None else base64.b64encode(self.image).decode('utf-8')
