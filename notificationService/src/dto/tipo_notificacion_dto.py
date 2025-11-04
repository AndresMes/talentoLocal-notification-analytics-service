from typing import Optional
from pydantic import BaseModel


class TipoNotificacionCreateDTO(BaseModel):
    codigo: str
    nombre: str
    descripcion: Optional[str] = None
    plantilla_asunto: Optional[str] = None
    plantilla_mensaje: Optional[str] = None
    activo: bool = True

class TipoNotificacionUpdateDTO(TipoNotificacionCreateDTO):
    pass

class TipoNotificacionResponseDTO(TipoNotificacionCreateDTO):
    id :str
