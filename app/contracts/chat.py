from .base import BaseContract, TimestampedContract
from uuid import UUID
from typing import Optional, List
from .document import DocumentResponse

class ChatMessageBase(BaseContract):
    content: str

class ChatMessageCreate(ChatMessageBase):
    session_id: UUID

class ChatMessageResponse(ChatMessageBase, TimestampedContract):
    id: UUID
    session_id: UUID

class ChatSessionBase(BaseContract):
    title: str
    user_id: UUID

class ChatSessionCreate(ChatSessionBase):
    pass

class ChatSessionUpdate(BaseContract):
    title: Optional[str] = None

class ChatSessionResponse(ChatSessionBase, TimestampedContract):
    id: UUID
    messages: List[ChatMessageResponse]
    documents: List[DocumentResponse] 