from datetime import datetime
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column
from typing import Optional


class Base(DeclarativeBase):
    pass


class ClientRecord(Base):
    __tablename__ = "clients"
    id: Mapped[int] = mapped_column(primary_key=True)
    username: Mapped[Optional[str]] = mapped_column(unique=True)
    email: Mapped[Optional[str]] = mapped_column(unique=True)
    password: Mapped[bytes] = mapped_column()  # stores bcrypt hash


class RevokedToken(Base):
    __tablename__ = "revoked_tokens"
    id: Mapped[int] = mapped_column(primary_key=True)
    token: Mapped[str] = mapped_column(unique=True)
    created_at: Mapped[datetime] = mapped_column(default=datetime.utcnow)
