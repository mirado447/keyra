from fastapi import APIRouter, Depends, HTTPException, Request
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError
from typing import cast
from slowapi import Limiter
from slowapi.util import get_remote_address
from app.core.deps import get_current_developer

from app.database import get_db
from app.models import Developer
from app.schemas.developer import DeveloperCreate, DeveloperOut, DeveloperLogin
from app.core.security import hash_password, verify_password, create_access_token

limiter = Limiter(key_func=get_remote_address)

router = APIRouter(prefix="/developers", tags=["developers"])

# Crée un nouveau développeur
@router.post("/register", response_model=DeveloperOut)
def register_developer(developer: DeveloperCreate, db: Session = Depends(get_db)):
    hashed_password = hash_password(developer.password)

    new_developer = Developer(
        name = developer.name,
        email = developer.email,
        password_hash = hashed_password
    )

    db.add(new_developer)
    try:
        db.commit()
    except IntegrityError:
        db.rollback()
        raise HTTPException(status_code=409, detail="Cet email est déja utilisé")

    db.refresh(new_developer)
    return new_developer

# Authentifie un développeur puis génère un token JWT en cas de connexion réussie.
@router.post("/login")
@limiter.limit("5/minute")
def login_developer(request: Request, credentials: DeveloperLogin, db: Session = Depends(get_db)):
    developer = db.query(Developer).filter(Developer.email == credentials.email).first()

    if not developer or not verify_password(credentials.password, cast(str, developer.password_hash)):
        raise HTTPException(status_code=401, detail="Email ou mot de passe incorrect")

    access_token = create_access_token(data={"sub": str(developer.id)})
    return {"access_token": access_token, "token_type": "bearer"}

@router.get("/me", response_model=DeveloperOut)
def get_me(current_developer: Developer = Depends(get_current_developer)):
    return current_developer