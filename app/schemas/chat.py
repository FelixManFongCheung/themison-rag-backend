from .base import BaseSchema, TimestampedSchema
from uuid import UUID
from typing import Optional, List, Dict
from .document import DocumentResponse

class ChatMessageBase(BaseSchema):
    content: str

class ChatMessageCreate(ChatMessageBase):
    session_id: UUID

class ChatMessageResponse(ChatMessageBase, TimestampedSchema):
    id: UUID
    session_id: UUID

class ChatSessionBase(BaseSchema):
    title: str
    user_id: UUID

class ChatSessionCreate(ChatSessionBase):
    pass

class ChatSessionUpdate(BaseSchema):
    title: Optional[str] = None

class ChatSessionResponse(ChatSessionBase, TimestampedSchema):
    id: UUID
    messages: List[ChatMessageResponse]
    documents: List[DocumentResponse] 