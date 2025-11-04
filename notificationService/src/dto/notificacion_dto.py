from datetime import datetime
from typing import Optional
from pydantic import BaseModel


class NotificacionCreateDTO(BaseModel):
    id_usuario: int
    id_empresa: int
    id_oferta: int
    asunto: str
    mensaje: str
    prioridad: Optional[str] = None
    datos_adicionales: Optional[str] = None
    fecha_expiracion: Optional[datetime] = None


class NotificacionReadDTO(BaseModel):
    id_notificacion: int
    asunto: str
    mensaje: str
    leida: bool
    prioridad: Optional[str]
    fecha_creacion: datetime
    fecha_expiracion: Optional[datetime]

    class Config:
        orm_mode = True  # Permite devolver objetos ORM directamente desde SQLModel
