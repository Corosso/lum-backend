# LUM Backend

## Descripción
LUM Backend es una API desarrollada en Python utilizando FastAPI. Proporciona funcionalidades para gestionar usuarios, órdenes y tiendas, y está diseñada para ser modular y escalable. Este proyecto utiliza SQLAlchemy para la interacción con la base de datos y Pydantic para la validación de datos.

## Características Principales
- **Gestión de Usuarios**: Crear, obtener, listar, actualizar y eliminar usuarios.
- **Gestión de Órdenes**: Crear órdenes con subórdenes e ítems, obtener órdenes por diferentes criterios, y gestionar mensajes asociados a órdenes.
- **Gestión de Tiendas**: Crear, obtener, listar, actualizar y eliminar tiendas con filtros avanzados.
- **Base de Datos**: Modelos relacionales definidos con SQLAlchemy.
- **Configuración**: Variables de entorno gestionadas con dotenv.

## Requisitos Previos
- Python 3.10 o superior
- PostgreSQL

## Instalación
1. Clona el repositorio:
   ```bash
   git clone https://github.com/Corosso/lum-backend.git
   cd lum-backend
   ```

2. Crea y activa un entorno virtual:
   ```bash
   python -m venv venv
   .\venv\Scripts\activate  # En Windows
   # source venv/bin/activate  # En Linux/Mac
   ```

3. Instala las dependencias:
   ```bash
   pip install -r requirements.txt
   ```

4. Configura las variables de entorno:
   - Crea un archivo `.env` en la raíz del proyecto basado en el archivo de ejemplo proporcionado.
   - Asegúrate de configurar correctamente las credenciales de la base de datos.

5. Ejecuta la aplicación:
   ```bash
   uvicorn src.main:app --reload
   ```

6. Accede a la documentación interactiva de la API en:
   - [http://127.0.0.1:8000/docs](http://127.0.0.1:8000/docs) (Swagger UI)
   - [http://127.0.0.1:8000/redoc](http://127.0.0.1:8000/redoc) (ReDoc)

## Estructura del Proyecto
```
.
├── src/
│   ├── api/v1/         # Rutas de la API
│   ├── core/           # Configuración del proyecto
│   ├── db.py           # Configuración de la base de datos
│   ├── main.py         # Punto de entrada de la aplicación
│   ├── models/         # Modelos de base de datos
│   ├── repositories/   # Lógica de acceso a datos
│   ├── schemas/        # Esquemas de entrada/salida
├── .env                # Variables de entorno
├── requirements.txt    # Dependencias del proyecto
```

## Implementación de Login
Para implementar un sistema de login, puedes seguir estos pasos:

1. **Crear un endpoint de autenticación**:
   - Utiliza un esquema como `UserBase` para validar las credenciales de entrada.
   - Verifica el `email` y `password_hash` del usuario en la base de datos.

2. **Generar un token de acceso**:
   - Usa una librería como `PyJWT` para generar tokens JWT.
   - Configura una clave secreta en el archivo `.env`.

3. **Proteger rutas**:
   - Implementa un middleware o dependencia en FastAPI para validar el token en las rutas protegidas.

### Ejemplo de Endpoint de Login
```python
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from passlib.context import CryptContext
from datetime import datetime, timedelta
import jwt

from ...db import get_db
from ...models.user import User
from ...schemas.user import UserBase

router = APIRouter()

SECRET_KEY = "cambia_esto_en_produccion"
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def verify_password(plain_password, hashed_password):
    return pwd_context.verify(plain_password, hashed_password)

def create_access_token(data: dict, expires_delta: timedelta):
    to_encode = data.copy()
    expire = datetime.utcnow() + expires_delta
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)

@router.post("/login")
def login(user: UserBase, db: Session = Depends(get_db)):
    db_user = db.query(User).filter(User.email == user.email).first()
    if not db_user or not verify_password(user.password, db_user.password_hash):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Credenciales incorrectas",
        )
    access_token = create_access_token(
        data={"sub": db_user.email},
        expires_delta=timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES),
    )
    return {"access_token": access_token, "token_type": "bearer"}
```

## Contribuciones
¡Las contribuciones son bienvenidas! Si encuentras un problema o tienes una mejora, no dudes en abrir un issue o enviar un pull request.

## Licencia
Este proyecto está bajo la licencia MIT.