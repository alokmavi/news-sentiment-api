import json
import logging
from pathlib import Path
from sqlalchemy import select
from src.database.session import SessionLocal
from src.database.models import ArticleRecord, SentimentResultRecord

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def export_daily_metrics(output_path: str = "latest_sentiment.json") -> None:
    try:
        with SessionLocal() as db:
            query = (
                select(ArticleRecord)
                .join(SentimentResultRecord)
                .order_by(ArticleRecord.published_at.desc())
                .limit(50)
            )
            records = db.scalars(query).all()

            payload = [
                {
                    "source_uri": article.source_uri,
                    "headline": article.headline,
                    "primary_sentiment": article.sentiment_analysis.primary_sentiment,
                    "confidence_score": round(article.sentiment_analysis.confidence_score, 4),
                    "published_at": article.published_at.isoformat()
                }
                for article in records
            ]

        out_file = Path(output_path)
        out_file.write_text(json.dumps(payload, indent=2))
        logger.info(f"Successfully exported {len(payload)} records to {output_path}")

    except Exception as export_error:
        logger.critical(f"Failed to export metrics: {export_error}")
        raise RuntimeError("Metrics export aborted.") from export_error

if __name__ == "__main__":
    export_daily_metrics()