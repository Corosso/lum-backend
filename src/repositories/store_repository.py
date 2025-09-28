from typing import List, Optional
from sqlalchemy.orm import Session, joinedload
from sqlalchemy import and_, or_, desc
from uuid import uuid4
from ..models.stores import Store
from ..schemas.store import StoreCreate, StoreUpdate
from sqlalchemy.sql import func

class StoreRepository:
    def __init__(self, db: Session):
        self.db = db

    def create_store(self, store_data: StoreCreate) -> Store:
        """Crear una nueva tienda"""
        store = Store(
            external_id=uuid4(),
            owner_user_id=store_data.owner_user_id,
            name=store_data.name,
            slug=store_data.slug,
            description=store_data.description,
            logo_key=store_data.logo_key,
            banner_key=store_data.banner_key,
            country=store_data.country,
            city=store_data.city,
            is_active=store_data.is_active,
            plan=store_data.plan
        )
        
        self.db.add(store)
        self.db.commit()
        self.db.refresh(store)
        return store

    def get_store_by_id(self, store_id: int) -> Optional[Store]:
        """Obtener una tienda por ID"""
        return self.db.query(Store)\
            .options(
                joinedload(Store.owner),
                joinedload(Store.products),
                joinedload(Store.store_users)
            )\
            .filter(Store.id == store_id)\
            .filter(Store.deleted_at.is_(None))\
            .first()

    def get_store_by_external_id(self, external_id: str) -> Optional[Store]:
        """Obtener una tienda por external_id"""
        return self.db.query(Store)\
            .options(
                joinedload(Store.owner),
                joinedload(Store.products)
            )\
            .filter(Store.external_id == external_id)\
            .filter(Store.deleted_at.is_(None))\
            .first()

    def get_store_by_slug(self, slug: str) -> Optional[Store]:
        """Obtener una tienda por slug"""
        return self.db.query(Store)\
            .options(
                joinedload(Store.owner),
                joinedload(Store.products)
            )\
            .filter(Store.slug == slug)\
            .filter(Store.deleted_at.is_(None))\
            .first()

    def get_stores_by_owner(self, owner_user_id: int, limit: int = 50, offset: int = 0) -> List[Store]:
        """Obtener tiendas de un propietario específico"""
        return self.db.query(Store)\
            .options(joinedload(Store.owner))\
            .filter(Store.owner_user_id == owner_user_id)\
            .filter(Store.deleted_at.is_(None))\
            .order_by(desc(Store.created_at))\
            .offset(offset)\
            .limit(limit)\
            .all()

    def get_stores_by_plan(self, plan: str, limit: int = 50, offset: int = 0) -> List[Store]:
        """Obtener tiendas por plan"""
        return self.db.query(Store)\
            .options(joinedload(Store.owner))\
            .filter(Store.plan == plan)\
            .filter(Store.deleted_at.is_(None))\
            .order_by(desc(Store.created_at))\
            .offset(offset)\
            .limit(limit)\
            .all()

    def get_active_stores(self, limit: int = 50, offset: int = 0) -> List[Store]:
        """Obtener tiendas activas"""
        return self.db.query(Store)\
            .options(joinedload(Store.owner))\
            .filter(Store.is_active == True)\
            .filter(Store.deleted_at.is_(None))\
            .order_by(desc(Store.created_at))\
            .offset(offset)\
            .limit(limit)\
            .all()

    def update_store(self, store_id: int, store_data: StoreUpdate) -> Optional[Store]:
        """Actualizar una tienda"""
        store = self.db.query(Store)\
            .filter(Store.id == store_id)\
            .filter(Store.deleted_at.is_(None))\
            .first()
        
        if not store:
            return None
        
        update_data = store_data.dict(exclude_unset=True)
        for field, value in update_data.items():
            setattr(store, field, value)
        
        self.db.commit()
        self.db.refresh(store)
        return store

    def delete_store(self, store_id: int) -> bool:
        """Eliminar una tienda (soft delete)"""
        store = self.db.query(Store)\
            .filter(Store.id == store_id)\
            .filter(Store.deleted_at.is_(None))\
            .first()
        
        if not store:
            return False
        
        store.deleted_at = func.now()
        self.db.commit()
        return True

    def get_stores_with_filters(
        self,
        owner_user_id: Optional[int] = None,
        plan: Optional[str] = None,
        is_active: Optional[bool] = None,
        country: Optional[str] = None,
        limit: int = 50,
        offset: int = 0
    ) -> List[Store]:
        """Obtener tiendas con filtros múltiples"""
        query = self.db.query(Store).options(joinedload(Store.owner))
        
        # Siempre filtrar tiendas no eliminadas
        query = query.filter(Store.deleted_at.is_(None))
        
        if owner_user_id:
            query = query.filter(Store.owner_user_id == owner_user_id)
        
        if plan:
            query = query.filter(Store.plan == plan)
        
        if is_active is not None:
            query = query.filter(Store.is_active == is_active)
        
        if country:
            query = query.filter(Store.country == country)
        
        return query.order_by(desc(Store.created_at))\
            .offset(offset)\
            .limit(limit)\
            .all()
