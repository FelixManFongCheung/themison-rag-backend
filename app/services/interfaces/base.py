from typing import Generic, TypeVar, List, Protocol
from uuid import UUID
from app.contracts.base import BaseContract

CreateContractType = TypeVar("CreateContractType", bound=BaseContract)
UpdateContractType = TypeVar("UpdateContractType", bound=BaseContract)
ResponseContractType = TypeVar("ResponseContractType", bound=BaseContract)

class IBaseService(Generic[CreateContractType, UpdateContractType, ResponseContractType]):
    async def create(self, contract: CreateContractType) -> ResponseContractType:
        pass
    
    async def get(self, id: UUID) -> ResponseContractType:
        pass
    
    async def update(self, id: UUID, contract: UpdateContractType) -> ResponseContractType:
        pass
    
    async def delete(self, id: UUID) -> None:
        pass
    
    async def list(self) -> List[ResponseContractType]:
        pass 