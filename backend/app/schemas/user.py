from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, EmailStr

from app.models.enums import UserRole
from app.schemas.common import ORMBase


class UserBase(BaseModel):
    email: EmailStr
    first_name: str
    last_name: str


class UserRead(UserBase, ORMBase):
    id: UUID
    company_id: UUID
    role: UserRole
    is_active: bool
    is_email_verified: bool
    created_at: datetime


class AdminUserCreate(UserBase):
    company_id: UUID
    role: UserRole = UserRole.USER
    password: str
    is_active: bool = True
    is_email_verified: bool = True
