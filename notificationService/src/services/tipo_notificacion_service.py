from typing import List, Optional, Dict, Any
from sqlmodel import Session
from ..models.tipo_notificacion import TipoNotificacion

# importamos las funciones del repo (usa imports relativos)
from ..repositories.tipo_notificacion_repo import (
    get_by_id as repo_get_by_id,
    get_by_codigo as repo_get_by_codigo,
    list_all as repo_list_all,
    create as repo_create,
    update as repo_update,
    delete as repo_delete,
)


class TipoNotificacionService:
    def __init__(self, session: Session):
        self.session = session

    def list(self) -> List[TipoNotificacion]:
        """Devuelve lista de tipos de notificación."""
        return repo_list_all(self.session)

    def get(self, id_: int) -> TipoNotificacion:
        """Devuelve un tipo por id o lanza ValueError si no existe."""
        obj = repo_get_by_id(self.session, id_)
        if not obj:
            raise ValueError("TipoNotificacion no encontrado")
        return obj

    def create(self, payload: Dict[str, Any]) -> TipoNotificacion:
        """
        Crea un TipoNotificacion.
        `payload` puede ser un dict o un objeto pydantic (con .dict() / .model_dump()).
        """
        # normalizar payload a dict si viene un Pydantic model
        if hasattr(payload, "model_dump"):
            payload = payload.model_dump(exclude_unset=True)
        elif hasattr(payload, "dict"):
            payload = payload.dict()

        # negocio: código único
        codigo = payload.get("codigo")
        if codigo and repo_get_by_codigo(self.session, codigo):
            raise ValueError("Código ya existe")

        tipo = TipoNotificacion(**payload)
        return repo_create(self.session, tipo)

    def update(self, id_: int, payload: Dict[str, Any]) -> TipoNotificacion:
        """
        Actualiza un TipoNotificacion.
        `payload` puede ser dict o DTO pydantic con solo los campos a cambiar.
        """
        if hasattr(payload, "model_dump"):
            data = payload.model_dump(exclude_unset=True)
        elif hasattr(payload, "dict"):
            data = payload.dict(exclude_unset=True)
        else:
            data = dict(payload or {})

        obj = self.get(id_)  # lanza ValueError si no existe

        # Aplicar cambios solo en los campos presentes
        for key, value in data.items():
            # opcional: proteger campos no actualizables
            if key == "id_tipo_notificacion":
                continue
            setattr(obj, key, value)

        return repo_update(self.session, obj)

    def set_active(self, id_: int, active: bool) -> TipoNotificacion:
        """Activa/desactiva un tipo."""
        obj = self.get(id_)
        obj.activo = active
        return repo_update(self.session, obj)

    def delete(self, id_: int) -> None:
        """Elimina un tipo (lanza ValueError si no existe)."""
        obj = self.get(id_)
        repo_delete(self.session, obj)