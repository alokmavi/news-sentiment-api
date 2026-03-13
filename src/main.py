from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from src.api.routes import sentiment_router

def create_application() -> FastAPI:
    application = FastAPI(
        title="News Sentiment Aggregator API",
        description="Automated pipeline for ingesting and analyzing news sentiment.",
        version="1.0.0"
    )

    # Standard permissive CORS for local development
    application.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    application.include_router(sentiment_router)
    
    return application

app = create_application()

@app.get("/health", tags=["System"])
def health_check():
    return {"status": "operational"}