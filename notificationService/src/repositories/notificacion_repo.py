from sqlmodel import select, Session
from typing import List, Optional
from uuid import UUID
from ..models.notificacion import Notificacion

class NotificacionRepository:
    def __init__(self, session: Session):
        self.session = session
    
    def get_by_id(self, session: Session, id_: UUID) -> Optional[Notificacion]:
        return session.get(Notificacion, id_)

    def list_all(self, session: Session, skip: int = 0, limit: int = 100) -> List[Notificacion]:
        stmt = select(Notificacion).order_by(Notificacion.fecha_creacion.desc()).offset(skip).limit(limit)
        return session.exec(stmt).all()

    def get_by_status(self, session: Session) -> List[Notificacion]:
        stmt = select(Notificacion).where(Notificacion.leida == False)
        results = session.exec(stmt)
        return results.all()

    def create(self, session: Session, notificacion: Notificacion) -> Notificacion:
        session.add(notificacion)
        session.commit()
        session.refresh(notificacion)
        return notificacion

    def update(self, session: Session, notificacion: Notificacion) -> Notificacion:
        session.add(notificacion)
        session.commit()
        session.refresh(notificacion)
        return notificacion

    def delete(self, session: Session, notificacion: Notificacion) -> None:
        session.delete(notificacion)
        session.commit()