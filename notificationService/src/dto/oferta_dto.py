from datetime import datetime
from pydantic import BaseModel
from typing import List, Optional


class OfertaDTO(BaseModel):
    """DTO para información de ofertas desde Synapse"""
    id: int
    title: str
    subtitle: str
    description: str
    modality: str
    salary: int
    requirements: str  # Aquí vienen las skills como texto
    benefits: str
    years_experience: int
    location: str
    journey: str
    schedule: str
    available_places: int
    status: str
    contract_type: str
    payment_type: str
    publication_date: datetime
    closing_date: Optional[datetime]
    company_id: int
    category_id: int


class PerfilDTO(BaseModel):
    """DTO para respuesta del API de perfiles"""
    id: int
    # Agrega los campos que devuelve el API de perfiles
    # Por ahora solo necesitamos el ID del usuario


class OfertaConSkillsDTO(BaseModel):
    """DTO para ofertas con skills extraídas"""
    oferta: OfertaDTO
    skills: List[str]  # Lista de skills extraídas de requirements