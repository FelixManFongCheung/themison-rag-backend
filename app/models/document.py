from sqlalchemy import Column, Text, JSONB
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()

class Document(Base):
    __tablename__ = 'documents'
    
    id = Column(UUID, primary_key=True)
    content = Column(Text)
    metadata = Column(JSONB)
