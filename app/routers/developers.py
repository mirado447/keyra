from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError

from app.database import get_db
from app.models import Developer
from app.schemas.developer import DeveloperCreate, DeveloperOut
from app.core.security import hash_password

router = APIRouter(prefix="/developers", tags=["developers"])

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