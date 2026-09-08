from fastapi import Depends, HTTPException
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.orm import Session

from app.database import get_db
from app.models import Developer
from app.core.security import decode_access_token

security_scheme = HTTPBearer()

def get_current_developer(
        credentials: HTTPAuthorizationCredentials = Depends(security_scheme),
        db: Session = Depends(get_db),
) -> Developer:
    token = credentials.credentials
    payload = decode_access_token(token)

    if payload is None:
        raise HTTPException(status_code=401, detail="Token invalide ou expiré")

    developer_id = payload.get("sub")
    if developer_id is None:
        raise HTTPException(status_code=401, detail="Token invalide")

    developer = db.query(Developer).filter(Developer.id == int(developer_id)).first()
    if developer is None:
        raise HTTPException(status_code=401, detail="Developpeur introuvable")

    return developer