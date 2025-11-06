from fastapi import FastAPI
from sqlmodel import SQLModel
from .config.db import engine
from .models import Notificacion
from .routes.notificacion_router import router


app = FastAPI(title="Notification-Service")

@app.get("/")
def home():
    return {"message" : "Hola mundo"}

app.include_router(router)