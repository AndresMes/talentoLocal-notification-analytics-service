from fastapi import APIRouter, Depends, Query, status
from sqlmodel import Session
from typing import Dict

from ..routes.deps.db_session import get_db
from ..routes.deps.synapse_session import get_synapse_session
from ..services.oferta_notificacion_service import OfertaNotificacionService
from ..repositories.notificacion_repo import NotificacionRepository
from ..repositories.oferta_notificada_repo import OfertaNotificadaRepository
from ..repositories.oferta_analitycs_repo import OfertaAnalyticsRepository


router = APIRouter(
    prefix="/procesamiento",
    tags=["Procesamiento Automático"]
)


def get_oferta_service(
    session: Session = Depends(get_db),
    synapse_session: Session = Depends(get_synapse_session)
) -> OfertaNotificacionService:
    """Dependencia para inyectar el servicio de ofertas"""
    notif_repo = NotificacionRepository(session)
    oferta_notif_repo = OfertaNotificadaRepository(session)
    oferta_analytics_repo = OfertaAnalyticsRepository(synapse_session)
    
    return OfertaNotificacionService(
        notif_repo,
        oferta_notif_repo,
        oferta_analytics_repo
    )


@router.post(
    "/notificar-ofertas-compatibles",
    response_model=Dict,
    status_code=status.HTTP_200_OK,
    summary="Notificar a usuarios sobre ofertas compatibles",
    description="""
    Procesa ofertas recientes y notifica a usuarios cuyos perfiles coincidan con los requisitos.
    
    **Cómo funciona:**
    1. Consulta ofertas activas recientes desde Synapse (últimos X días)
    2. Extrae las skills de los requirements de cada oferta
    3. Llama al API de perfiles para obtener usuarios con esas skills
    4. Crea notificaciones para cada usuario compatible
    5. Marca la oferta como procesada para evitar duplicados
    
    **Ejemplo de uso:**
    - Ejecutar diariamente (ej: cada 24 horas)
    - Los usuarios ven notificaciones en `/notificaciones/{id_usuario}/user/all`
    """
)
def notificar_ofertas_compatibles(
    dias_atras: int = Query(
        default=7,
        ge=1,
        le=30,
        description="Ventana de tiempo en días para buscar ofertas nuevas (1-30 días)"
    ),
    session: Session = Depends(get_db),
    service: OfertaNotificacionService = Depends(get_oferta_service)
):
    """
    Endpoint para procesar ofertas y notificar a usuarios compatibles.
    
    Args:
        dias_atras: Días hacia atrás para buscar ofertas
        session: Sesión de BD
        service: Servicio de procesamiento
        
    Returns:
        Resumen con notificaciones creadas
    """
    resultado = service.procesar_nuevas_ofertas(session, dias_atras)
    return resultado


@router.get(
    "/estadisticas-ofertas-notificadas",
    response_model=Dict,
    status_code=status.HTTP_200_OK,
    summary="Obtener estadísticas de ofertas notificadas"
)
def obtener_estadisticas_ofertas(
    session: Session = Depends(get_db)
):
    """
    Obtiene estadísticas sobre ofertas notificadas.
    """
    from sqlmodel import select, func, col
    from ..models.oferta_notificada import OfertaNotificada
    
    # Total de ofertas notificadas
    stmt_total = select(func.count()).select_from(OfertaNotificada)
    total = session.exec(stmt_total).one()
    
    # Total de usuarios notificados (suma)
    stmt_usuarios = select(func.sum(col(OfertaNotificada.usuarios_notificados)))
    total_usuarios = session.exec(stmt_usuarios).one() or 0
    
    # Top ofertas por usuarios notificados
    stmt_top = (
        select(
            col(OfertaNotificada.id_oferta),
            col(OfertaNotificada.titulo),
            col(OfertaNotificada.usuarios_notificados)
        )
        .order_by(col(OfertaNotificada.usuarios_notificados).desc())
        .limit(10)
    )
    top_ofertas = session.exec(stmt_top).all()
    
    return {
        "total_ofertas_notificadas": total,
        "total_usuarios_notificados": total_usuarios,
        "top_10_ofertas": [
            {
                "id_oferta": row[0],
                "titulo": row[1],
                "usuarios_notificados": row[2]
            }
            for row in top_ofertas
        ]
    }