from fastapi import APIRouter
from ..models import TipoNotificacion
from ..dto.tipo_notificacion_dto import TipoNotificacionCreateDTO, TipoNotificacionUpdateDTO, TipoNotificacionResponseDTO
from .deps.db_session import SessionDep

tipo_notificacion_router = APIRouter(prefix = "/tipo-notificaciones", tags=["tipo-notificaciones"])