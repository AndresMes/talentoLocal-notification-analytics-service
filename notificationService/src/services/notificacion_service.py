from sqlmodel import Session
from typing import List
from uuid import UUID  
from datetime import datetime
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
    
    def listar_dado_id_usuario(self, session: Session, id_usuario:int) -> List[NotificacionResponseDTO]:
        
        # Poner validación de ID cuando se tenga acceso
        results = self.notificacionRepository.get_by_id_usuario(session, id_usuario)
        return [NotificacionResponseDTO.model_validate(e) for e in results]
    
    def listar_dado_id_empresa(self, session: Session, id_empresa:int) -> List[NotificacionResponseDTO]:
        
        # Poner validación de ID cuando se tenga acceso
        results = self.notificacionRepository.get_by_id_empresa(session, id_empresa)
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
    
    def marcar_todas_leidas_usuario(self, session: Session, id_usuario: int) -> dict:
        """Marcar todas las notificaciones de un usuario como leídas"""
        notificaciones = self.notificacionRepository.get_no_leidas_by_usuario(session, id_usuario)
        
        if not notificaciones:
            return {
                "mensaje": "No hay notificaciones sin leer para este usuario",
                "cantidad_actualizada": 0
            }
        
        fecha_actual = datetime.now()
        for notificacion in notificaciones:
            notificacion.leida = True
            notificacion.fecha_lectura = fecha_actual
        
        self.notificacionRepository.update_many(session, notificaciones)
        
        return {
            "mensaje": f"Se marcaron {len(notificaciones)} notificaciones como leídas",
            "cantidad_actualizada": len(notificaciones)
        }

    def marcar_todas_leidas_empresa(self, session: Session, id_empresa: int) -> dict:
        """Marcar todas las notificaciones de una empresa como leídas"""
        notificaciones = self.notificacionRepository.get_no_leidas_by_empresa(session, id_empresa)
        
        if not notificaciones:
            return {
                "mensaje": "No hay notificaciones sin leer para esta empresa",
                "cantidad_actualizada": 0
            }
        
        fecha_actual = datetime.now()
        for notificacion in notificaciones:
            notificacion.leida = True
            notificacion.fecha_lectura = fecha_actual
        
        self.notificacionRepository.update_many(session, notificaciones)
        
        return {
            "mensaje": f"Se marcaron {len(notificaciones)} notificaciones como leídas",
            "cantidad_actualizada": len(notificaciones)
        }

    def delete(self, session: Session, id_notificacion: UUID) -> None:  # UUID
        entidad = self.notificacionRepository.get_by_id(session, id_notificacion)
        if not entidad:
            raise NotificacionNotFound(f"Notificación {id_notificacion} no encontrada.")
        
        self.notificacionRepository.delete(session, entidad)