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