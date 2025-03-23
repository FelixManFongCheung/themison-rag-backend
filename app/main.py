from fastapi import FastAPI
from app.api.routes import documents, query
from app.encoding import get_embedding_model
import threading

app = FastAPI()

# Include only the items router
app.include_router(documents.router, prefix="/documents")
app.include_router(query.router, prefix="/query")


# Use lifespan context manager instead of deprecated on_event
@app.lifespan
async def lifespan(app: FastAPI):
    # Load model in a background thread to avoid blocking startup
    threading.Thread(target=lambda: get_embedding_model()).start()
     # Store any resources that need cleanup
    app.state.background_tasks = []
    
    yield
    
    # Cleanup
    print("Application shutting down, performing cleanup...")
    
    # 1. Close any open file handles
    if hasattr(app.state, "file_handles"):
        for handle in app.state.file_handles:
            handle.close()
    
    # 2. Release model resources (if applicable)
    if hasattr(app.state, "model") and hasattr(app.state.model, "cleanup"):
        app.state.model.cleanup()
    
    # 3. Wait for background tasks to complete (with timeout)
    import asyncio
    for task in app.state.background_tasks:
        try:
            await asyncio.wait_for(task, timeout=5.0)
        except asyncio.TimeoutError:
            print(f"Task {task} didn't complete in time")
    
    # 4. Remove temporary files
    import shutil
    if os.path.exists("./temp_files"):
        shutil.rmtree("./temp_files")

@app.get("/health")
async def health_check():
    return {"status": "healthy"}