from pydantic import BaseModel, Field
from datetime import datetime

class SentimentData(BaseModel):
    primary_sentiment: str
    confidence_score: float = Field(..., ge=0.0, le=1.0)

class ArticleSentimentResponse(BaseModel):
    article_id: str
    headline: str
    source_uri: str
    published_at: datetime
    sentiment: SentimentData | None

    class Config:
        from_attributes = True