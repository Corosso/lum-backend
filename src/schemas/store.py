from typing import Optional
from pydantic import BaseModel, Field, validator
from uuid import UUID
from datetime import datetime

class StoreBase(BaseModel):
    name: str = Field(..., min_length=1, max_length=255, description="Nombre de la tienda")
    slug: str = Field(..., min_length=1, max_length=100, description="Slug único de la tienda")
    description: Optional[str] = Field(None, max_length=1000, description="Descripción de la tienda")
    logo_key: Optional[str] = Field(None, description="Clave del logo en el almacenamiento")
    banner_key: Optional[str] = Field(None, description="Clave del banner en el almacenamiento")
    country: str = Field(default="CO", description="País de la tienda")
    city: Optional[str] = Field(None, max_length=100, description="Ciudad de la tienda")
    is_active: bool = Field(default=True, description="Si la tienda está activa")
    plan: str = Field(default="free", description="Plan de la tienda")

    @validator('slug')
    def validate_slug(cls, v):
        # Validar que el slug solo contenga caracteres válidos
        import re
        if not re.match(r'^[a-z0-9-]+$', v):
            raise ValueError('El slug solo puede contener letras minúsculas, números y guiones')
        return v

    @validator('plan')
    def validate_plan(cls, v):
        valid_plans = ['free', 'pro', 'business']
        if v not in valid_plans:
            raise ValueError(f'Plan debe ser uno de: {", ".join(valid_plans)}')
        return v

class StoreCreate(StoreBase):
    owner_user_id: int = Field(..., gt=0, description="ID del usuario propietario")

class StoreUpdate(BaseModel):
    name: Optional[str] = Field(None, min_length=1, max_length=255)
    slug: Optional[str] = Field(None, min_length=1, max_length=100)
    description: Optional[str] = Field(None, max_length=1000)
    logo_key: Optional[str] = None
    banner_key: Optional[str] = None
    country: Optional[str] = None
    city: Optional[str] = Field(None, max_length=100)
    is_active: Optional[bool] = None
    plan: Optional[str] = None

    @validator('slug')
    def validate_slug(cls, v):
        if v is not None:
            import re
            if not re.match(r'^[a-z0-9-]+$', v):
                raise ValueError('El slug solo puede contener letras minúsculas, números y guiones')
        return v

    @validator('plan')
    def validate_plan(cls, v):
        if v is not None:
            valid_plans = ['free', 'pro', 'business']
            if v not in valid_plans:
                raise ValueError(f'Plan debe ser uno de: {", ".join(valid_plans)}')
        return v

class StoreOut(StoreBase):
    id: int
    external_id: UUID
    owner_user_id: int
    created_at: datetime
    updated_at: datetime
    deleted_at: Optional[datetime] = None

    class Config:
        from_attributes = True
