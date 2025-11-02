from fastapi import FastAPI

app = FastAPI(title="Notification-Service")

@app.get("/")
def home():
    return {"message" : "Hola mundo"}
