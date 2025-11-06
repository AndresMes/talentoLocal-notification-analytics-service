from datetime import datetime
from typing import Optional
from pydantic import BaseModel, Field


class NotificacionCreateDTO(BaseModel):
    id_usuario: int
    id_empresa: int
    tipo_notificacion: str = Field(nullable = False)
    asunto: str = Field(nullable = False, min_length=5, max_length=30)
    mensaje: str 

    id_oferta: int
    prioridad: Optional[int] = None
    datos_adicionales: Optional[str] = None


class NotificacionResponseDTO(BaseModel):
    id_notificacion: str
    id_usuario: int
    id_empresa: int
    tipo_notificacion: str 
    asunto: str 
    mensaje: str 
    id_oferta: int
    prioridad: Optional[int] = None
    datos_adicionales: Optional[str] = None
    leida: bool
    fecha_lectura : Optional[datetime] = None
    fecha_creacion: datetime

    model_config = {"from_attributes": True}
