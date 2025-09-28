# src/api/v1/orders.py
from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session
from typing import List, Optional
from uuid import UUID

from ...db import get_db
from ...repositories.order_repository import OrderRepository
from ...models.order import OrderMessage
from ...schemas.order import (
    OrderCreate, OrderOut, OrderUpdate,
    OrderMessageCreate, OrderMessageOut, OrderMessageUpdate
)

router = APIRouter(prefix="/orders", tags=["orders"])

@router.post("", response_model=OrderOut, status_code=status.HTTP_201_CREATED)
def create_order(
    order_data: OrderCreate,
    db: Session = Depends(get_db)
):
    """Crear una nueva orden"""
    try:
        order_repo = OrderRepository(db)
        order = order_repo.create_order(order_data)
        return order
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Error al crear la orden: {str(e)}"
        )

@router.get("/{order_id}", response_model=OrderOut)
def get_order(
    order_id: int,
    db: Session = Depends(get_db)
):
    """Obtener una orden por ID"""
    order_repo = OrderRepository(db)
    order = order_repo.get_order_by_id(order_id)
    
    if not order:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Orden no encontrada"
        )
    
    return order

@router.get("/external/{external_id}", response_model=OrderOut)
def get_order_by_external_id(
    external_id: UUID,
    db: Session = Depends(get_db)
):
    """Obtener una orden por external_id"""
    order_repo = OrderRepository(db)
    order = order_repo.get_order_by_external_id(str(external_id))
    
    if not order:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Orden no encontrada"
        )
    
    return order

@router.get("", response_model=List[OrderOut])
def list_orders(
    user_id: Optional[int] = Query(None, description="Filtrar por usuario"),
    status: Optional[str] = Query(None, description="Filtrar por estado"),
    store_id: Optional[int] = Query(None, description="Filtrar por tienda"),
    limit: int = Query(50, ge=1, le=200, description="Límite de resultados"),
    offset: int = Query(0, ge=0, description="Offset para paginación"),
    db: Session = Depends(get_db)
):
    """Listar órdenes con filtros opcionales"""
    order_repo = OrderRepository(db)
    orders = order_repo.get_orders_with_filters(
        user_id=user_id,
        status=status,
        store_id=store_id,
        limit=limit,
        offset=offset
    )
    return orders

@router.get("/user/{user_id}", response_model=List[OrderOut])
def get_user_orders(
    user_id: int,
    limit: int = Query(50, ge=1, le=200),
    offset: int = Query(0, ge=0),
    db: Session = Depends(get_db)
):
    """Obtener órdenes de un usuario específico"""
    order_repo = OrderRepository(db)
    orders = order_repo.get_orders_by_user(user_id, limit, offset)
    return orders

@router.put("/{order_id}", response_model=OrderOut)
def update_order(
    order_id: int,
    order_data: OrderUpdate,
    db: Session = Depends(get_db)
):
    """Actualizar una orden"""
    order_repo = OrderRepository(db)
    order = order_repo.update_order(order_id, order_data)
    
    if not order:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Orden no encontrada"
        )
    
    return order

@router.delete("/{order_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_order(
    order_id: int,
    db: Session = Depends(get_db)
):
    """Eliminar una orden (soft delete)"""
    order_repo = OrderRepository(db)
    success = order_repo.delete_order(order_id)
    
    if not success:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Orden no encontrada"
        )

# Endpoints para mensajes de órdenes
@router.post("/{order_id}/messages", response_model=OrderMessageOut, status_code=status.HTTP_201_CREATED)
def create_order_message(
    order_id: int,
    message_data: OrderMessageCreate,
    from_user_id: int = Query(..., description="ID del usuario que envía el mensaje"),
    db: Session = Depends(get_db)
):
    """Crear un mensaje en una orden"""
    # Verificar que la orden existe
    order_repo = OrderRepository(db)
    order = order_repo.get_order_by_id(order_id)
    if not order:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Orden no encontrada"
        )
    
    message_data.order_id = order_id
    message = order_repo.create_order_message(message_data, from_user_id)
    return message

@router.get("/{order_id}/messages", response_model=List[OrderMessageOut])
def get_order_messages(
    order_id: int,
    db: Session = Depends(get_db)
):
    """Obtener mensajes de una orden"""
    order_repo = OrderRepository(db)
    messages = order_repo.get_order_messages(order_id)
    return messages

@router.put("/messages/{message_id}", response_model=OrderMessageOut)
def update_order_message(
    message_id: int,
    message_data: OrderMessageUpdate,
    db: Session = Depends(get_db)
):
    """Actualizar un mensaje de orden (principalmente para marcar como leído)"""
    order_repo = OrderRepository(db)
    
    if message_data.is_read:
        success = order_repo.mark_message_as_read(message_id)
        if not success:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Mensaje no encontrado"
            )
    
    # Obtener el mensaje actualizado
    message = db.query(OrderMessage).filter(OrderMessage.id == message_id).first()
    if not message:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Mensaje no encontrado"
        )
    
    return message