# notificationService/src/models/notificacion.py
from __future__ import annotations
from typing import TYPE_CHECKING, Optional, List
from datetime import datetime

from sqlmodel import SQLModel, Field, Relationship

class NotificacionInt(SQLModel, table=True):
    __tablename__:str = "notificaciones"
    __table_args__ = {'extend_existing': True}

    id_notificacion: int | None = Field(default=None, primary_key=True)

    id_usuario: int 
    id_empresa: int 

    tipo_notificacion: str = Field(nullable=False)
    asunto: str = Field(nullable=False)
    mensaje: str

    id_oferta: int = Field(nullable=False)
    prioridad: int | None = None
    datos_adicionales: str | None = None

    leida: bool = Field(default=False) 
    fecha_lectura: datetime | None = None
    fecha_creacion: datetime = Field(default_factory=datetime.utcnow)
    