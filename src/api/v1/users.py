from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session
from uuid import uuid4
from sqlalchemy.sql import func

from ...db import get_db
from ...models.user import User
from ...schemas.user import UserCreate, UserOut, UserUpdate
from ...services.auth0 import update_auth0_user_metadata, create_auth0_user

router = APIRouter(prefix="/users", tags=["users"])

@router.post("", response_model=UserOut, status_code=status.HTTP_201_CREATED)
def create_user(payload: UserCreate, db: Session = Depends(get_db)):
    """Crear un nuevo usuario"""
    # Validar que los campos requeridos estén presentes
    required_fields = [payload.full_name, payload.phone]
    if any(f is None or (isinstance(f, str) and not f.strip()) for f in required_fields):
        raise HTTPException(status_code=400, detail="Faltan datos obligatorios para crear el usuario. Por favor completa todos los campos requeridos.")

    # Si ya viene auth0_user_id, no crear en Auth0, solo guardar y actualizar metadata
    if payload.auth0_user_id:
        auth0_user_id = payload.auth0_user_id
    else:
        # Crear usuario en Auth0 primero
        try:
            auth0_user = create_auth0_user(
                email=payload.email,
                password=payload.password_hash if payload.password_hash else None,
                full_name=payload.full_name,
                phone=payload.phone,
                is_verified=payload.is_verified,
                can_sell=payload.can_sell
            )
            auth0_user_id = auth0_user.get("user_id")
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Error creando usuario en Auth0: {e}")

    user = User(
        external_id=uuid4(),
        email=payload.email,
        password_hash=payload.password_hash,
        full_name=payload.full_name,
        phone=payload.phone,
        is_verified=payload.is_verified,
        can_sell=payload.can_sell,
        auth0_user_id=auth0_user_id
    )

    db.add(user)
    db.commit()
    db.refresh(user)

    # Actualizar metadata en Auth0 (por si quieres guardar el id interno de tu BD)
    if auth0_user_id:
        metadata = {
            "numero": user.phone,
            "id": user.id,
            "is_verified": user.is_verified,
            "can_sell": user.can_sell
        }
        try:
            update_auth0_user_metadata(auth0_user_id, metadata)
        except Exception as e:
            print(f"Error actualizando metadata en Auth0: {e}")

    return user

@router.get("/{user_id}", response_model=UserOut)
def get_user(user_id: int, db: Session = Depends(get_db)):
    """Obtener un usuario por ID"""
    user = db.query(User).filter(User.id == user_id).filter(User.deleted_at.is_(None)).first()
    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Usuario no encontrado")
    return user

@router.get("", response_model=list[UserOut])
def list_users(
    db: Session = Depends(get_db),
    limit: int = Query(50, ge=1, le=200),
    offset: int = Query(0, ge=0),
):
    """Listar usuarios"""
    q = db.query(User).filter(User.deleted_at.is_(None)).order_by(User.id).offset(offset).limit(limit)
    return q.all()

@router.put("/{user_id}", response_model=UserOut)
def update_user(
    user_id: int, 
    user_data: UserUpdate, 
    db: Session = Depends(get_db)
):
    """Actualizar un usuario"""
    user = db.query(User).filter(User.id == user_id).filter(User.deleted_at.is_(None)).first()
    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Usuario no encontrado")
    
    update_data = user_data.dict(exclude_unset=True)
    for field, value in update_data.items():
        setattr(user, field, value)

    db.commit()
    db.refresh(user)

    # Actualizar datos y metadata en Auth0 si el usuario tiene auth0_user_id
    auth0_user_id = user.auth0_user_id or getattr(user_data, 'auth0_user_id', None)
    if auth0_user_id:
        metadata = {
            "numero": user.phone,
            "id": user.id,
            "is_verified": user.is_verified,
            "can_sell": user.can_sell
        }
        try:
            update_auth0_user_metadata(auth0_user_id, metadata)
            # Si se requiere actualizar email, nombre, etc. en Auth0, aquí puedes hacerlo
        except Exception as e:
            print(f"Error actualizando metadata en Auth0: {e}")

    return user

@router.delete("/{user_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_user(user_id: int, db: Session = Depends(get_db)):
    """Eliminar un usuario (soft delete)"""
    user = db.query(User).filter(User.id == user_id).filter(User.deleted_at.is_(None)).first()
    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Usuario no encontrado")

    # Eliminar en Auth0 si tiene auth0_user_id
    if user.auth0_user_id:
        try:
            from ...services.auth0_delete import delete_auth0_user
            delete_auth0_user(user.auth0_user_id)
        except Exception as e:
            print(f"Error eliminando usuario en Auth0: {e}")

    user.deleted_at = func.now()
    db.commit()




#
#    _________        _________
#   /  _______|      / _______ \
#   |  |            | | x   x | |
#   |  |            | |  x x  | |
#   |  |            | |   +   | |
#   |  |            | |   +   | |
#   |  |            | |  x x  | |
#   |  |_______     | |_x___x_| |
#   \__________|     \_________/
#    _________        _________
#   |    __   \      / _______ \
#   |   |  |   |    | | x   x | |
#   |   |__|   |    | |  x x  | |
#   |   __   __|    | |   +   | |
#   |  |  \  \      | |   +   | |
#   |  |   \  \     | |  x x  | |
#   |  |    \  \    | |_x___x_| |
#   |__|     \__\    \_________/
#
#
#
#
#
