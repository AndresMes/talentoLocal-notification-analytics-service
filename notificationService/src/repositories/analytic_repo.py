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
    