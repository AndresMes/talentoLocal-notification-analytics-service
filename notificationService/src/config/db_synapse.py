import os
from sqlmodel import create_engine
from dotenv import load_dotenv

dotenv_path = os.path.join(os.path.dirname(__file__), '../../.env')
load_dotenv(dotenv_path)

# Configuración de Azure Synapse Analytics
SYNAPSE_SERVER = os.getenv("SYNAPSE_SERVER")
SYNAPSE_PORT = os.getenv("SYNAPSE_PORT", "1433")
SYNAPSE_DB = os.getenv("SYNAPSE_DB")
SYNAPSE_USER = os.getenv("SYNAPSE_USER")
SYNAPSE_PASSWORD = os.getenv("SYNAPSE_PASSWORD")
SYNAPSE_DRIVER = os.getenv("SYNAPSE_DRIVER", "ODBC Driver 18 for SQL Server")

# Construcción de la cadena de conexión para Synapse
# Nota: Synapse Analytics requiere configuración especial para transacciones
synapse_connection_url = (
    f"mssql+pyodbc://{SYNAPSE_USER}:{SYNAPSE_PASSWORD}"
    f"@{SYNAPSE_SERVER}:{SYNAPSE_PORT}/{SYNAPSE_DB}"
    f"?driver={SYNAPSE_DRIVER.replace(' ', '+')}"
    f"&Encrypt=yes&TrustServerCertificate=no&Connection+Timeout=30"
)

# Motor de Synapse con configuración optimizada
synapse_engine = create_engine(
    synapse_connection_url,
    echo=False,  # Cambiar a True para debug
    pool_pre_ping=True,  # Verifica la conexión antes de usar
    pool_size=10,  # Tamaño del pool de conexiones
    max_overflow=20,  # Conexiones adicionales permitidas
    pool_recycle=3600,  # Reciclar conexiones cada hora
    connect_args={
        "autocommit": True  # Importante para evitar problemas con transacciones en Synapse
    }
)