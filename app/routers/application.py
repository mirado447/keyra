from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy import func
from app.models import Enduser
import secrets

from app.database import get_db
from app.models import Application, Developer
from app.schemas.application import ApplicationCreate, ApplicationCreated, ApplicationOut
from app.core.security import hash_password
from app.core.deps import get_current_developer

router = APIRouter(prefix="/applications", tags=["applications"])

@router.post("/", response_model=ApplicationCreated)
def create_application(
    application: ApplicationCreate,
    db: Session = Depends(get_db),
    current_developer: Developer = Depends(get_current_developer),
):
    public_key = secrets.token_urlsafe(24)
    private_key = secrets.token_urlsafe(32)
    private_key_hash = hash_password(private_key)

    new_app = Application(
        name = application.name,
        public_key = public_key,
        private_key_hash = private_key_hash,
        developer_id = current_developer.id,
    )
    db.add(new_app)
    db.commit()
    db.refresh(new_app)

    return ApplicationCreated(
        id= new_app.id,
        name= new_app.name,
        public_key= new_app.public_key,
        create_at= new_app.create_at,
        private_key= private_key,
    )

@router.get("/", response_model=list[ApplicationOut])
def get_applications(
    db: Session = Depends(get_db),
    current_developer: Developer = Depends(get_current_developer)
):
    results = (
        db.query(Application, func.count(Enduser.id).label("end_user_count"))
        .outerjoin(Enduser, Enduser.app_id == Application.id)
        .filter(Application.developer_id == current_developer.id)
        .group_by(Application.id)
        .all()
    )

    applications = []
    for app, count in results:
        app_out = ApplicationOut.model_validate(app)
        app_out.end_user_count = count
        applications.append(app_out)
    return applications

@router.get("/{application_id}", response_model=ApplicationOut)
def get_application(
    application_id: int,
    db: Session = Depends(get_db),
    current_developer: Developer = Depends(get_current_developer),
):
    application = (
        db.query(Application).
        filter(
            Application.id == application_id,
            Application.developer_id == current_developer.id,
        )
        .first()
    )

    if application is None:
        raise HTTPException(status_code=404, detail="Application introuvable")

    return application