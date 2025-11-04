from fastapi import APIRouter, Depends, HTTPException, status
from sqlmodel import Session
from typing import List

from .deps.db_session import get_db
from ..dto.tipo_notificacion_dto import (
    TipoNotificacionCreateDTO,
    TipoNotificacionResponseDTO,
    TipoNotificacionUpdateDTO,
)
from ..services.tipo_notificacion_service import TipoNotificacionService

tipo_notificaciones_router = APIRouter(prefix="/tipo-notificaciones", tags=["tipo_notificaciones"])

def get_service(session: Session = Depends(get_db)) -> TipoNotificacionService:
    return TipoNotificacionService(session)

@tipo_notificaciones_router.get("/", response_model=List[TipoNotificacionResponseDTO])
def list_tipo_notificaciones(service: TipoNotificacionService = Depends(get_service)):
    return service.list()

@tipo_notificaciones_router.get("/{id_}", response_model=TipoNotificacionResponseDTO)
def get_tipo_notificacion(id_: int, service: TipoNotificacionService = Depends(get_service)):
    try:
        return service.get(id_)
    except ValueError:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Tipo no encontrado")

@tipo_notificaciones_router.post("/", response_model=TipoNotificacionResponseDTO, status_code=status.HTTP_201_CREATED)
def create_tipo_notificacion(dto: TipoNotificacionCreateDTO, service: TipoNotificacionService = Depends(get_service)):
    try:
        obj = service.create(dto)
        return obj
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))

@tipo_notificaciones_router.put("/{id_}", response_model=TipoNotificacionResponseDTO)
def update_tipo_notificacion(id_: int, dto: TipoNotificacionUpdateDTO, service: TipoNotificacionService = Depends(get_service)):
    try:
        return service.update(id_, dto)
    except ValueError:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Tipo no encontrado")

@tipo_notificaciones_router.patch("/{id_}/activo", response_model=TipoNotificacionResponseDTO)
def set_active(id_: int, active: bool, service: TipoNotificacionService = Depends(get_service)):
    try:
        return service.set_active(id_, active)
    except ValueError:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Tipo no encontrado")

@tipo_notificaciones_router.delete("/{id_}", status_code=status.HTTP_204_NO_CONTENT)
def delete_tipo_notificacion(id_: int, service: TipoNotificacionService = Depends(get_service)):
    try:
        service.delete(id_)
    except ValueError:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Tipo no encontrado")
