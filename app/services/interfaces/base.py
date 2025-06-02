from abc import ABC, abstractmethod
from typing import Generic, TypeVar, List
from uuid import UUID
from app.schemas.base import BaseSchema

CreateSchemaType = TypeVar("CreateSchemaType", bound=BaseSchema)
UpdateSchemaType = TypeVar("UpdateSchemaType", bound=BaseSchema)
ResponseSchemaType = TypeVar("ResponseSchemaType", bound=BaseSchema)

class IBaseService(ABC, Generic[CreateSchemaType, UpdateSchemaType, ResponseSchemaType]):
    @abstractmethod
    async def create(self, schema: CreateSchemaType) -> ResponseSchemaType:
        pass
    
    @abstractmethod
    async def get(self, id: UUID) -> ResponseSchemaType:
        pass
    
    @abstractmethod
    async def update(self, id: UUID, schema: UpdateSchemaType) -> ResponseSchemaType:
        pass
    
    @abstractmethod
    async def delete(self, id: UUID) -> None:
        pass
    
    @abstractmethod
    async def list(self) -> List[ResponseSchemaType]:
        pass 