from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError
from datetime import datetime, timezone

from app.database import get_db
from app.models import Enduser, Application, RefreshToken
from app.schemas.enduser import EndUserCreate, EndUserLogin, EndUserOut
from app.core.security import hash_password, verify_password, create_access_token, generate_refresh_token, hash_token
from app.core.deps import get_application_by_public_key

router = APIRouter(prefix="/apps/{public_key}", tags=["end-user-auth"])

# Inscrit un nouvel utilisateur pour l'application spécifiée
@router.post("/register", response_model=EndUserOut)
def register_enduser(
    public_key: str,
    enduser: EndUserCreate,
    db: Session = Depends(get_db),
    application: Application = Depends(get_application_by_public_key),
):
    existing = (
        db.query(Enduser)
        .filter(Enduser.app_id == application.id, Enduser.email == enduser.email)
        .first()
    )
    if existing:
        raise HTTPException(status_code=409, detail="Cet email est déja utilisé pour cette application")

    new_enduser = Enduser(
        name= enduser.name,
        email= enduser.email,
        password_hash= hash_password(enduser.password),
        app_id = application.id
    )
    db.add(new_enduser)
    try:
        db.commit()
    except IntegrityError:
        db.rollback()
        raise HTTPException(status_code=409, detail="Cet email est déja utilisé pour cette application")

    db.refresh(new_enduser)
    return new_enduser

# Authentifie un utilisateur et génère un access token et un refresh token
@router.post("/login")
def login_enduser(
    public_key: str,
    credentials: EndUserLogin,
    db: Session = Depends(get_db),
    application: Application = Depends(get_application_by_public_key),
):
    enduser = (
        db.query(Enduser)
        .filter(Enduser.app_id == application.id, Enduser.email == credentials.email)
        .first()
    )

    if not enduser or not verify_password(credentials.password, str(enduser.password_hash)):
        raise HTTPException(status_code=401, detail="Email ou mot de passe incorrect")

    access_token = create_access_token(
        data={"sub": str(enduser.id), "app_id": application.id}
    )

    raw_refresh_token, refresh_token_hash, expires_at = generate_refresh_token()
    new_refresh_token = RefreshToken(
        token_hash = refresh_token_hash,
        expire_at = expires_at,
        user_id = enduser.id,
    )
    db.add(new_refresh_token)
    db.commit()

    return {
        "access_token": access_token,
        "refresh_token": raw_refresh_token,
        "token_type": "bearer",
        }

# Vérifie le refresh token et génère un nouvel access token et un nouveau refresh token
@router.post("/refresh")
def refresh_token_endpoint(
    public_key: str,
    refresh_token: str,
    db: Session = Depends(get_db),
    application: Application = Depends(get_application_by_public_key),
):
    token_hash = hash_token(refresh_token)

    stored_token = db.query(RefreshToken).filter(RefreshToken.token_hash == token_hash).first()

    if stored_token is None or stored_token.revoked:
        raise HTTPException(status_code=401, detail="Refresh token invalide")

    if stored_token.expire_at < datetime.now(timezone.utc):
        raise HTTPException(status_code=401, detail="Refresh token expiré")

    enduser = db.query(Enduser).filter(Enduser.id == stored_token.user_id).first()
    if enduser is None or enduser.app_id != application.id:
        raise HTTPException(status_code=401, detail="Refresh token invalide pour cette application")

    stored_token.revoked = True

    new_access_token = create_access_token(data={"sub": str(enduser.id), "app_id": application.id})
    raw_new_refresh, new_refresh_hash, new_expires_at = generate_refresh_token()
    new_refresh_token = RefreshToken(
        token_hash=new_refresh_hash,
        expire_at=new_expires_at,
        user_id=enduser.id,
    )
    db.add(new_refresh_token)
    db.commit()

    return {
        "access_token": new_access_token,
        "refresh_token": raw_new_refresh,
        "token_type": "bearer",
    }

# Révoque le refresh token et déconnecte l'utilisateur
@router.post("/logout")
def logout_enduser(
    public_key:str,
    refresh_token:str,
    db: Session = Depends(get_db),
    application: Application = Depends(get_application_by_public_key)
):
    token_hash = hash_token(refresh_token)
    stored_token = db.query(RefreshToken).filter(RefreshToken.token_hash == token_hash).first()

    if stored_token:
        stored_token.revoked = True
        db.commit()

    return {"detail": "Déconnecté"}