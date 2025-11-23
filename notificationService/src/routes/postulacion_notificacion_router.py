from fastapi import APIRouter, Depends, status
from sqlmodel import Session
from typing import Dict

from ..routes.deps.db_session import get_db
from ..routes.deps.synapse_session import get_synapse_session
from ..services.postulacion_notificacion_service import PostulacionNotificacionService
from ..repositories.notificacion_repo import NotificacionRepository
from ..repositories.convocatoria_snapshot_repo import ConvocatoriaSnapshotRepository
from ..repositories.analytic_repo import NotificacionAnalyticsRepository


router = APIRouter(
    prefix="/procesamiento",
    tags=["Procesamiento Automático"]
)


def get_postulacion_service(
    session: Session = Depends(get_db),
    synapse_session: Session = Depends(get_synapse_session)
) -> PostulacionNotificacionService:
    """Dependencia para inyectar el servicio de postulaciones"""
    notif_repo = NotificacionRepository(session)
    snapshot_repo = ConvocatoriaSnapshotRepository(session)
    analytics_repo = NotificacionAnalyticsRepository(synapse_session)
    
    return PostulacionNotificacionService(
        notif_repo,
        snapshot_repo,
        analytics_repo
    )


@router.post(
    "/notificar-postulaciones",
    response_model=Dict,
    status_code=status.HTTP_200_OK,
    summary="Procesar y notificar nuevas postulaciones",
    description="""
    Procesa todas las convocatorias activas y crea notificaciones cuando detecta
    incrementos en el número de postulaciones.
    
    **Cómo funciona:**
    1. Consulta la vista agregada en Synapse que tiene el total de postulados por convocatoria
    2. Compara con el último snapshot guardado
    3. Si hay incremento, crea una notificación para la empresa
    4. Actualiza los snapshots con los valores actuales
    
    **Ejemplo de uso:**
    - Llamar este endpoint cada hora desde un scheduler
    - El frontend consulta `/notificaciones/{id_empresa}/company/all` para mostrar las nuevas
    """
)
def procesar_notificaciones_postulaciones(
    session: Session = Depends(get_db),
    service: PostulacionNotificacionService = Depends(get_postulacion_service)
):
    """
    Endpoint principal para procesar postulaciones y crear notificaciones.
    
    Returns:
        Resumen con cantidad de notificaciones creadas y detalle por convocatoria
    """
    resultado = service.procesar_nuevas_postulaciones(session)
    return resultado


@router.get(
    "/resumen-convocatorias",
    response_model=Dict,
    status_code=status.HTTP_200_OK,
    summary="Obtener resumen del estado de convocatorias",
    description="""
    Obtiene un resumen del estado actual de todas las convocatorias activas
    y sus snapshots guardados. Útil para debugging y monitoreo.
    """
)
def obtener_resumen_convocatorias(
    session: Session = Depends(get_db),
    service: PostulacionNotificacionService = Depends(get_postulacion_service)
):
    """
    Obtiene información sobre convocatorias activas y snapshots.
    """
    return service.obtener_resumen_convocatorias(session)


@router.get(
    "/estadisticas-snapshots",
    response_model=Dict,
    status_code=status.HTTP_200_OK,
    summary="Obtener estadísticas de snapshots guardados"
)
def obtener_estadisticas_snapshots(
    session: Session = Depends(get_db)
):
    """
    Obtiene estadísticas sobre los snapshots de convocatorias guardados.
    """
    from sqlmodel import select, func, col
    from ..models.convocatoria_snapshot import ConvocatoriaSnapshot
    
    # Total de snapshots
    stmt_total = select(func.count()).select_from(ConvocatoriaSnapshot)
    total = session.exec(stmt_total).one()
    
    # Snapshots por empresa - usar col() para forzar tipo correcto
    stmt_por_empresa = (
        select(
            col(ConvocatoriaSnapshot.id_empresa),
            func.count().label('total')
        )
        .select_from(ConvocatoriaSnapshot)
        .group_by(col(ConvocatoriaSnapshot.id_empresa))
        .order_by(func.count().desc())
        .limit(10)
    )
    por_empresa = session.exec(stmt_por_empresa).all()
    
    return {
        "total_snapshots": total,
        "top_empresas": [
            {"id_empresa": row[0], "convocatorias_activas": row[1]}
            for row in por_empresa
        ]
    }


@router.delete(
    "/limpiar-snapshots-inactivos",
    status_code=status.HTTP_200_OK,
    summary="Limpiar snapshots de convocatorias inactivas",
    description="""
    Elimina snapshots de convocatorias que ya no están en la vista activa.
    Útil para mantener la tabla limpia.
    """
)
def limpiar_snapshots_inactivos(
    session: Session = Depends(get_db),
    synapse_session: Session = Depends(get_synapse_session)
):
    """
    Limpia snapshots de convocatorias que ya no están activas.
    """
    from ..repositories.convocatoria_snapshot_repo import ConvocatoriaSnapshotRepository
    from ..repositories.analytic_repo import NotificacionAnalyticsRepository
    
    snapshot_repo = ConvocatoriaSnapshotRepository(session)
    analytics_repo = NotificacionAnalyticsRepository(synapse_session)
    
    # Obtener IDs de convocatorias activas
    convocatorias_activas = analytics_repo.get_postulados_por_convocatoria()
    ids_activos = {conv['id_convocatoria'] for conv in convocatorias_activas}
    
    # Obtener todos los snapshots
    todos_snapshots = snapshot_repo.get_all_snapshots()
    
    # Eliminar los que ya no están activos
    eliminados = 0
    for snapshot in todos_snapshots:
        if snapshot.id_convocatoria not in ids_activos:
            snapshot_repo.eliminar_snapshot(snapshot.id_convocatoria)
            eliminados += 1
    
    return {
        "mensaje": f"Se limpiaron {eliminados} snapshots de convocatorias inactivas",
        "snapshots_eliminados": eliminados,
        "snapshots_restantes": len(todos_snapshots) - eliminados
    }