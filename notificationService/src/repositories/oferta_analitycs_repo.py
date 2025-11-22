from sqlmodel import Session, text
from typing import List, Dict, Any
from datetime import datetime, timedelta


class OfertaAnalyticsRepository:
    """
    Repositorio para consultar ofertas desde Azure Synapse Analytics.
    """
    
    def __init__(self, session: Session):
        self.session = session
    
    def get_ofertas_activas_recientes(self, dias_atras: int = 7) -> List[Dict[str, Any]]:
        """
        Obtiene ofertas activas publicadas recientemente.
        
        Args:
            dias_atras: Ventana de tiempo para buscar ofertas (default 7 días)
            
        Returns:
            Lista de ofertas con toda su información
        """
        fecha_limite = datetime.utcnow() - timedelta(days=dias_atras)
        
        query = text("""
            SELECT 
                id,
                title,
                subtitle,
                description,
                modality,
                salary,
                requeriments,
                benefits,
                years_experience,
                location,
                journey,
                schedule,
                available_places,
                status,
                contract_type,
                payment_type,
                publication_date,
                closing_date,
                company_id,
                category_id
            FROM ofertas_python
            ORDER BY publication_date DESC
        """)
        
        # Usar execute() en lugar de exec() para SQL raw con text()
        result = self.session.execute(
            query, 
            {"fecha_limite": fecha_limite}
        )
        results = result.fetchall()
        
        return [
            {
                "id": row[0],
                "title": row[1],
                "subtitle": row[2],
                "description": row[3],
                "modality": row[4],
                "salary": row[5],
                "requirements": row[6],
                "benefits": row[7],
                "years_experience": row[8],
                "location": row[9],
                "journey": row[10],
                "schedule": row[11],
                "available_places": row[12],
                "status": row[13],
                "contract_type": row[14],
                "payment_type": row[15],
                "publication_date": row[16],
                "closing_date": row[17],
                "company_id": row[18],
                "category_id": row[19]
            }
            for row in results
        ]