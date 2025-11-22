from sqlmodel import Session
from typing import List, Dict, Any
from datetime import datetime

from ..repositories.notificacion_repo import NotificacionRepository
from ..repositories.convocatoria_snapshot_repo import ConvocatoriaSnapshotRepository
from ..repositories.analytic_repo import NotificacionAnalyticsRepository
from ..models.notificacion import Notificacion
from ..dto.postulacion_dto import IncrementoPostulacionesDTO


class PostulacionNotificacionService:
    """
    Servicio para crear notificaciones automáticas sobre nuevas postulaciones.
    Usa la vista agregada de Synapse para detectar incrementos.
    """
    
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
        """
        Procesa convocatorias activas y crea notificaciones para las que tengan
        nuevas postulaciones desde la última verificación.
        
        Args:
            session: Sesión de base de datos
            
        Returns:
            Resumen del procesamiento con cantidad de notificaciones creadas
        """
        # 1. Obtener conteos actuales desde Synapse
        convocatorias_actuales = self.analytics_repo.get_postulados_por_convocatoria()
        
        if not convocatorias_actuales:
            return {
                "mensaje": "No hay convocatorias activas para procesar",
                "notificaciones_creadas": 0,
                "convocatorias_procesadas": 0
            }
        
        # 2. Obtener snapshots previos
        snapshots_previos = {
            s.id_convocatoria: s 
            for s in self.snapshot_repo.get_all_snapshots()
        }
        
        # 3. Detectar incrementos
        incrementos = self._detectar_incrementos(
            convocatorias_actuales, 
            snapshots_previos
        )
        
        # 4. Crear notificaciones para convocatorias con incrementos
        notificaciones_creadas = 0
        detalles = []
        
        for incremento in incrementos:
            if incremento.tiene_incremento:
                notificacion = self._crear_notificacion_incremento(
                    session, 
                    incremento
                )
                
                if notificacion:
                    notificaciones_creadas += 1
                    detalles.append({
                        "id_convocatoria": incremento.id_convocatoria,
                        "titulo": incremento.titulo,
                        "nuevas_postulaciones": incremento.nuevas_postulaciones,
                        "total_actual": incremento.total_actual
                    })
        
        # 5. Actualizar todos los snapshots con valores actuales
        self._actualizar_snapshots(convocatorias_actuales)
        
        return {
            "mensaje": f"Se procesaron {len(convocatorias_actuales)} convocatorias activas",
            "notificaciones_creadas": notificaciones_creadas,
            "convocatorias_procesadas": len(convocatorias_actuales),
            "convocatorias_con_incremento": len([i for i in incrementos if i.tiene_incremento]),
            "detalle": detalles
        }
    
    def _detectar_incrementos(
        self, 
        convocatorias_actuales: List[Dict],
        snapshots_previos: Dict[int, Any]
    ) -> List[IncrementoPostulacionesDTO]:
        """
        Compara conteos actuales con snapshots previos para detectar incrementos.
        """
        incrementos = []
        
        for conv in convocatorias_actuales:
            id_conv = conv['id_convocatoria']
            total_actual = conv['total_postulados']
            
            # Si existe snapshot previo, calcular diferencia
            if id_conv in snapshots_previos:
                total_anterior = snapshots_previos[id_conv].total_postulados
                nuevas = max(0, total_actual - total_anterior)
            else:
                # Primera vez que vemos esta convocatoria
                # Opción 1: Notificar todo (nuevas = total_actual)
                # Opción 2: No notificar la primera vez (nuevas = 0)
                # Usaremos opción 2 para evitar spam en primera ejecución
                total_anterior = 0
                nuevas = 0
            
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
        session: Session,
        incremento: IncrementoPostulacionesDTO
    ) -> Notificacion | None:
        """
        Crea una notificación para informar sobre nuevas postulaciones.
        """
        cantidad = incremento.nuevas_postulaciones
        titulo = incremento.titulo
        
        # Mensaje adaptado según cantidad
        if cantidad == 1:
            mensaje = f"Tienes 1 nueva postulación en '{titulo}'. Total: {incremento.total_actual}"
        else:
            mensaje = f"Tienes {cantidad} nuevas postulaciones en '{titulo}'. Total: {incremento.total_actual}"
        
        notificacion = Notificacion(
            id_usuario=0,  # No aplica para empresas
            id_empresa=incremento.id_empresa,
            tipo_notificacion="NUEVA_POSTULACION",
            asunto=f"Nuevas postulaciones en {titulo}",
            mensaje=mensaje,
            id_oferta=incremento.id_convocatoria,  # Asumiendo que id_convocatoria = id_oferta
            prioridad="MEDIA",
            datos_adicionales=f"nuevas:{cantidad},total:{incremento.total_actual}",
            leida=False
        )
        
        return self.notificacion_repo.create(session, notificacion)
    
    def _actualizar_snapshots(self, convocatorias_actuales: List[Dict]) -> None:
        """
        Actualiza los snapshots con los valores actuales de todas las convocatorias.
        """
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