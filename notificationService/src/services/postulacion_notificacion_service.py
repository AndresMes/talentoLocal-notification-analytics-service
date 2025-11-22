from sqlmodel import Session
from typing import List, Dict, Any, Optional
from datetime import datetime

from ..repositories.notificacion_repo import NotificacionRepository
from ..repositories.convocatoria_snapshot_repo import ConvocatoriaSnapshotRepository
from ..repositories.analytic_repo import NotificacionAnalyticsRepository
from ..models.notificacion import Notificacion
from ..dto.postulacion_dto import IncrementoPostulacionesDTO
from ..models.notificacionInt import NotificacionInt

PRIORIDAD_MAP = {
    "BAJA": 1,
    "MEDIA": 2,
    "ALTA": 3
}

class PostulacionNotificacionService:
    def __init__(
        self,
        notificacion_repo: NotificacionRepository,
        snapshot_repo: ConvocatoriaSnapshotRepository,
        analytics_repo: NotificacionAnalyticsRepository
    ):
        self.notificacion_repo = notificacion_repo
        self.snapshot_repo = snapshot_repo
        self.analytics_repo = analytics_repo
    
    def procesar_nuevas_postulaciones(self, session: Session) -> Dict[str, Any]:
        convocatorias_actuales = self.analytics_repo.get_postulados_por_convocatoria()
        
        if not convocatorias_actuales:
            return {
                "mensaje": "No hay convocatorias activas para procesar",
                "notificaciones_creadas": 0,
                "convocatorias_procesadas": 0
            }

        snapshots_previos = {
            s.id_convocatoria: s 
            for s in self.snapshot_repo.get_all_snapshots()
        }
        
        incrementos = self._detectar_incrementos(
            convocatorias_actuales, 
            snapshots_previos
        )
        
        notificaciones_creadas = 0
        detalles = []
        
        for incremento in incrementos:
            if incremento.nuevas_postulaciones > 0:
                notificacion = self._crear_notificacion_incremento(incremento)
                
                if notificacion:
                    notificaciones_creadas += 1
                    detalles.append({
                        "id_convocatoria": incremento.id_convocatoria,
                        "titulo": incremento.titulo,
                        "nuevas_postulaciones": incremento.nuevas_postulaciones,
                        "total_actual": incremento.total_actual
                    })
        
        self._actualizar_snapshots(convocatorias_actuales)
        
        return {
            "mensaje": f"Se procesaron {len(convocatorias_actuales)} convocatorias activas",
            "notificaciones_creadas": notificaciones_creadas,
            "convocatorias_procesadas": len(convocatorias_actuales),
            "convocatorias_con_incremento": len([i for i in incrementos if i.nuevas_postulaciones > 0]),
            "detalle": detalles
        }
    
    def _detectar_incrementos(
        self, 
        convocatorias_actuales: List[Dict],
        snapshots_previos: Dict[int, Any]
    ) -> List[IncrementoPostulacionesDTO]:
        incrementos = []
        
        for conv in convocatorias_actuales:
            id_conv = conv['id_convocatoria']
            total_actual = conv['total_postulados']
            
            if id_conv in snapshots_previos:
                total_anterior = snapshots_previos[id_conv].total_postulados
                nuevas = max(0, total_actual - total_anterior)
            else:
                # Regla de negocio: Notificar todo en la primera ejecución
                total_anterior = 0
                nuevas = total_actual
            
            incrementos.append(IncrementoPostulacionesDTO(
                id_empresa=conv['id_empresa'],
                id_convocatoria=id_conv,
                titulo=conv['titulo'],
                total_anterior=total_anterior,
                total_actual=total_actual,
                nuevas_postulaciones=nuevas
            ))
        
        return incrementos
    
    def _crear_notificacion_incremento(
        self, 
        incremento: IncrementoPostulacionesDTO
    ) -> NotificacionInt | None:
        
        cantidad = incremento.nuevas_postulaciones
        titulo = incremento.titulo
        
        if cantidad == 1:
            mensaje = f"Tienes 1 nueva postulación en '{titulo}'. Total: {incremento.total_actual}"
        else:
            mensaje = f"Tienes {cantidad} nuevas postulaciones en '{titulo}'. Total: {incremento.total_actual}"
        
        notificacion = NotificacionInt(
            id_usuario=0, 
            id_empresa=incremento.id_empresa,
            tipo_notificacion="NUEVA_POSTULACION",
            asunto=f"Nuevas postulaciones en {titulo}",
            mensaje=mensaje,
            id_oferta=incremento.id_convocatoria, 
            prioridad=PRIORIDAD_MAP.get("MEDIA", 2),
            datos_adicionales=f"nuevas:{cantidad},total:{incremento.total_actual}",
            leida=False
        )
        
        # Llama al método create_ que gestiona su propia sesión
        return self.notificacion_repo.create_(notificacion)
    
    def _actualizar_snapshots(self, convocatorias_actuales: List[Dict]) -> None:
        snapshots_data = [
            {
                'id_empresa': conv['id_empresa'],
                'id_convocatoria': conv['id_convocatoria'],
                'titulo': conv['titulo'],
                'total_postulados': conv['total_postulados']
            }
            for conv in convocatorias_actuales
        ]
        
        self.snapshot_repo.actualizar_multiples_snapshots(snapshots_data)
    
    def obtener_resumen_convocatorias(self, session: Session) -> Dict[str, Any]:
        """
        Obtiene un resumen del estado actual de todas las convocatorias activas.
        Útil para debugging y monitoreo.
        """
        convocatorias_actuales = self.analytics_repo.get_postulados_por_convocatoria()
        snapshots = self.snapshot_repo.get_all_snapshots()
        
        return {
            "convocatorias_activas": len(convocatorias_actuales),
            "snapshots_guardados": len(snapshots),
            "convocatorias": [
                {
                    "id_convocatoria": conv['id_convocatoria'],
                    "titulo": conv['titulo'],
                    "total_postulados": conv['total_postulados'],
                    "id_empresa": conv['id_empresa']
                }
                for conv in convocatorias_actuales
            ]
        }