from sqlmodel import select, Session
from typing import List, Optional
from uuid import UUID
from ..models.notificacion import Notificacion

class NotificacionRepository:
    def __init__(self, session: Session):
        self.session = session
    
    ## FUNCIONES DE OBTENER

    def get_by_id(self, session: Session, id_: UUID) -> Optional[Notificacion]:
        return session.get(Notificacion, id_)
    
    def get_by_id_usuario(self, session:Session, id_usuario: int) -> List[Notificacion]:
        stmt = select(Notificacion).where(Notificacion.id_usuario == id_usuario)
        results = session.exec(stmt)
        return results.all()
    
    def get_by_id_empresa(self, session:Session, id_empresa: int) -> List[Notificacion]:
        stmt = select(Notificacion).where(Notificacion.id_empresa == id_empresa)
        results = session.exec(stmt)
        return results.all()
    
    def get_no_leidas_by_usuario(self, session: Session, id_usuario: int) -> List[Notificacion]:
        """Obtener notificaciones no leídas de un usuario"""
        stmt = (
            select(Notificacion)
            .where(Notificacion.id_usuario == id_usuario)
            .where(Notificacion.leida == False)
            .order_by(Notificacion.fecha_creacion.desc())
        )
        results = session.exec(stmt)
        return results.all()

    def get_no_leidas_by_empresa(self, session: Session, id_empresa: int) -> List[Notificacion]:
        """Obtener notificaciones no leídas de una empresa"""
        stmt = (
            select(Notificacion)
            .where(Notificacion.id_empresa == id_empresa)
            .where(Notificacion.leida == False)
            .order_by(Notificacion.fecha_creacion.desc())
        )
        results = session.exec(stmt)
        return results.all()

    def list_all(self, session: Session, skip: int = 0, limit: int = 100) -> List[Notificacion]:
        stmt = select(Notificacion).order_by(Notificacion.fecha_creacion.desc()).offset(skip).limit(limit)
        return session.exec(stmt).all()

    def get_by_status(self, session: Session) -> List[Notificacion]:
        stmt = select(Notificacion).where(Notificacion.leida == False)
        results = session.exec(stmt)
        return results.all()


    # FUNCIONES POST 

    def create(self, session: Session, notificacion: Notificacion) -> Notificacion:
        session.add(notificacion)
        session.commit()
        session.refresh(notificacion)
        return notificacion

    #FUNCIONES PUT/PATCH

    def update(self, session: Session, notificacion: Notificacion) -> Notificacion:
        session.add(notificacion)
        session.commit()
        session.refresh(notificacion)
        return notificacion
    
    def update_many(self, session: Session, notificaciones: List[Notificacion]) -> None:
        """Actualizar múltiples notificaciones"""
        for notificacion in notificaciones:
            session.add(notificacion)
        session.commit()


    #FUNCIONES DELETE
    
    def delete(self, session: Session, notificacion: Notificacion) -> None:
        session.delete(notificacion)
        session.commit()