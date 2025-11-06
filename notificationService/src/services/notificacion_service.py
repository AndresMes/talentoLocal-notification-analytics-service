from sqlmodel import Session
from typing import List
from uuid import UUID  
from ..repositories.notificacion_repo import NotificacionRepository
from ..dto.notificacion_dto import NotificacionCreateDTO, NotificacionResponseDTO
from ..models.notificacion import Notificacion
from ..exception.notificacion_not_found import NotificacionNotFound 

class NotificacionService:
    def __init__(self, notificacionRepository: NotificacionRepository):
        self.notificacionRepository = notificacionRepository
    
    def get_by_id(self, session: Session, id_notificacion: UUID) -> NotificacionResponseDTO:  # UUID en lugar de int
        entidad = self.notificacionRepository.get_by_id(session, id_notificacion)
        if not entidad:
            raise NotificacionNotFound(f"Notificación {id_notificacion} no encontrada.")
        return NotificacionResponseDTO.model_validate(entidad)

    def listar_todas(self, session: Session, limit: int = 100, offset: int = 0) -> List[NotificacionResponseDTO]:
        results = self.notificacionRepository.list_all(session, offset, limit)
        return [NotificacionResponseDTO.model_validate(e) for e in results]

    def listar_no_leidas(self, session: Session) -> List[NotificacionResponseDTO]:
        results = self.notificacionRepository.get_by_status(session)
        return [NotificacionResponseDTO.model_validate(e) for e in results]

    def create(self, session: Session, notificacionDto: NotificacionCreateDTO) -> NotificacionResponseDTO:
        notificacion = Notificacion(**notificacionDto.model_dump())
        nueva_notificacion = self.notificacionRepository.create(session, notificacion)
        return NotificacionResponseDTO.model_validate(nueva_notificacion)

    def update(self, session: Session, id_notificacion: UUID, notificacionDto: NotificacionCreateDTO) -> NotificacionResponseDTO:  # UUID
        entidad = self.notificacionRepository.get_by_id(session, id_notificacion)
        if not entidad:
            raise NotificacionNotFound(f"Notificación {id_notificacion} no encontrada.")
        
        for key, value in notificacionDto.model_dump(exclude_unset=True).items():
            setattr(entidad, key, value)
        
        notificacion_actualizada = self.notificacionRepository.update(session, entidad)
        return NotificacionResponseDTO.model_validate(notificacion_actualizada)

    def marcar_como_leida(self, session: Session, id_notificacion: UUID) -> NotificacionResponseDTO:  # UUID
        from datetime import datetime
        
        entidad = self.notificacionRepository.get_by_id(session, id_notificacion)
        if not entidad:
            raise NotificacionNotFound(f"Notificación {id_notificacion} no encontrada.")
        
        entidad.leida = True
        entidad.fecha_lectura = datetime.now()
        
        notificacion_actualizada = self.notificacionRepository.update(session, entidad)
        return NotificacionResponseDTO.model_validate(notificacion_actualizada)

    def delete(self, session: Session, id_notificacion: UUID) -> None:  # UUID
        entidad = self.notificacionRepository.get_by_id(session, id_notificacion)
        if not entidad:
            raise NotificacionNotFound(f"Notificación {id_notificacion} no encontrada.")
        
        self.notificacionRepository.delete(session, entidad)