#!/bin/bash
# start.sh

# Optional: Run a quick warmup to ensure model is loaded
python -c "from app.embedding_service import get_embedding_model; get_embedding_model()"

# Start the FastAPI application
exec uvicorn app.main:app --host 0.0.0.0 --port $PORT