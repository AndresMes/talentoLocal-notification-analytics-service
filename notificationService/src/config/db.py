import os
from sqlmodel import create_engine
from dotenv import load_dotenv

dotenv_path = os.path.join(os.path.dirname(__file__), '../../.env')
load_dotenv(dotenv_path)

SQLAZURE_SERVER = os.getenv("AZURESQL_SERVER")
SQLAZURE_PORT = os.getenv("AZURESQL_PORT")
SQLAZURE_DB = os.getenv("AZURESQL_DB")
SQLAZURE_USER = os.getenv("AZURESQL_USER")
SQLAZURE_PASSWORD = os.getenv("AZURESQL_PASSWORD")
SQLAZURE_DRIVER = os.getenv("AZURESQL_DRIVER")

db_connection_url = f"mssql+pyodbc://{SQLAZURE_USER}:{SQLAZURE_PASSWORD}@{SQLAZURE_SERVER}:{SQLAZURE_PORT}/{SQLAZURE_DB}?driver={SQLAZURE_DRIVER.replace(' ', '+')}"

engine = create_engine(db_connection_url)

