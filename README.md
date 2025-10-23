# LUM Backend

API desarrollada con FastAPI para gestionar usuarios, órdenes y tiendas.

## Requisitos
- Python 3.10+
- PostgreSQL

## Instalación

1. **Clonar repositorio**:
   ```bash
   git clone https://github.com/Corosso/lum-backend.git
   cd lum-backend
   ```

2. **Crear entorno virtual**:
   ```bash
   python -m venv venv
   .\venv\Scripts\activate
   ```

3. **Instalar dependencias**:
   ```bash
   pip install -r requirements.txt
   ```

4. **Configurar variables de entorno**:
   Crear archivo `.env`:
   ```
   DATABASE_URL=postgresql://usuario:contraseña@localhost/nombre_db
   SECRET_KEY=tu_clave_secreta_aqui
   ```

5. **Ejecutar aplicación**:
   ```bash
   uvicorn src.main:app --reload
   ```

## Documentación API
- Swagger UI: http://127.0.0.1:8000/docs
- ReDoc: http://127.0.0.1:8000/redoc

## Estructura
```
src/
├── api/v1/         # Endpoints
├── core/           # Configuración
├── models/         # Modelos DB
├── repositories/   # Lógica de datos
├── schemas/        # Validación
└── main.py         # App principal
```