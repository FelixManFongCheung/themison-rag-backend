# boilerplate code for the database session

from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker
from app.config import get_settings

settings = get_settings()
engine = create_async_engine(settings.supabase_db_url)
async_session = sessionmaker(engine, class_=AsyncSession, expire_on_commit=False) 