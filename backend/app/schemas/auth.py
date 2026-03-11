from pydantic import BaseModel, EmailStr, Field

from app.schemas.user import UserRead


class RegisterRequest(BaseModel):
    company_name: str = Field(min_length=2, max_length=255)
    company_slug: str | None = Field(default=None, max_length=120)
    email: EmailStr
    password: str = Field(min_length=8, max_length=128)
    first_name: str
    last_name: str


class LoginRequest(BaseModel):
    email: EmailStr
    password: str


class RefreshRequest(BaseModel):
    refresh_token: str


class LogoutRequest(BaseModel):
    refresh_token: str


class TokenPair(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str = 'bearer'


class AuthResponse(BaseModel):
    tokens: TokenPair
    user: UserRead
