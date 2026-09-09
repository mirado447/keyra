from fastapi import FastAPI
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.util import get_remote_address
from slowapi.errors import RateLimitExceeded
from typing import cast
from starlette.types import ExceptionHandler

from app.routers import developers, application, enduser_auth

limiter = Limiter(key_func=get_remote_address)

app = FastAPI()
app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded,  cast("ExceptionHandler", _rate_limit_exceeded_handler))

app.include_router(developers.router)
app.include_router(application.router)
app.include_router(enduser_auth.router)

@app.get("/health")
def health_check():
    return {"status": "ok"}
