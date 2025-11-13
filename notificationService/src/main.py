from fastapi import FastAPI
from sqlmodel import SQLModel
from .config.db import engine
from .models import Notificacion
from .routes.notificacion_router import router
from fastapi.responses import HTMLResponse


app = FastAPI(title="Notification-Service")

@app.get("/", response_class=HTMLResponse)
def home():
    html = """
    <!DOCTYPE html>
    <html lang="es">
    <head>
        <meta charset="UTF-8">
        <title>FastAPI Home</title>
        <style>
            body {
                display: flex;
                flex-direction: column;
                align-items: center;
                justify-content: center;
                height: 100vh;
                margin: 0;
                background-color: #f0f4f8;
                font-family: Arial, sans-serif;
            }
            img {
                width: 180px;
                height: auto;
                margin-bottom: 20px;
            }
            h1 {
                color: #05998b;
                font-size: 24px;
            }
        </style>
    </head>
    <body>
        <img src="https://fastapi.tiangolo.com/img/logo-margin/logo-teal.png" alt="FastAPI Logo">
        <h1>Bienvenido a Talento Analytic Server 📊</h1>
    </body>
    </html>
    """
    return HTMLResponse(content=html)

app.include_router(router)