from sqlmodel import Session, select
from typing import List, Dict, Optional
from datetime import datetime
from ..models.convocatoria_snapshot import ConvocatoriaSnapshot

class ConvocatoriaSnapshotRepository:
    """Repositorio para gestionar snapshots de conteos de postulaciones"""

    def __init__(self, session:Session) -> None:
        self.session = session

    def get_snapshot(self, id_convocatoria:int) -> Optional[ConvocatoriaSnapshot]:
        """
        Obtiene el snapshot más reciente de una convocatoria

        Args:
            id_convocatoria: ID de la convocatoria

        Returns:
            Snapshot si existe, None si no
        """
        stmt = select(ConvocatoriaSnapshot).where(
            ConvocatoriaSnapshot.id_convocatoria == id_convocatoria
        )

        return self.session.exec(stmt).first()
    
    def get_all_snapshots(self) -> List[ConvocatoriaSnapshot]:
        """Obtiene todos los snapshots guardados"""
        stmt = select(ConvocatoriaSnapshot)
        return list(self.session.exec(stmt).all())
    
    def get_snapshots_por_empresa(self, id_empresa: str) -> List[ConvocatoriaSnapshot]:
        """Obtiene todos los snapshots de una empresa"""
        stmt = select(ConvocatoriaSnapshot).where(
            ConvocatoriaSnapshot.id_empresa == id_empresa
        )
        return list(self.session.exec(stmt).all())
    
    def crear_o_actualizar_sanpshot(
            self,
            id_empresa: str,
            id_convocatoria: int,
            titulo: str,
            total_postulados: int
    ) -> ConvocatoriaSnapshot:
        """
        Crea o actualiza el snapshot de una convocatoria

        Args:
            id_empresa: ID de la empresa
            id_convocatoria: ID de la convocatoria
            titulo: Título de la convocatoria
            total_postulados: Total actual de postulados

        Returns:
            Snapshot creado o actualizado
        """
        snapshot = self.get_snapshot(id_convocatoria)

        if snapshot:
            snapshot.total_postulados = total_postulados
            snapshot.titulo = titulo 
            snapshot.ultima_actualizacion = datetime.utcnow()
            self.session.add(snapshot)
        else:
            snapshot = ConvocatoriaSnapshot(
                id_empresa=id_empresa,
                id_convocatoria=id_convocatoria,
                titulo = titulo,
                total_postulados=total_postulados
            )
            self.session.add(snapshot)
        
        self.session.commit()
        self.session.refresh(snapshot)
        return snapshot
    
    def actualizar_multiples_snapshots(
            self,
            snapshots_data: List[Dict]
    ) -> List[ConvocatoriaSnapshot]:
        """
        Actualiza múltiples snapshots en batch

        Args:
            snapshots_data = Lista de dicts con id_empresa, id_convocatoria, titulo, total_postulados

        Returns:
            Lista de snapshots actualizados
        """

        resultados = []

        for data in snapshots_data:
            snapshot = self.crear_o_actualizar_sanpshot(
                id_empresa=data['id_empresa'],
                id_convocatoria=data['id_convocatoria'],
                titulo=data['titulo'],
                total_postulados=data['total_postulados']
            )

        return resultados
    
    def eliminar_snapshot(self, id_convocatoria: int) -> bool:
        """
        Elimina un snapshot (útil cuando una convocatoria ya no está activa)

        Args:
            id_convocatoria: ID de la convocatoria

        Returns:
            True si se eliminó, False si no exisitía
        """
        snapshot = self.get_snapshot(id_convocatoria)

        if snapshot:
            self.session.delete(snapshot)
            self.session.commit()
            return True
        return False