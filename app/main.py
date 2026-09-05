from fastapi import FastAPI
from app.routers import developers

app = FastAPI()
app.include_router(developers.router)

@app.get("/health")
def health_check():
    return {"status": "ok"}
