from fastapi import FastAPI
# from app.api.routes import items

def create_application() -> FastAPI:
    application = FastAPI()

    # Include only the items router
    # application.include_router(items.router, prefix=settings.API_V1_STR)

    @application.get("/")
    async def root():
        return {"message": "Welcome to the API"}

    return application

app = create_application()

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("app.main:app", host="0.0.0.0", port=8000, reload=True)