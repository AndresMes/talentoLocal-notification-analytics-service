from pydantic import BaseModel
from typing import List

class PostuladoConvocatoria(BaseModel):
    id_empresa: int
    id_convocatoria: int
    titulo: str
    total_postulados: int

class PostuladosResponse(BaseModel):
    data: List[PostuladoConvocatoria]

class CantidadResponse(BaseModel):
    cantidad: int

class URLResponse(BaseModel):
    url: str
