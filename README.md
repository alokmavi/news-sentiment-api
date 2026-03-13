# Automated News Sentiment API

[![Daily Sentiment Pipeline](https://github.com/alokmavi/news-sentiment-api/actions/workflows/daily_pipeline.yml/badge.svg)](https://github.com/alokmavi/news-sentiment-api/actions/workflows/daily_pipeline.yml)

A backend data pipeline that ingests daily news from RSS feeds, evaluates article sentiment using a local NLP model, and exposes the aggregated data through a REST API. 

I built this project to practice modular backend architecture, database migrations, and integrating machine learning inference into a standard web service.

## Architecture

The system is decoupled into three primary modules:
1. **Ingestion Layer:** Parses XML feeds (BBC, NYT) and safely loads raw text into a PostgreSQL database, ignoring duplicates.
2. **Inference Engine:** A batch processor that lazy-loads a HuggingFace transformer (`distilbert-base-uncased-finetuned-sst-2-english`), analyzes unprocessed articles, and stores confidence scores.
3. **Serving Layer:** A FastAPI application providing read-only endpoints to query the analyzed data.

An automated GitHub Action runs the ingestion and inference modules daily at midnight UTC, exporting a static JSON snapshot of the latest database state.

## Tech Stack

* **Core:** Python 3.12, FastAPI, Uvicorn
* **Database:** PostgreSQL, SQLAlchemy 2.0 (ORM), Alembic (Migrations)
* **Machine Learning:** PyTorch, HuggingFace `transformers`
* **Infrastructure:** Docker Compose, GitHub Actions

## Local Development Setup

**1. Clone and configure the environment**
```sh
git clone https://github.com/alokmavi/news-sentiment-api.git
cd news-sentiment-api
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

**2. Initialize the database**
Requires Docker to spin up the local PostgreSQL instance.
```sh
docker compose up -d
alembic upgrade head
```

**3. Run the pipeline locally**
Pull the latest articles and run the ML batch processor.
```sh
python -m src.ingestion.rss_fetcher
python -m src.services.batch_processor
```

**4. Start the API server**
```sh
uvicorn src.main:app --reload
```
The API documentation will be available at `http://127.0.0.1:8000/docs`.

## API Usage Example

**GET** `/v1/news/latest?limit=5`

```json
[
  {
    "article_id": "550e8400-e29b-41d4-a716-446655440000",
    "headline": "Global Markets Rally Amid Tech Sector Growth",
    "source_uri": "https://example.com/news/123",
    "published_at": "2026-03-14T00:00:00Z",
    "sentiment": {
      "primary_sentiment": "POSITIVE",
      "confidence_score": 0.985
    }
  }
]
```