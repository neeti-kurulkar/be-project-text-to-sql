from pydantic import BaseModel, EmailStr, Field
from typing import Optional


class LoginRequest(BaseModel):
    email: EmailStr
    password: str = Field(..., min_length=6)


class RegisterRequest(BaseModel):
    email: EmailStr
    password: str = Field(..., min_length=6)
    name: str = Field(..., min_length=2)
    role: str = Field(default='analyst', pattern='^(admin|analyst|viewer)$')


class UserResponse(BaseModel):
    id: str
    email: str
    name: str
    role: str
    company: str


class AuthResponse(BaseModel):
    user: UserResponse
    token: str


class TokenPayload(BaseModel):
    sub: str  # user_id
    organization_id: int
    email: str
    role: str
    exp: Optional[int] = None
    iat: Optional[int] = None
