import logging
from src.database.session import SessionLocal
from src.database.repository import fetch_unprocessed_articles, insert_sentiment_record
from src.services.sentiment_analyzer import SentimentInferenceEngine

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def run_sentiment_batch() -> None:
    inference_engine = SentimentInferenceEngine()
    
    with SessionLocal() as active_transaction:
        pending_articles = fetch_unprocessed_articles(db_session=active_transaction, batch_limit=20)
        
        if not pending_articles:
            logger.info("No unprocessed articles found in the database.")
            return

        logger.info(f"Initiating processing for {len(pending_articles)} articles.")
        
        successful_inferences = 0
        
        for article in pending_articles:
            try:
                # We use content_body if available, otherwise fallback to headline
                payload_text = article.content_body if article.content_body else article.headline
                
                inference_output = inference_engine.process_text(text_payload=payload_text)
                
                insert_sentiment_record(
                    db_session=active_transaction,
                    target_article_id=article.id,
                    label=str(inference_output["sentiment_label"]),
                    score=float(inference_output["confidence_score"])
                )
                successful_inferences += 1
                
            except Exception as processing_fault:
                logger.error(f"Skipping article {article.id} due to processing fault: {processing_fault}")
                continue
                
        logger.info(f"Successfully processed and stored {successful_inferences} sentiments.")

if __name__ == "__main__":
    run_sentiment_batch()