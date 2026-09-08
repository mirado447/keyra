from fastapi import FastAPI
from app.routers import developers, application

app = FastAPI()
app.include_router(developers.router)
app.include_router(application.router)

@app.get("/health")
def health_check():
    return {"status": "ok"}
