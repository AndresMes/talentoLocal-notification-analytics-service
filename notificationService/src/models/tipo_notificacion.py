# notificationService/src/models/tipo_notificacion.py
from __future__ import annotations
from typing import TYPE_CHECKING, Optional, List


from sqlmodel import SQLModel, Field, Relationship

if TYPE_CHECKING:
    from .notificacion import Notificacion


class TipoNotificacion(SQLModel, table=True):
    __tablename__ = "tipo_notificaciones"

    id_tipo_notificacion: int | None = Field(default=None, primary_key=True)
    codigo: str = Field(nullable=False)
    nombre: str = Field(nullable=False)
    descripcion: str | None = None
    plantilla_asunto: str | None = None
    plantilla_mensaje: str | None = None
    activo: bool = True

    # Especifica la clase target como string en el Relationship
    notificaciones: List["Notificacion"]= Relationship(back_populates="tipo_notificacion")