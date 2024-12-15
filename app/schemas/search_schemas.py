from datetime import datetime
from typing import Optional
from pydantic import BaseModel
from app.models.user_model import UserRole

class UserSearchParams(BaseModel):
    search_term: Optional[str] = None
    role: Optional[UserRole] = None
    is_locked: Optional[bool] = None
    is_verified: Optional[bool] = None
    registration_start: Optional[datetime] = None
    registration_end: Optional[datetime] = None 