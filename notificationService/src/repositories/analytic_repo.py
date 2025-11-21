from sqlmodel import Session, text
from typing import List, Dict, Any
from datetime import datetime, timedelta

class NotificacionAnalyticsRepository:
    """
    Repositorio para análisis de notificaciones en Azure Synapse Analytics.
    Orientado a consultas de lectura pesadas y análisis de datos históricos.
    """
    
    def __init__(self, session: Session):
        self.session = session
    

    def get_postulados_por_convocatoria(
        self, 
    ) -> List[Dict[str, Any]]:
        """
        Obtener distribución de notificaciones por tipo.
        """
        query = text("""
            SELECT 
                id_empresa,
                id_convocatoria,
                titulo,
                total_postulados
            FROM postulados_por_convocatoria
        """)
        
        results = self.session.exec(query).all() #type: ignore
        
        return [
            {
                "id_empresa": row[0],
                "id_convocatoria": row[1],
                "titulo": row[2],
                "total_postulados": row[3]
            }
            for row in results
        ]
    def get_cant_empleos_publicados(
        self,
    ) -> int:
        """
        Obtener la cantidad de empleos (ofertas) publicadas
        """
        query = text("""
            SELECT COUNT(id) as cantidad_ofertas
            FROM ofertas                
            WHERE closing_date IS NULL
        """)

        results = self.session.exec(query).scalar() # type: ignore

        return results or 0
    
    def get_cant_empresas(
        self,
    ) -> int:
        """
        Obtener la cantidad de empresas activas
        """
        query = text("""
            SELECT COUNT(empresa_id) as cantidad_empresas
            FROM mock_empresas
        """)

        results = self.session.exec(query).scalar() # type: ignore

        return results or 0
    
    def get_cant_usuarios(
        self,
    ) -> int:
        """
        Obtener la cantidad de usuarios
        """
        query = text("""
            SELECT COUNT(usuario_id) as cantidad_usuarios
            FROM mock_usuarios
        """)

        results = self.session.exec(query).scalar() # type: ignore

        return results or 0
    
    