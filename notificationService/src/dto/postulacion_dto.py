from pydantic import BaseModel


class ConvocatoriaPostuladosDTO(BaseModel):
    """DTO para información de postulados por convocatoria desde Synapse"""
    id_empresa: int
    id_convocatoria: int
    titulo: str
    total_postulados: int


class IncrementoPostulacionesDTO(BaseModel):
    """DTO para representar el incremento de postulaciones en una convocatoria"""
    id_empresa: str
    id_convocatoria: int
    titulo: str
    total_anterior: int
    total_actual: int
    nuevas_postulaciones: int
    
    @property
    def tiene_incremento(self) -> bool:
        return self.nuevas_postulaciones > 0