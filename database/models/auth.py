import datetime
from typing import Optional, TYPE_CHECKING

import jwt
from sqlalchemy import Column, DateTime, func, BIGINT, Integer, String, Boolean, ForeignKey
from sqlalchemy.ext.hybrid import hybrid_property
from sqlalchemy.orm import Mapped, relationship

import config
from database.models.base import Base


class User(Base):
    __tablename__ = "user"
    
    created_at: Mapped[datetime.datetime] = Column(DateTime, nullable=False, server_default=func.now())
    id: Mapped[int] = Column(Integer, primary_key=True, autoincrement=True)
    username: Mapped[str] = Column(String(100), nullable=False)
    email: Mapped[str] = Column(String(255), nullable=False, unique=True)
    password: Mapped[str] = Column(String(255), nullable=False)
    is_admin: Mapped[bool] = Column(Boolean, nullable=False, default=False)
    
