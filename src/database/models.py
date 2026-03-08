import uuid
from datetime import datetime, timezone
from sqlalchemy import String, Text, DateTime, Float, ForeignKey
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship

class Base(DeclarativeBase):
    pass

class ArticleRecord(Base):
    __tablename__ = "article_records"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    source_uri: Mapped[str] = mapped_column(String(255), unique=True, index=True)
    headline: Mapped[str] = mapped_column(String(500))
    content_body: Mapped[str] = mapped_column(Text)
    published_at: Mapped[datetime] = mapped_column(DateTime(timezone=True))
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))

    sentiment_analysis: Mapped["SentimentResultRecord"] = relationship(
        back_populates="article", 
        cascade="all, delete-orphan"
    )

class SentimentResultRecord(Base):
    __tablename__ = "sentiment_results"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    article_id: Mapped[str] = mapped_column(ForeignKey("article_records.id", ondelete="CASCADE"), unique=True, index=True)
    primary_sentiment: Mapped[str] = mapped_column(String(50))
    confidence_score: Mapped[float] = mapped_column(Float)
    analyzed_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))

    article: Mapped["ArticleRecord"] = relationship(back_populates="sentiment_analysis")