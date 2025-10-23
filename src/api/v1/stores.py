from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session
from typing import List, Optional
from uuid import UUID

from ...db import get_db
from ...repositories.store_repository import StoreRepository
from ...schemas.store import StoreCreate, StoreOut, StoreUpdate

# Constantes
STORE_NOT_FOUND_ERROR = "Tienda no encontrada"
SLUG_ALREADY_IN_USE_ERROR = "El slug ya está en uso"

router = APIRouter(prefix="/stores", tags=["stores"])

@router.post("", response_model=StoreOut, status_code=status.HTTP_201_CREATED)
def create_store(
    store_data: StoreCreate,
    db: Session = Depends(get_db)
):
    """Crear una nueva tienda"""
    try:
        store_repo = StoreRepository(db)
        
        # Verificar que el slug no esté en uso
        existing_store = store_repo.get_store_by_slug(store_data.slug)
        if existing_store:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail=SLUG_ALREADY_IN_USE_ERROR
            )
        
        store = store_repo.create_store(store_data)
        return store
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Error al crear la tienda: {str(e)}"
        )

@router.get("/{store_id}", response_model=StoreOut)
def get_store(
    store_id: int,
    db: Session = Depends(get_db)
):
    """Obtener una tienda por ID"""
    store_repo = StoreRepository(db)
    store = store_repo.get_store_by_id(store_id)
    
    if not store:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=STORE_NOT_FOUND_ERROR
        )
    
    return store

@router.get("/external/{external_id}", response_model=StoreOut)
def get_store_by_external_id(
    external_id: UUID,
    db: Session = Depends(get_db)
):
    """Obtener una tienda por external_id"""
    store_repo = StoreRepository(db)
    store = store_repo.get_store_by_external_id(str(external_id))
    
    if not store:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=STORE_NOT_FOUND_ERROR
        )
    
    return store

@router.get("/slug/{slug}", response_model=StoreOut)
def get_store_by_slug(
    slug: str,
    db: Session = Depends(get_db)
):
    """Obtener una tienda por slug"""
    store_repo = StoreRepository(db)
    store = store_repo.get_store_by_slug(slug)
    
    if not store:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=STORE_NOT_FOUND_ERROR
        )
    
    return store

@router.get("", response_model=List[StoreOut])
def list_stores(
    owner_user_id: Optional[int] = Query(None, description="Filtrar por propietario"),
    plan: Optional[str] = Query(None, description="Filtrar por plan"),
    is_active: Optional[bool] = Query(None, description="Filtrar por estado activo"),
    country: Optional[str] = Query(None, description="Filtrar por país"),
    limit: int = Query(50, ge=1, le=200, description="Límite de resultados"),
    offset: int = Query(0, ge=0, description="Offset para paginación"),
    db: Session = Depends(get_db)
):
    """Listar tiendas con filtros opcionales"""
    store_repo = StoreRepository(db)
    stores = store_repo.get_stores_with_filters(
        owner_user_id=owner_user_id,
        plan=plan,
        is_active=is_active,
        country=country,
        limit=limit,
        offset=offset
    )
    return stores

@router.get("/owner/{owner_user_id}", response_model=List[StoreOut])
def get_owner_stores(
    owner_user_id: int,
    limit: int = Query(50, ge=1, le=200),
    offset: int = Query(0, ge=0),
    db: Session = Depends(get_db)
):
    """Obtener tiendas de un propietario específico"""
    store_repo = StoreRepository(db)
    stores = store_repo.get_stores_by_owner(owner_user_id, limit, offset)
    return stores

@router.put("/{store_id}", response_model=StoreOut)
def update_store(
    store_id: int,
    store_data: StoreUpdate,
    db: Session = Depends(get_db)
):
    """Actualizar una tienda"""
    store_repo = StoreRepository(db)
    
    # Si se está actualizando el slug, verificar que no esté en uso
    if store_data.slug:
        existing_store = store_repo.get_store_by_slug(store_data.slug)
        if existing_store and existing_store.id != store_id:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail=SLUG_ALREADY_IN_USE_ERROR
            )
    
    store = store_repo.update_store(store_id, store_data)
    
    if not store:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=STORE_NOT_FOUND_ERROR
        )
    
    return store

@router.delete("/{store_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_store(
    store_id: int,
    db: Session = Depends(get_db)
):
    """Eliminar una tienda (soft delete)"""
    store_repo = StoreRepository(db)
    success = store_repo.delete_store(store_id)
    
    if not success:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=STORE_NOT_FOUND_ERROR
        )