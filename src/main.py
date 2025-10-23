# src/main.py
from fastapi import FastAPI
from contextlib import asynccontextmanager
from .db import engine, Base
from .models import user as users_model, order as orders_model  
from .api.v1.users import router as users_router
from .api.v1.orders import router as orders_router
from .api.v1.stores import router as stores_router
from fastapi.middleware.cors import CORSMiddleware

@asynccontextmanager
async def lifespan(app: FastAPI):
    Base.metadata.create_all(bind=engine)
    yield

app = FastAPI(title="LUM Backend", lifespan=lifespan)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],  # Cambia esto por el dominio de tu frontend en producción
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(users_router, prefix="/api/v1")
app.include_router(orders_router, prefix="/api/v1")
app.include_router(stores_router, prefix="/api/v1")

@app.get("/health")
def health():
    return {"status": "ok"}