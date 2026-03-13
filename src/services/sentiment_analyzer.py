import logging
from transformers import pipeline

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class SentimentInferenceEngine:
    def __init__(self, target_model: str = "distilbert/distilbert-base-uncased-finetuned-sst-2-english"):
        self._target_model = target_model
        self._active_pipeline = None

    def _initialize_pipeline(self) -> None:
        """Lazy loads the model into memory only when first required."""
        if self._active_pipeline is None:
            try:
                logger.info(f"Initializing transformer pipeline using model: {self._target_model}")
                self._active_pipeline = pipeline("sentiment-analysis", model=self._target_model)
            except Exception as initialization_failure:
                logger.error(f"Failed to mount inference pipeline: {initialization_failure}")
                raise RuntimeError("ML pipeline boot failure.") from initialization_failure

    def process_text(self, text_payload: str) -> dict[str, float | str]:
        """Executes inference on the provided text, returning label and confidence."""
        self._initialize_pipeline()
        
        try:
            # The pipeline returns a list of dictionaries, we grab the first result
            inference_result = self._active_pipeline(text_payload, truncation=True, max_length=512)[0]
            
            return {
                "sentiment_label": inference_result["label"],
                "confidence_score": inference_result["score"]
            }
            
        except Exception as inference_error:
            logger.error(f"Inference processing failed: {inference_error}")
            # We raise a specific ValueError so the caller knows the payload was problematic
            raise ValueError("Failed to process sentiment for provided payload.") from inference_error