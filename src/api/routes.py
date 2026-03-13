import logging
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from sqlalchemy import select

from src.database.session import SessionLocal
from src.database.models import ArticleRecord, SentimentResultRecord
from src.api.schemas import ArticleSentimentResponse

logger = logging.getLogger(__name__)
sentiment_router = APIRouter(prefix="/v1/news", tags=["Sentiment Analysis"])

def get_db_session():
    db_transaction = SessionLocal()
    try:
        yield db_transaction
    finally:
        db_transaction.close()

@sentiment_router.get("/latest", response_model=list[ArticleSentimentResponse])
def fetch_latest_sentiments(limit: int = 10, db: Session = Depends(get_db_session)):
    try:
        query = (
            select(ArticleRecord)
            .join(SentimentResultRecord)
            .order_by(ArticleRecord.published_at.desc())
            .limit(limit)
        )
        
        records = db.scalars(query).all()
        
        # Manually mapping to match the nested Pydantic schema structure
        response_payload = []
        for article in records:
            response_payload.append({
                "article_id": article.id,
                "headline": article.headline,
                "source_uri": article.source_uri,
                "published_at": article.published_at,
                "sentiment": {
                    "primary_sentiment": article.sentiment_analysis[0].primary_sentiment,
                    "confidence_score": article.sentiment_analysis[0].confidence_score
                } if article.sentiment_analysis else None
            })
            
        return response_payload
        
    except Exception as query_error:
        logger.error(f"Failed to fetch latest sentiments: {query_error}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal database error while fetching articles."
        )