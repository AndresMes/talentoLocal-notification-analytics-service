from sqlmodel import select, Session
from typing import List, Optional
from ..models.tipo_notificacion import TipoNotificacion

def get_by_id(session: Session, id_: int) -> Optional[TipoNotificacion]:
    return session.get(TipoNotificacion, id_)

def get_by_codigo(session: Session, codigo: str) -> Optional[TipoNotificacion]:
    stmt = select(TipoNotificacion).where(TipoNotificacion.codigo == codigo)
    return session.exec(stmt).first()

def list_all(session: Session, skip: int = 0, limit: int = 100) -> List[TipoNotificacion]:
    stmt = select(TipoNotificacion).offset(skip).limit(limit)
    return session.exec(stmt).all()

def create(session: Session, tipo: TipoNotificacion) -> TipoNotificacion:
    session.add(tipo)
    session.commit()
    session.refresh(tipo)
    return tipo

def update(session: Session, tipo: TipoNotificacion) -> TipoNotificacion:
    session.add(tipo)
    session.commit()
    session.refresh(tipo)
    return tipo

def delete(session: Session, tipo: TipoNotificacion) -> None:
    session.delete(tipo)
    session.commit()