from pydantic import BaseModel, ConfigDict
from datetime import datetime
from typing import Optional

class BaseContract(BaseModel):
    model_config = ConfigDict(from_attributes=True)

class TimestampedContract(BaseContract):
    created_at: datetime
    updated_at: Optional[datetime] = None 