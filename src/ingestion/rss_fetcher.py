import logging
import feedparser
from datetime import datetime, timezone
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from src.database.session import SessionLocal
from src.database.models import ArticleRecord

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

TARGET_RSS_ENDPOINTS = [
    "http://feeds.bbci.co.uk/news/world/rss.xml",
    "https://rss.nytimes.com/services/xml/rss/nyt/World.xml"
]

def ingest_news_feeds(db_session: Session, feed_urls: list[str]) -> None:
    for target_url in feed_urls:
        try:
            parsed_payload = feedparser.parse(target_url)
            
            # bozo is feedparser's flag for malformed XML
            if parsed_payload.bozo:
                logger.error(f"Malformed XML payload from {target_url}: {parsed_payload.bozo_exception}")
                continue

            successful_inserts = 0
            
            for article_entry in parsed_payload.entries:
                entry_uri = getattr(article_entry, 'link', None)
                entry_headline = getattr(article_entry, 'title', "Untitled")
                entry_summary = getattr(article_entry, 'summary', "No content available.")
                
                if not entry_uri:
                    continue
                    
                new_article_record = ArticleRecord(
                    source_uri=entry_uri,
                    headline=entry_headline,
                    content_body=entry_summary,
                    published_at=datetime.now(timezone.utc)
                )
                
                db_session.add(new_article_record)
                
                # We commit per article to isolate IntegrityErrors (duplicate unique URIs)
                try:
                    db_session.commit()
                    successful_inserts += 1
                except IntegrityError:
                    db_session.rollback()

            logger.info(f"Ingested {successful_inserts} new articles from {target_url}")

        except Exception as network_or_parsing_error:
            logger.critical(f"Critical failure processing {target_url}: {network_or_parsing_error}")

if __name__ == "__main__":
    with SessionLocal() as active_transaction:
        ingest_news_feeds(db_session=active_transaction, feed_urls=TARGET_RSS_ENDPOINTS)