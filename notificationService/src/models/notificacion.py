# notificationService/src/models/notificacion.py
from __future__ import annotations
from typing import Optional
from datetime import datetime

from sqlmodel import SQLModel, Field


class Notificacion(SQLModel, table=True):
    __tablename__:str = "notificaciones"

    id_notificacion: int | None = Field(default=None, primary_key=True)

    id_usuario: str = Field(nullable=False, max_length=50)  # UUID como VARCHAR(50)
    id_empresa: str = Field(nullable=False, max_length=50)  # UUID como VARCHAR(50)

    tipo_notificacion: str = Field(nullable=False)
    asunto: str = Field(nullable=False)
    mensaje: str

    id_oferta: int = Field(nullable=False)
    prioridad: str | None = None
    datos_adicionales: str | None = None

    leida: bool = Field(default=False) 
    fecha_lectura: datetime | None = None
    fecha_creacion: datetime = Field(default_factory=datetime.utcnow)