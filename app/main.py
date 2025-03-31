from fastapi import FastAPI
from app.api.routes import query, upload
from app.utils.embeddings import get_embedding_model
from contextlib import asynccontextmanager

ml_models = {}

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Load model in a background thread to avoid blocking startup
    ml_models["embedding_model"] = get_embedding_model()
    yield
    # Clean up the ML models and release the resources
    ml_models.clear()
    
app = FastAPI(lifespan=lifespan)
# Include only the items router
app.include_router(upload.router, prefix="/documents")
app.include_router(query.router, prefix="/query")