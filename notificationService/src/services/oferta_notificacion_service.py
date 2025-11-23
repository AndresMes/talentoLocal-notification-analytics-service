from sqlmodel import Session
from typing import List, Dict, Any
import httpx
import re

from ..repositories.notificacion_repo import NotificacionRepository
from ..repositories.oferta_notificada_repo import OfertaNotificadaRepository
from ..repositories.oferta_analitycs_repo import OfertaAnalyticsRepository
from ..models.notificacionInt import NotificacionInt
from ..dto.oferta_dto import OfertaDTO

# Lista completa de skills (de tu seed)
SKILLS_CONOCIDAS = [
    # Blandas
    "Pensamiento creativo", "Comunicación asertiva", "Gestión emocional",
    "Manejo de conflictos", "Empoderamiento personal", "Disciplina laboral",
    "Capacidad de análisis", "Responsabilidad social", "Etica profesional",
    "Honestidad", "Tolerancia a la frustración", "Aprendizaje continuo",
    "Orientación al servicio", "Paciencia", "Confianza interpersonal",
    "Cortesía", "Pensamiento lógico", "Sensibilidad cultural",
    "Autonomía", "Capacidad de adaptación", "Trabajo bajo presión",
    "Capacidad de escucha", "Planeación personal", "Gestión del cambio",
    "Toma de iniciativa", "Orientación al cliente", "Pensamiento positivo",
    "Capacidad de observación", "Confidencialidad", "Influencia y persuasión",
    "Manejo de prioridades", "Pensamiento organizado", "Gestión del tiempo personal",
    "Trabajo colaborativo", "Sentido de pertenencia", "Optimismo",
    "Autocontrol", "Capacidad de concentración", "Empatía social",
    "Escucha empática", "Respeto a la diversidad", "Manejo de la frustración",
    "Pensamiento sistémico", "Colaboración interdepartamental", "Gestión del conflicto",
    "Orientación a resultados", "Manejo del cambio organizacional", "Tolerancia",
    "Capacidad de negociación", "Capacidad de aprendizaje rápido", "Motivación personal",
    "Capacidad de liderazgo", "Asertividad", "Capacidad de autocrítica",
    "Trabajo ético", "Desarrollo personal", "Pensamiento estratégico personal",
    "Capacidad de mediación", "Respeto por las normas", "Responsabilidad colectiva",
    "Compromiso organizacional", "Solidaridad",
    # Duras
    "Programación en Java", "Programación en Python", "SQL",
    "Git / Control de versiones", "Linux", "Docker", "Kubernetes",
    "HTML / CSS", "Spring Boot", "React.js", "Contabilidad financiera",
    "Análisis de estados financieros", "Gestión de presupuestos",
    "Auditoría interna", "Control de inventarios", "Planeación financiera",
    "Gestión de nómina", "Tributación básica", "Evaluación de proyectos",
    "Costos y presupuestos", "Marketing digital", "Copywriting",
    "SEO (posicionamiento en buscadores)", "Análisis de mercado",
    "Branding", "Relaciones públicas", "Planificación de campañas publicitarias",
    "Email marketing", "Gestión de redes sociales", "Atención al cliente",
    # ... (resto de skills)
]

PRIORIDAD_MAP = {
    "BAJA": 1,
    "MEDIA": 2,
    "ALTA": 3,
    "URGENTE": 3
}


class OfertaNotificacionService:
    """
    Servicio para notificar a usuarios sobre nuevas ofertas que coincidan con sus skills.
    """
    
    def __init__(
        self,
        notificacion_repo: NotificacionRepository,
        oferta_notificada_repo: OfertaNotificadaRepository,
        oferta_analytics_repo: OfertaAnalyticsRepository,
        profiles_api_url: str = "https://profiles-auth-fadbasetc6fja8hs.westus3-01.azurewebsites.net/api/v1/profile"
    ):
        self.notificacion_repo = notificacion_repo
        self.oferta_notificada_repo = oferta_notificada_repo
        self.oferta_analytics_repo = oferta_analytics_repo
        self.profiles_api_url = profiles_api_url
    
    def procesar_nuevas_ofertas(self, session: Session, dias_atras: int = 7) -> Dict[str, Any]:
        """
        Procesa ofertas recientes y notifica a usuarios compatibles.
        
        Args:
            session: Sesión de base de datos
            dias_atras: Ventana de tiempo para buscar ofertas nuevas
            
        Returns:
            Resumen del procesamiento
        """
        # 1. Obtener ofertas activas recientes
        ofertas_recientes = self.oferta_analytics_repo.get_ofertas_activas_recientes(dias_atras)
        
        if not ofertas_recientes:
            return {
                "mensaje": "No hay ofertas nuevas para procesar",
                "notificaciones_creadas": 0,
                "ofertas_procesadas": 0
            }
        
        # 2. Filtrar ofertas ya notificadas
        ids_ofertas = [o['id'] for o in ofertas_recientes]
        ids_ya_notificados = self.oferta_notificada_repo.get_ids_ya_notificados(ids_ofertas)
        
        ofertas_nuevas = [
            o for o in ofertas_recientes 
            if o['id'] not in ids_ya_notificados
        ]
        
        if not ofertas_nuevas:
            return {
                "mensaje": "Todas las ofertas ya fueron notificadas",
                "notificaciones_creadas": 0,
                "ofertas_procesadas": 0
            }
        
        # 3. Procesar cada oferta
        total_notificaciones = 0
        detalles = []
        errores = []
        
        for oferta_data in ofertas_nuevas:
            try:
                # Extraer skills de los requirements
                skills = self._extraer_skills(oferta_data['requirements'])
                
                if not skills:
                    print(f"⚠️  Oferta {oferta_data['id']} sin skills reconocibles, skip")
                    continue
                
                # Limitar a las primeras 10 skills para evitar URLs muy largas
                skills_limitadas = skills[:10]
                if len(skills) > 10:
                    print(f"⚠️  Oferta {oferta_data['id']} tiene {len(skills)} skills, usando solo las primeras 10")
                
                # Buscar usuarios compatibles
                usuarios_compatibles = self._buscar_usuarios_compatibles(skills_limitadas)
                
                if usuarios_compatibles:
                    # Crear notificaciones para cada usuario
                    notificaciones_creadas = self._crear_notificaciones_oferta(
                        oferta_data,
                        usuarios_compatibles
                    )
                    
                    total_notificaciones += notificaciones_creadas
                    
                    # Marcar oferta como notificada
                    self.oferta_notificada_repo.marcar_como_notificada(
                        id_oferta=oferta_data['id'],
                        id_empresa=str(oferta_data['company_id']),
                        titulo=oferta_data['title'],
                        fecha_publicacion=oferta_data['publication_date'],
                        usuarios_notificados=notificaciones_creadas
                    )
                    
                    detalles.append({
                        "id_oferta": oferta_data['id'],
                        "titulo": oferta_data['title'],
                        "skills_encontradas": len(skills),
                        "skills_usadas": len(skills_limitadas),
                        "usuarios_notificados": notificaciones_creadas
                    })
                else:
                    print(f"ℹ️  Oferta {oferta_data['id']}: No se encontraron usuarios compatibles")
                    
            except Exception as e:
                error_msg = f"Error procesando oferta {oferta_data.get('id', 'unknown')}: {str(e)}"
                print(f"❌ {error_msg}")
                errores.append(error_msg)
                continue
        
        resultado = {
            "mensaje": f"Se procesaron {len(ofertas_nuevas)} ofertas nuevas",
            "notificaciones_creadas": total_notificaciones,
            "ofertas_procesadas": len(ofertas_nuevas),
            "ofertas_con_usuarios": len(detalles),
            "detalle": detalles
        }
        
        if errores:
            resultado["errores"] = errores
        
        return resultado
    
    def _extraer_skills(self, requirements_text: str) -> List[str]:
        """
        Extrae skills conocidas del texto de requirements.
        Busca coincidencias con la lista de skills del seed.
        """
        if not requirements_text:
            return []
        
        skills_encontradas = []
        requirements_lower = requirements_text.lower()
        
        for skill in SKILLS_CONOCIDAS:
            # Búsqueda case-insensitive
            if skill.lower() in requirements_lower:
                skills_encontradas.append(skill)
        
        return skills_encontradas
    
    def _buscar_usuarios_compatibles(self, skills: List[str]) -> List[str]:  # Retorna UUIDs como strings
        """
        Llama al API de perfiles para obtener usuarios que tengan las skills.
        
        Args:
            skills: Lista de skills a buscar
            
        Returns:
            Lista de UUIDs de usuarios compatibles (como strings)
        """
        if not skills:
            return []
        
        try:
            # Construir la URL con las skills
            skills_param = ",".join(skills)
            url = f"{self.profiles_api_url}/{skills_param}"
            
            print(f"🔍 Consultando API de perfiles: {url[:100]}...")  # Log para debug

            token = "eyJhbGciOiJIUzI1NiJ9.eyJzdWIiOiJqb2huLmRvZUBleGFtcGxlLmNvbSIsInVpZCI6Ijc1ZDQ0ZjhmLTViOTEtNDRkNC05ZDY4LTA5Zjg0Mjc4ZDVhNiIsInJvbGVzIjpbXSwiaWF0IjoxNzYzODU2NDUwLCJleHAiOjE3NjM5NDI4NTB9.pdJ-KQtHYmSOzDHd8zeC3bQbMJYZ7AaJoHQwheicOuc"
            
            # Hacer la petición con timeout más largo y reintentos
            with httpx.Client(timeout=60.0) as client:  # Aumentado a 60 segundos
                response = client.get(
                    url,
                    headers={"Authorization": f"Bearer {token}"}
                                      )
                response.raise_for_status()
                
                # Parsear respuesta
                data = response.json()
                
                print(f"✅ API respondió con {len(data) if isinstance(data, list) else 'datos'}")
                
                # Extraer IDs de usuarios
                # Ajusta según la estructura real de la respuesta del API
                if isinstance(data, list):
                    usuarios = [perfil.get('id') for perfil in data if perfil.get('id')]
                    return usuarios
                elif isinstance(data, dict) and 'profiles' in data:
                    usuarios = [perfil.get('id') for perfil in data['profiles'] if perfil.get('id')]
                    return usuarios
                else:
                    print(f"⚠️  Formato de respuesta inesperado: {type(data)}")
                    return []
                
        except httpx.TimeoutException as e:
            print(f"⏱️  Timeout al consultar API de perfiles (más de 60s): {url[:100]}")
            print(f"   Considera reducir la cantidad de skills o aumentar el timeout")
            return []
        except httpx.HTTPError as e:
            print(f"❌ Error HTTP al consultar API de perfiles: {e}")
            print(f"   URL: {url[:100]}")
            return []
        except Exception as e:
            print(f"❌ Error inesperado: {e}")
            return []
    
    def _crear_notificaciones_oferta(
        self,
        oferta_data: Dict,
        usuarios_ids: List[str]  # UUIDs como strings
    ) -> int:
        """
        Crea notificaciones para cada usuario compatible.
        
        Returns:
            Cantidad de notificaciones creadas
        """
        notificaciones_creadas = 0
        
        # Determinar prioridad basada en status
        prioridad = PRIORIDAD_MAP.get(
            oferta_data.get('status', '').upper(), 
            2  # MEDIA por defecto
        )
        
        # Convertir company_id a string (UUID)
        id_empresa = str(oferta_data['company_id'])
        
        for usuario_id in usuarios_ids:
            try:
                notificacion = NotificacionInt(
                    id_usuario=usuario_id,  # Ya es string (UUID)
                    id_empresa=id_empresa,  # Convertido a string
                    tipo_notificacion="NUEVA_OFERTA_COMPATIBLE",
                    asunto=f"Nueva oferta: {oferta_data['title']}",
                    mensaje=f"Hay una nueva oferta que coincide con tu perfil: '{oferta_data['title']}' en {oferta_data['location']}.&Salario: ${oferta_data['salary']}",
                    id_oferta=oferta_data['id'],
                    prioridad=prioridad,
                    datos_adicionales=f"modalidad:{oferta_data['modality']}&ubicacion:{oferta_data['location']}",
                    leida=False
                )
                
                # Crear la notificación (gestiona su propia sesión)
                self.notificacion_repo.create_(notificacion)
                notificaciones_creadas += 1
                
            except Exception as e:
                print(f"Error al crear notificación para usuario {usuario_id}: {e}")
                continue
        
        return notificaciones_creadas
    
    def analizar_ofertas_sin_notificar(self, session: Session, dias_atras: int = 7) -> Dict[str, Any]:
        """
        Analiza ofertas y extrae skills SIN llamar al API ni crear notificaciones.
        Útil para debugging y ver qué skills se están extrayendo.
        
        Returns:
            Resumen con ofertas y skills encontradas
        """
        ofertas_recientes = self.oferta_analytics_repo.get_ofertas_activas_recientes(dias_atras)
        
        if not ofertas_recientes:
            return {
                "mensaje": "No hay ofertas nuevas para analizar",
                "ofertas_analizadas": 0
            }
        
        ids_ofertas = [o['id'] for o in ofertas_recientes]
        ids_ya_notificados = self.oferta_notificada_repo.get_ids_ya_notificados(ids_ofertas)
        
        ofertas_nuevas = [
            o for o in ofertas_recientes 
            if o['id'] not in ids_ya_notificados
        ]
        
        analisis = []
        total_skills = 0
        
        for oferta_data in ofertas_nuevas:
            skills = self._extraer_skills(oferta_data['requirements'])
            total_skills += len(skills)
            
            analisis.append({
                "id_oferta": oferta_data['id'],
                "titulo": oferta_data['title'],
                "company_id": oferta_data['company_id'],
                "requirements_preview": oferta_data['requirements'][:200] + "..." if len(oferta_data['requirements']) > 200 else oferta_data['requirements'],
                "skills_encontradas": len(skills),
                "skills": skills[:10],  # Solo las primeras 10
                "total_skills": len(skills)
            })
        
        return {
            "mensaje": f"Análisis completado (sin notificar)",
            "ofertas_analizadas": len(ofertas_nuevas),
            "total_skills_encontradas": total_skills,
            "promedio_skills_por_oferta": round(total_skills / len(ofertas_nuevas), 2) if ofertas_nuevas else 0,
            "ofertas": analisis
        }