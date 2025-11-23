import os
from urllib.parse import quote_plus
from sqlmodel import create_engine
from dotenv import load_dotenv
from urllib.parse import quote_plus

dotenv_path = os.path.join(os.path.dirname(__file__), '../../.env')
load_dotenv(dotenv_path)

# Configuración de Azure Synapse Analytics
SYNAPSE_SERVER = os.getenv("SYNAPSE_SERVER")
SYNAPSE_PORT = os.getenv("SYNAPSE_PORT", "1433")
SYNAPSE_DB = os.getenv("SYNAPSE_DB")
SYNAPSE_USER = os.getenv("SYNAPSE_USER")
SYNAPSE_PASSWORD = os.getenv("SYNAPSE_PASSWORD")
SYNAPSE_DRIVER = os.getenv("SYNAPSE_DRIVER", "ODBC Driver 18 for SQL Server")

# URL-encode el usuario y contraseña para manejar caracteres especiales
encoded_user = quote_plus(SYNAPSE_USER) if SYNAPSE_USER else ""
encoded_password = quote_plus(SYNAPSE_PASSWORD) if SYNAPSE_PASSWORD else ""
encoded_driver = quote_plus(SYNAPSE_DRIVER)


# Construcción de la cadena de conexión para Synapse
synapse_connection_url = (
    f"mssql+pyodbc://{encoded_user}:{encoded_password}"
    f"@{SYNAPSE_SERVER}:{SYNAPSE_PORT}/{SYNAPSE_DB}"
    f"?driver={encoded_driver}"
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