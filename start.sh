#!/bin/bash
# start.sh

# Start the FastAPI application
exec uvicorn app.main:app --host 0.0.0.0 --port $PORT