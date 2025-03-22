from fastapi import FastAPI
from app.api.routes import documents, query

def create_application() -> FastAPI:
    application = FastAPI()

    # Include only the items router
    application.include_router(documents.router, prefix="/documents")
    application.include_router(query.router, prefix="/query")

    @application.get("/")
    async def root():
        return {"message": "Welcome to the API"}

    return application

app = create_application()

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("app.main:app", host="0.0.0.0", port=8000, reload=True)