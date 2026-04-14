from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from .. import models, schemas, dependencies
from ..database import get_db
from typing import List

router = APIRouter(prefix="/admin", tags=["admin"])

@router.get("/users", response_model=List[schemas.UserAccountOut])
def get_all_users(user=Depends(dependencies.require_role(models.RoleEnum.admin)), db: Session = Depends(get_db)):
    return db.query(models.UserAccount).all()

@router.get("/reports")
def get_reports(user=Depends(dependencies.require_role(models.RoleEnum.admin)), db: Session = Depends(get_db)):
    # Dummy report
    return {"orders": db.query(models.Order).count(), "payments": db.query(models.Payment).count(), "tickets": db.query(models.SupportTicket).count()}
