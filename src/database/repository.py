import logging
from sqlalchemy.orm import Session
from sqlalchemy import select
from src.database.models import ArticleRecord, SentimentResultRecord

logger = logging.getLogger(__name__)

def fetch_unprocessed_articles(db_session: Session, batch_limit: int = 50) -> list[ArticleRecord]:
    try:
        # LEFT OUTER JOIN ensures we only retrieve articles where the sentiment ID is null
        query = (
            select(ArticleRecord)
            .outerjoin(SentimentResultRecord)
            .where(SentimentResultRecord.id.is_(None))
            .limit(batch_limit)
        )
        return list(db_session.scalars(query).all())
    except Exception as query_failure:
        logger.error(f"Failed to fetch unprocessed articles: {query_failure}")
        raise RuntimeError("Database query execution failed.") from query_failure
    
def insert_sentiment_record(db_session: Session, target_article_id: str, label: str, score: float) -> None:
    try:
        new_sentiment = SentimentResultRecord(
            article_id=target_article_id,
            primary_sentiment=label,
            confidence_score=score
        )
        db_session.add(new_sentiment)
        db_session.commit()
    except Exception as insert_failure:
        db_session.rollback()
        logger.error(f"Failed to persist sentiment for article {target_article_id}: {insert_failure}")
        raise ValueError("Database insertion failed due to integrity or connection error.") from insert_failure