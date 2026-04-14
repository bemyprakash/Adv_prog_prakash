from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from .. import models, schemas, auth, dependencies
from ..database import get_db
from jose import JWTError
from datetime import timedelta
import uuid

router = APIRouter(prefix="/auth", tags=["auth"])

@router.post("/register", response_model=schemas.UserAccountOut)
def register(user: schemas.UserAccountCreate, db: Session = Depends(get_db)):
    # Check if user exists
    if db.query(models.UserAccount).filter(models.UserAccount.email == user.email).first():
        raise HTTPException(status_code=400, detail="Email already registered")
    user_id = str(uuid.uuid4())
    hashed_pw = auth.get_password_hash(user.password)
    db_user = models.UserAccount(
        user_id=user_id,
        name=user.name,
        phone=user.phone,
        email=user.email,
        password=hashed_pw,
        role=user.role
    )
    db.add(db_user)
    # Create role-specific record
    if user.role == models.RoleEnum.customer:
        db.add(models.Customer(user_id=user_id))
    elif user.role == models.RoleEnum.restaurant_owner:
        db.add(models.RestaurantOwner(user_id=user_id, restaurant_id=f"r-{user_id[:6]}", restaurant_name="", opening_hours=""))
    elif user.role == models.RoleEnum.delivery_agent:
        db.add(models.DeliveryAgent(user_id=user_id, agent_id=f"a-{user_id[:6]}", vehicle_type="", current_location="", is_available=True))
    elif user.role == models.RoleEnum.customer_support:
        db.add(models.CustomerSupport(user_id=user_id, support_id=f"s-{user_id[:6]}", availability_status="AVAILABLE", department="General"))
    db.commit()
    db.refresh(db_user)
    return db_user

@router.post("/login", response_model=schemas.Token)
def login(form_data: schemas.UserAccountCreate, db: Session = Depends(get_db)):
    user = auth.authenticate_user(db, form_data.email, form_data.password)
    if not user:
        raise HTTPException(status_code=401, detail="Incorrect email or password")
    access_token = auth.create_access_token(data={"sub": user.user_id, "role": user.role})
    return {"access_token": access_token, "token_type": "bearer"}
