from datetime import datetime
from sqlmodel import SQLModel, Field


class OfertaNotificada(SQLModel, table=True):
    """
    Tabla para trackear qué ofertas ya fueron notificadas a los usuarios.
    Evita crear notificaciones duplicadas cuando se ejecuta el proceso.
    """
    __tablename__: str= "ofertas_notificadas"

    id: int | None = Field(default=None, primary_key=True)
    id_oferta: int = Field(index=True, nullable=False, unique=True)
    id_empresa: str = Field(index=True, nullable=False, max_length=50)  # UUID como VARCHAR(50)
    titulo: str = Field(nullable=False)
    fecha_publicacion: datetime = Field(nullable=False)
    fecha_notificacion: datetime = Field(default_factory=datetime.utcnow)
    usuarios_notificados: int = Field(default=0)  # Contador de usuarios notificados
    
    class Config:
        indexes = [
            {"fields": ["id_oferta"], "unique": True},
            {"fields": ["fecha_publicacion"]},
        ]