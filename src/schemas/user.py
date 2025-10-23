# src/schemas/user.py
from typing import Optional
from pydantic import BaseModel, EmailStr
from uuid import UUID

class UserBase(BaseModel):
    email: EmailStr
    full_name: Optional[str] = None
    phone: Optional[str] = None
    is_verified: bool = False
    can_sell: bool = False

class UserCreate(UserBase):
    # Por simplicidad inicial, aceptamos password_hash directo.
    # Mas adelante cambiaremos a hashing seguro / Auth0.
    password_hash: Optional[str] = None
    auth0_user_id: Optional[str] = None

class UserUpdate(BaseModel):
    email: Optional[EmailStr] = None
    full_name: Optional[str] = None
    phone: Optional[str] = None
    is_verified: Optional[bool] = None
    can_sell: Optional[bool] = None
    password_hash: Optional[str] = None
    auth0_user_id: Optional[str] = None

class UserOut(UserBase):
    id: int
    external_id: UUID

    class Config:
        from_attributes = True