from datetime import datetime
from sqlmodel import SQLModel, Field

class ConvocatoriaSnapshot(SQLModel, table=True):
    """
    Tabla para guardar el último conteo conocido de postulaciones por convocatoria.
    Permite detectar incrementos comparando con el estado actual.
    """

    __tablename__ : str = "convocatoria_snapshots"

    id: int | None = Field(default=None, primary_key=True)
    id_empresa: int = Field(index=True, nullable=False)
    id_convocatoria: int = Field(index=True, nullable=False, unique=True)
    titulo: str = Field(nullable=False)
    total_postulados: int = Field(default=0)
    ultima_actualizacion: datetime = Field(default_factory=datetime.utcnow)

    class Config:
        indexes = [
            {"fields": ["id_empresa", "id_convocatoria"]},
        ]