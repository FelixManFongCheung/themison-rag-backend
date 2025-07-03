from fastapi import FastAPI, Depends
from app.api.routes import *
from app.dependencies.auth import auth
from app.core.embeddings import SentenceTransformerProvider
from fastapi.middleware.cors import CORSMiddleware
from dotenv import load_dotenv
from contextlib import asynccontextmanager
import os

load_dotenv()

# Application state for storing loaded models
app_state = {}

@asynccontextmanager
async def lifespan(app: FastAPI):
    """Load heavy models at startup"""
    app_state["embedding_provider"] = SentenceTransformerProvider()
    yield
    # Clean up
    app_state.clear()

app = FastAPI(lifespan=lifespan)
app.add_middleware(
    CORSMiddleware,
    allow_origins=[os.getenv("FRONTEND_URL") or "http://localhost:3000"],  # Your frontend URL
    allow_methods=["*"],
    allow_headers=["*"],
    allow_credentials=True,
)

app.include_router(
    auth_router,
    prefix="/auth",
    tags=["auth"]
)

# Protected routes
app.include_router(
    upload_router,
    prefix="/upload",
    tags=["upload"],
    dependencies=[Depends(auth.verify_jwt)]
)

app.include_router(
    query_router,
    prefix="/query",
    tags=["query"],
    dependencies=[Depends(auth.verify_jwt)]
)

app.include_router(
    documents_router,
    prefix="/documents",
    tags=["documents"],
    dependencies=[Depends(auth.verify_jwt)]
)