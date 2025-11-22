from datetime import datetime
from typing import Optional
from pydantic import BaseModel, Field


class NotificacionCreateDTO(BaseModel):
    id_usuario: str = Field(..., max_length=50)  # UUID como string
    id_empresa: str = Field(..., max_length=50)  # UUID como string
    tipo_notificacion: str = Field()
    asunto: str = Field(min_length=5, max_length=30)
    mensaje: str 

    id_oferta: int
    prioridad: Optional[int] = None
    datos_adicionales: Optional[str] = None


class NotificacionResponseDTO(BaseModel):
    id_notificacion: int
    id_usuario: str  # UUID como string
    id_empresa: str  # UUID como string
    tipo_notificacion: str 
    asunto: str 
    mensaje: str 
    id_oferta: int
    prioridad: Optional[int] = None
    datos_adicionales: Optional[str] = None
    leida: bool
    fecha_lectura: Optional[datetime] = None
    fecha_creacion: datetime

    model_config = {"from_attributes": True}