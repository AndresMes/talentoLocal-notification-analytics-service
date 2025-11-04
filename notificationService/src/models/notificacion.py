from sqlmodel import SQLModel, Field, Relationship
from typing import Optional
from datetime import datetime

from .tipo_notificacion import TipoNotificacion


class Notificacion(SQLModel, table=True):
    id_notificacion: Optional[int] = Field(default=None, primary_key=True)

    id_tipo_notificacion: int = Field(foreign_key="tiponotificacion.id_tipo_notificacion", nullable=False)
    id_usuario: int = Field(nullable=False)
    id_empresa: int = Field(nullable=False)
    id_oferta: int = Field(nullable=False)

    asunto: str
    mensaje: str
    prioridad: Optional[str] = None
    datos_adicionales: Optional[str] = None

    leida: bool = False 
    fecha_lectura: Optional[datetime] = None
    fecha_creacion: datetime = Field(default_factory=datetime.utcnow)
    fecha_expiracion: Optional[datetime] = None

    # Relación hacia TipoNotificacion
    tipo_notificacion: Optional[TipoNotificacion] = Relationship(back_populates="notificaciones")
