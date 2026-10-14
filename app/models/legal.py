from datetime import datetime

from sqlalchemy import Boolean, ForeignKey, Index, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.db import Base
from app.models.base import ts_column, utcnow


class LegalAct(Base):
    __tablename__ = "legal_acts"

    id: Mapped[int] = mapped_column(primary_key=True)
    adilet_code: Mapped[str] = mapped_column(String(60), unique=True, index=True)
    title: Mapped[str] = mapped_column(String(500))
    short_title: Mapped[str | None] = mapped_column(String(120))
    url: Mapped[str] = mapped_column(String(600))
    loaded_at: Mapped[datetime] = ts_column(default=utcnow)

    articles: Mapped[list["LegalArticle"]] = relationship(back_populates="act")


class LegalArticle(Base):
    __tablename__ = "legal_articles"

    id: Mapped[int] = mapped_column(primary_key=True)
    act_id: Mapped[int] = mapped_column(ForeignKey("legal_acts.id"), index=True)
    number: Mapped[str] = mapped_column(String(30), index=True)
    title: Mapped[str | None] = mapped_column(String(700))
    text: Mapped[str] = mapped_column(Text)

    act: Mapped[LegalAct] = relationship(back_populates="articles", lazy="joined")


Index("ix_legal_articles_act_number", LegalArticle.act_id, LegalArticle.number)


class LegalRequest(Base):
    __tablename__ = "legal_requests"

    id: Mapped[int] = mapped_column(primary_key=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"), index=True)
    input_text: Mapped[str] = mapped_column(Text)
    output_text: Mapped[str | None] = mapped_column(Text)
    verified: Mapped[bool] = mapped_column(Boolean, default=False)
    created_at: Mapped[datetime] = ts_column(default=utcnow, index=True)
