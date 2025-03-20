from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from .routes import api

app = FastAPI(title="RAG API with Hybrid Search")

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(api.router, prefix="/api/v1")