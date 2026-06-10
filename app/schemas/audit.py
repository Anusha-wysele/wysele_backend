from pydantic import BaseModel, ConfigDict
from typing import Optional, Any
from datetime import datetime

class AuditResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    user_id: Optional[int] = None
    email: Optional[str] = None
    action: str
    details: Optional[Any] = None
    ip_address: Optional[str] = None
    created_at: datetime
