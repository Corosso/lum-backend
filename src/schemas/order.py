# src/schemas/order.py
from typing import Optional, List, Dict, Any
from pydantic import BaseModel, Field, validator
from uuid import UUID
from datetime import datetime

# Esquemas base
class OrderBase(BaseModel):
    total_amount_cop: int = Field(..., gt=0, description="Monto total en centavos de peso colombiano")
    currency: str = Field(default="COP", description="Moneda de la orden")
    status: str = Field(default="pending", description="Estado de la orden")
    shipping_address: Optional[Dict[str, Any]] = None
    billing_address: Optional[Dict[str, Any]] = None
    order_metadata: Optional[Dict[str, Any]] = None  # Cambiado de metadataimg a order_metadata

    @validator('status')
    def validate_status(cls, v):
        valid_statuses = ['pending', 'confirmed', 'processing', 'shipped', 'delivered', 'cancelled', 'refunded']
        if v not in valid_statuses:
            raise ValueError(f'Status debe ser uno de: {", ".join(valid_statuses)}')
        return v

class OrderCreate(OrderBase):
    user_id: int = Field(..., gt=0, description="ID del usuario que realiza la orden")
    sub_orders: List['SubOrderCreate'] = Field(..., min_items=1, description="Sub-órdenes de la orden")

class OrderUpdate(BaseModel):
    status: Optional[str] = None
    shipping_address: Optional[Dict[str, Any]] = None
    billing_address: Optional[Dict[str, Any]] = None
    order_metadata: Optional[Dict[str, Any]] = None  # Cambiado de metadataimg a order_metadata

    @validator('status')
    def validate_status(cls, v):
        if v is not None:
            valid_statuses = ['pending', 'confirmed', 'processing', 'shipped', 'delivered', 'cancelled', 'refunded']
            if v not in valid_statuses:
                raise ValueError(f'Status debe ser uno de: {", ".join(valid_statuses)}')
        return v

class OrderOut(OrderBase):
    id: int
    external_id: UUID
    user_id: int
    created_at: datetime
    updated_at: datetime
    sub_orders: List['SubOrderOut'] = []

    class Config:
        from_attributes = True

# Esquemas para SubOrder
class SubOrderBase(BaseModel):
    store_id: int = Field(..., gt=0, description="ID de la tienda")
    subtotal_cop: int = Field(..., gt=0, description="Subtotal en centavos")
    shipping_cop: int = Field(default=0, ge=0, description="Costo de envío en centavos")
    marketplace_fee_cop: int = Field(default=0, ge=0, description="Comisión del marketplace en centavos")
    seller_net_cop: int = Field(..., gt=0, description="Monto neto para el vendedor en centavos")
    status: str = Field(default="pending", description="Estado del sub-orden")

class SubOrderCreate(SubOrderBase):
    order_items: List['OrderItemCreate'] = Field(..., min_items=1, description="Items del sub-orden")

class SubOrderUpdate(BaseModel):
    status: Optional[str] = None
    shipping_cop: Optional[int] = Field(None, ge=0)
    marketplace_fee_cop: Optional[int] = Field(None, ge=0)
    seller_net_cop: Optional[int] = Field(None, gt=0)

class SubOrderOut(SubOrderBase):
    id: int
    external_id: UUID
    order_id: int
    created_at: datetime
    updated_at: datetime
    order_items: List['OrderItemOut'] = []

    class Config:
        from_attributes = True

# Esquemas para OrderItem
class OrderItemBase(BaseModel):
    product_id: int = Field(..., gt=0, description="ID del producto")
    product_variant_id: Optional[int] = Field(None, gt=0, description="ID de la variante del producto")
    title: str = Field(..., min_length=1, description="Título del item")
    unit_price_cop: int = Field(..., gt=0, description="Precio unitario en centavos")
    quantity: int = Field(..., gt=0, description="Cantidad")

class OrderItemCreate(OrderItemBase):
    pass

class OrderItemOut(OrderItemBase):
    id: int
    sub_order_id: int
    total_price_cop: int
    created_at: datetime

    class Config:
        from_attributes = True

# Esquemas para OrderMessage
class OrderMessageBase(BaseModel):
    body: str = Field(..., min_length=1, description="Contenido del mensaje")
    attachments: Optional[Dict[str, Any]] = None

class OrderMessageCreate(OrderMessageBase):
    order_id: int = Field(..., gt=0, description="ID de la orden")
    to_user_id: Optional[int] = Field(None, gt=0, description="ID del usuario destinatario")

class OrderMessageUpdate(BaseModel):
    is_read: Optional[bool] = None

class OrderMessageOut(OrderMessageBase):
    id: int
    order_id: int
    from_user_id: Optional[int]
    to_user_id: Optional[int]
    is_read: bool
    created_at: datetime

    class Config:
        from_attributes = True

# Actualizar referencias forward
OrderCreate.model_rebuild()
SubOrderCreate.model_rebuild()