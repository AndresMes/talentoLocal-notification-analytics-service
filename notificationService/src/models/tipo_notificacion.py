from notificationService.src.models import notificacion
from sqlmodel import SQLModel, Field, Relationship
from typing import Optional, List

class TipoNotificacion(SQLModel, table=True):
    __table_name__ = "tipo_notificaciones"
    id_tipo_notificacion: Optional[int] = Field(default=None, primary_key=True)
    codigo: str = Field(nullable=False)
    nombre: str = Field(nullable=False)
    descripcion: Optional[str] = None
    plantilla_asunto: Optional[str] = None
    plantilla_mensaje: Optional[str] = None
    activo: bool = True

    # Relación inversa hacia Notificacion
    notificaciones: List["notificacion"] = Relationship(back_populates="tipo_notificacion") # type: ignore