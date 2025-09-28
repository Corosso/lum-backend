from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session
from uuid import uuid4
from sqlalchemy.sql import func

from ...db import get_db
from ...models.user import User
from ...schemas.user import UserCreate, UserOut, UserUpdate

router = APIRouter(prefix="/users", tags=["users"])

@router.post("", response_model=UserOut, status_code=status.HTTP_201_CREATED)
def create_user(payload: UserCreate, db: Session = Depends(get_db)):
    """Crear un nuevo usuario"""
    existing = db.query(User).filter(User.email == payload.email).first()
    if existing:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Email ya registrado")

    user = User(
        external_id=uuid4(),
        email=payload.email,
        password_hash=payload.password_hash,
        full_name=payload.full_name,
        phone=payload.phone,
        is_verified=payload.is_verified,
        can_sell=payload.can_sell,
    )
    db.add(user)
    db.commit()
    db.refresh(user)
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
    
    # Verificar que el email no esté en uso por otro usuario
    if user_data.email and user_data.email != user.email:
        existing = db.query(User).filter(User.email == user_data.email).filter(User.id != user_id).first()
        if existing:
            raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Email ya registrado")
    
    update_data = user_data.dict(exclude_unset=True)
    for field, value in update_data.items():
        setattr(user, field, value)
    
    db.commit()
    db.refresh(user)
    return user

@router.delete("/{user_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_user(user_id: int, db: Session = Depends(get_db)):
    """Eliminar un usuario (soft delete)"""
    user = db.query(User).filter(User.id == user_id).filter(User.deleted_at.is_(None)).first()
    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Usuario no encontrado")
    
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
