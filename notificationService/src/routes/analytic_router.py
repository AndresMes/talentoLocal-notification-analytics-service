from fastapi import APIRouter, Depends, Query, status
from sqlmodel import Session
from datetime import datetime
from typing import List, Dict, Any, Optional
from ..repositories.analytic_repo import NotificacionAnalyticsRepository
from ..config.db_synapse import synapse_engine
from ..schemas.analytics_schemas import (
    PostuladosResponse,
    CantidadResponse,
    URLResponse
)

router = APIRouter(
    prefix="/analytics",
    tags=["Analytics - Synapse"]
)

def get_synapse_session():
    """Retorna una sesión conectada a Synapse."""
    with Session(synapse_engine) as session:
        yield session

def get_repo(session: Session = Depends(get_synapse_session)):
    """Retorna el repositorio de analytics."""
    return NotificacionAnalyticsRepository(session)

## Enpoints
@router.get(
    "/postulados-por-convocatoria",
    summary="Postulados por convocatoria",
    response_model=PostuladosResponse,
)
def postulados_por_convocatoria(repo=Depends(get_repo)):
    """Retorna la cantidad de postulados por cada convocatoria."""
    return {"data": repo.get_postulados_por_convocatoria()}


@router.get(
    "/empleos-publicados",
    summary="Cantidad de empleos publicados",
    response_model=CantidadResponse,
)
def empleos_publicados(repo=Depends(get_repo)):
    """Retorna el número de ofertas activas."""
    return {"cantidad": repo.get_cant_empleos_publicados()}


@router.get(
    "/cant-empresas",
    summary="Cantidad de empresas",
    response_model=CantidadResponse,
)
def empresas(repo=Depends(get_repo)):
    """Retorna el número total de empresas."""
    return {"cantidad": repo.get_cant_empresas()}


@router.get(
    "/cant-usuarios",
    summary="Cantidad de usuarios",
    response_model=CantidadResponse,
)
def usuarios(repo=Depends(get_repo)):
    """Retorna el número total de usuarios."""
    return {"cantidad": repo.get_cant_usuarios()}


DASHBOARD_URL = "https://app.powerbi.com/view?r=eyJrIjoiMDE5MmFiY2QtMTg0OC00MjAyLTg0ZGItOWNiZjVlYzRkNWJhIiwidCI6ImZkNjljZTFiLTIwYzYtNDJlYy1iNTRlLTZkMWIzODcwYWM2ZSIsImMiOjR9&pageName=1eff730f848408a19727"
@router.get(
    "/dashboard-url",
    summary="Dashboard URL",
    response_model=URLResponse,
)
def dashboard_url():
    """Retorna la URL pública del dashboard."""
    return {"url": DASHBOARD_URL}
