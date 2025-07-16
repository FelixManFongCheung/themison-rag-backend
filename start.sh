#!/bin/bash
# start.sh

PORT=8000
# Start the FastAPI application
exec uvicorn app.main:app --host 0.0.0.0 --port $PORT