from sqlmodel import Session, select
from typing import List, Optional, Set
from ..models.oferta_notificada import OfertaNotificada


class OfertaNotificadaRepository:
    """Repositorio para gestionar el tracking de ofertas notificadas"""
    
    def __init__(self, session: Session):
        self.session = session
    
    def get_oferta_notificada(self, id_oferta: int) -> Optional[OfertaNotificada]:
        """
        Verifica si una oferta ya fue notificada.
        
        Args:
            id_oferta: ID de la oferta
            
        Returns:
            Registro de oferta notificada o None
        """
        stmt = select(OfertaNotificada).where(
            OfertaNotificada.id_oferta == id_oferta
        )
        return self.session.exec(stmt).first()
    
    def get_ids_ya_notificados(self, ids_ofertas: List[int] | int) -> Set[int]:
        """
        Obtiene los IDs de ofertas que ya fueron notificadas.
        
        Args:
            ids_ofertas: Lista de IDs a verificar o un solo ID
            
        Returns:
            Set de IDs que ya fueron notificados
        """
        if not ids_ofertas:
            return set()
        
        # Normalizar: si es int, convertir a lista
        if isinstance(ids_ofertas, int):
            ids_ofertas = [ids_ofertas]
        
        from sqlmodel import col
        
        stmt = select(OfertaNotificada.id_oferta).where(
            col(OfertaNotificada.id_oferta).in_(ids_ofertas)
        )
        results = self.session.exec(stmt).all()
        return set(results)
    
    def marcar_como_notificada(
        self,
        id_oferta: int,
        id_empresa: str,  # UUID como string
        titulo: str,
        fecha_publicacion,
        usuarios_notificados: int
    ) -> OfertaNotificada:
        """
        Marca una oferta como notificada.
        
        Args:
            id_oferta: ID de la oferta
            id_empresa: ID de la empresa
            titulo: Título de la oferta
            fecha_publicacion: Fecha de publicación
            usuarios_notificados: Cantidad de usuarios notificados
            
        Returns:
            Registro creado
        """
        registro = OfertaNotificada(
            id_oferta=id_oferta,
            id_empresa=id_empresa,
            titulo=titulo,
            fecha_publicacion=fecha_publicacion,
            usuarios_notificados=usuarios_notificados
        )
        self.session.add(registro)
        self.session.commit()
        self.session.refresh(registro)
        return registro
    
    def get_all(self) -> List[OfertaNotificada]:
        """Obtiene todas las ofertas notificadas"""
        stmt = select(OfertaNotificada)
        return list(self.session.exec(stmt).all())