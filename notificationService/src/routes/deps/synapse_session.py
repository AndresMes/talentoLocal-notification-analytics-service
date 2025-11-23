from typing import Annotated, Generator
from fastapi import Depends
from sqlmodel import Session
from ...config.db_synapse import synapse_engine


def get_synapse_session() -> Generator[Session, None, None]:
    """
    Generador de sesión para Azure Synapse Analytics.
    Se usa para consultas analíticas y de solo lectura.
    """
    with Session(synapse_engine) as session:
        yield session


SynapseSessionDep = Annotated[Session, Depends(get_synapse_session)]