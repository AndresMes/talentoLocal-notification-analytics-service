from fastapi import FastAPI
from sqlmodel import SQLModel
from .config.db import engine
from .models import Notificacion, TipoNotificacion
from .routes.tipo_notificacion_router import tipo_notificacion_router 

app = FastAPI(title="Notification-Service")

@app.get("/")
def home():
    return {"message" : "Hola mundo"}

app.include_router(tipo_notificacion_router)