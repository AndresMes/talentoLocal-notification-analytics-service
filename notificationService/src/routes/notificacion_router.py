from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlmodel import Session
from uuid import UUID
from typing import List
from .deps.db_session import get_db  # Ajusta según tu configuración de BD
from ..services.notificacion_service import NotificacionService
from ..repositories.notificacion_repo import NotificacionRepository
from ..dto.notificacion_dto import NotificacionCreateDTO, NotificacionResponseDTO
from ..exception.notificacion_not_found import NotificacionNotFound

router = APIRouter(
    prefix="/notificaciones",
    tags=["Notificaciones"]
)

# Dependencia para inyectar el servicio
def get_notificacion_service(session: Session = Depends(get_db)) -> NotificacionService:
    repository = NotificacionRepository(session)
    return NotificacionService(repository)


@router.get("/", response_model=List[NotificacionResponseDTO], status_code=status.HTTP_200_OK)
def listar_notificaciones(
    limit: int = Query(default=100, le=100, ge=1),
    offset: int = Query(default=0, ge=0),
    session: Session = Depends(get_db),
    service: NotificacionService = Depends(get_notificacion_service)
):
    """
    Listar todas las notificaciones con paginación
    """
    return service.listar_todas(session, limit, offset)


@router.get("/no-leidas", response_model=List[NotificacionResponseDTO], status_code=status.HTTP_200_OK)
def listar_notificaciones_no_leidas(
    session: Session = Depends(get_db),
    service: NotificacionService = Depends(get_notificacion_service)
):
    """
    Listar solo las notificaciones no leídas
    """
    return service.listar_no_leidas(session)


@router.get("/{id_notificacion}", response_model=NotificacionResponseDTO, status_code=status.HTTP_200_OK)
def obtener_notificacion(
    id_notificacion: UUID,
    session: Session = Depends(get_db),
    service: NotificacionService = Depends(get_notificacion_service)
):
    """
    Obtener una notificación por su ID
    """
    try:
        return service.get_by_id(session, id_notificacion)
    except NotificacionNotFound as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e)
        )


@router.post("/", response_model=NotificacionResponseDTO, status_code=status.HTTP_201_CREATED)
def crear_notificacion(
    notificacion: NotificacionCreateDTO,
    session: Session = Depends(get_db),
    service: NotificacionService = Depends(get_notificacion_service)
):
    """
    Crear una nueva notificación
    """
    return service.create(session, notificacion)


@router.delete("/{id_notificacion}", status_code=status.HTTP_204_NO_CONTENT)
def eliminar_notificacion(
    id_notificacion: UUID,
    session: Session = Depends(get_db),
    service: NotificacionService = Depends(get_notificacion_service)
):
    """
    Eliminar una notificación
    """
    try:
        service.delete(session, id_notificacion)
        return None
    except NotificacionNotFound as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e)
        )