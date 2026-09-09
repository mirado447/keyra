from fastapi import FastAPI
from app.routers import developers, application, enduser_auth

app = FastAPI()
app.include_router(developers.router)
app.include_router(application.router)
app.include_router(enduser_auth.router)

@app.get("/health")
def health_check():
    return {"status": "ok"}
