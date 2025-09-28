# src/repositories/order_repository.py
from typing import List, Optional, Dict, Any
from sqlalchemy.orm import Session, joinedload
from sqlalchemy import and_, or_, desc
from uuid import uuid4
from ..models.order import Order, SubOrder, OrderItem, OrderMessage
from ..schemas.order import OrderCreate, OrderUpdate, SubOrderCreate, OrderItemCreate, OrderMessageCreate

class OrderRepository:
    def __init__(self, db: Session):
        self.db = db

    def create_order(self, order_data: OrderCreate) -> Order:
        """Crear una nueva orden con sus sub-órdenes e items"""
        # Crear la orden principal
        order = Order(
            external_id=uuid4(),
            user_id=order_data.user_id,
            total_amount_cop=order_data.total_amount_cop,
            currency=order_data.currency,
            status=order_data.status,
            shipping_address=order_data.shipping_address,
            billing_address=order_data.billing_address,
            order_metadata=order_data.order_metadata  # Cambiado de metadataimg a order_metadata
        )
        
        self.db.add(order)
        self.db.flush()  # Para obtener el ID de la orden
        
        # Crear sub-órdenes
        for sub_order_data in order_data.sub_orders:
            sub_order = SubOrder(
                external_id=uuid4(),
                order_id=order.id,
                store_id=sub_order_data.store_id,
                subtotal_cop=sub_order_data.subtotal_cop,
                shipping_cop=sub_order_data.shipping_cop,
                marketplace_fee_cop=sub_order_data.marketplace_fee_cop,
                seller_net_cop=sub_order_data.seller_net_cop,
                status=sub_order_data.status
            )
            
            self.db.add(sub_order)
            self.db.flush()  # Para obtener el ID del sub-orden
            
            # Crear items del sub-orden
            for item_data in sub_order_data.order_items:
                order_item = OrderItem(
                    sub_order_id=sub_order.id,
                    product_id=item_data.product_id,
                    product_variant_id=item_data.product_variant_id,
                    title=item_data.title,
                    unit_price_cop=item_data.unit_price_cop,
                    quantity=item_data.quantity,
                    total_price_cop=item_data.unit_price_cop * item_data.quantity
                )
                self.db.add(order_item)
        
        self.db.commit()
        self.db.refresh(order)
        return order

    def get_order_by_id(self, order_id: int) -> Optional[Order]:
        """Obtener una orden por ID con todas sus relaciones"""
        return self.db.query(Order)\
            .options(
                joinedload(Order.sub_orders).joinedload(SubOrder.order_items),
                joinedload(Order.user),
                joinedload(Order.order_messages)
            )\
            .filter(Order.id == order_id)\
            .first()

    def get_order_by_external_id(self, external_id: str) -> Optional[Order]:
        """Obtener una orden por external_id"""
        return self.db.query(Order)\
            .options(
                joinedload(Order.sub_orders).joinedload(SubOrder.order_items),
                joinedload(Order.user),
                joinedload(Order.order_messages)
            )\
            .filter(Order.external_id == external_id)\
            .first()

    def get_orders_by_user(self, user_id: int, limit: int = 50, offset: int = 0) -> List[Order]:
        """Obtener órdenes de un usuario específico"""
        return self.db.query(Order)\
            .options(
                joinedload(Order.sub_orders).joinedload(SubOrder.order_items)
            )\
            .filter(Order.user_id == user_id)\
            .order_by(desc(Order.created_at))\
            .offset(offset)\
            .limit(limit)\
            .all()

    def get_orders_by_status(self, status: str, limit: int = 50, offset: int = 0) -> List[Order]:
        """Obtener órdenes por estado"""
        return self.db.query(Order)\
            .options(
                joinedload(Order.sub_orders).joinedload(SubOrder.order_items)
            )\
            .filter(Order.status == status)\
            .order_by(desc(Order.created_at))\
            .offset(offset)\
            .limit(limit)\
            .all()

    def update_order(self, order_id: int, order_data: OrderUpdate) -> Optional[Order]:
        """Actualizar una orden"""
        order = self.db.query(Order).filter(Order.id == order_id).first()
        if not order:
            return None
        
        update_data = order_data.dict(exclude_unset=True)
        for field, value in update_data.items():
            setattr(order, field, value)
        
        self.db.commit()
        self.db.refresh(order)
        return order

    def delete_order(self, order_id: int) -> bool:
        """Eliminar una orden (soft delete usando order_metadata)"""
        order = self.db.query(Order).filter(Order.id == order_id).first()
        if not order:
            return False
        
        # En lugar de eliminar físicamente, marcamos como eliminada
        if order.order_metadata is None:  # Cambiado de metadataimg a order_metadata
            order.order_metadata = {}
        order.order_metadata["deleted"] = True
        order.order_metadata["deleted_at"] = "now()"
        
        self.db.commit()
        return True

    def create_order_message(self, message_data: OrderMessageCreate, from_user_id: int) -> OrderMessage:
        """Crear un mensaje en una orden"""
        message = OrderMessage(
            order_id=message_data.order_id,
            from_user_id=from_user_id,
            to_user_id=message_data.to_user_id,
            body=message_data.body,
            attachments=message_data.attachments
        )
        
        self.db.add(message)
        self.db.commit()
        self.db.refresh(message)
        return message

    def get_order_messages(self, order_id: int) -> List[OrderMessage]:
        """Obtener mensajes de una orden"""
        return self.db.query(OrderMessage)\
            .filter(OrderMessage.order_id == order_id)\
            .order_by(OrderMessage.created_at)\
            .all()

    def mark_message_as_read(self, message_id: int) -> bool:
        """Marcar un mensaje como leído"""
        message = self.db.query(OrderMessage).filter(OrderMessage.id == message_id).first()
        if not message:
            return False
        
        message.is_read = True
        self.db.commit()
        return True

    def get_orders_with_filters(
        self, 
        user_id: Optional[int] = None,
        status: Optional[str] = None,
        store_id: Optional[int] = None,
        limit: int = 50,
        offset: int = 0
    ) -> List[Order]:
        """Obtener órdenes con filtros múltiples"""
        query = self.db.query(Order).options(
            joinedload(Order.sub_orders).joinedload(SubOrder.order_items)
        )
        
        if user_id:
            query = query.filter(Order.user_id == user_id)
        
        if status:
            query = query.filter(Order.status == status)
        
        if store_id:
            query = query.join(SubOrder).filter(SubOrder.store_id == store_id)
        
        return query.order_by(desc(Order.created_at))\
            .offset(offset)\
            .limit(limit)\
            .all()