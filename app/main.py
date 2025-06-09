from fastapi import FastAPI, Depends
from app.api.routes import *
from app.services.utils.indexing.embeddings import get_embedding_model
from contextlib import asynccontextmanager
from fastapi.middleware.cors import CORSMiddleware
from dotenv import load_dotenv
import os

load_dotenv()

ml_models = {}

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Load model in a background thread to avoid blocking startup
    ml_models["embedding_model"] = get_embedding_model()
    yield
    # Clean up the ML models and release the resources
    ml_models.clear()
    
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
    prefix="/documents",
    tags=["documents"],
    dependencies=[Depends(auth.verify_jwt)]
)

app.include_router(
    query_router,
    prefix="/query",
    tags=["query"],
    dependencies=[Depends(auth.verify_jwt)]
)