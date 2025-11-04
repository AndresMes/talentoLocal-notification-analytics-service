# notificationService/src/models/notificacion.py
from __future__ import annotations
from typing import TYPE_CHECKING, Optional, List
from datetime import datetime

from sqlmodel import SQLModel, Field, Relationship

if TYPE_CHECKING:
    from .tipo_notificacion import TipoNotificacion


class Notificacion(SQLModel, table=True):
    __tablename__ = "notificaciones"

    id_notificacion: int | None = Field(default=None, primary_key=True)

    id_usuario: int = Field(nullable=False)
    id_empresa: int = Field(nullable=False)
    id_oferta: int = Field(nullable=False)

    asunto: str
    mensaje: str
    prioridad: str | None = None
    datos_adicionales: str | None = None

    leida: bool = False
    fecha_lectura: datetime | None = None
    fecha_creacion: datetime = Field(default_factory=datetime.utcnow)
    fecha_expiracion: datetime | None = None

    id_tipo_notificacion: Optional[int] = Field(default=None, foreign_key="tipo_notificaciones.id_tipo_notificacion")
    tipo_notificacion: Optional["TipoNotificacion"] = Relationship(back_populates="notificaciones")
    