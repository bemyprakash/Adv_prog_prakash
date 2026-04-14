from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from .. import models, schemas, dependencies
from ..database import get_db
from typing import List

router = APIRouter(prefix="/restaurant", tags=["restaurant"])

@router.get("/menu", response_model=List[schemas.MenuItemOut])
def get_menu(user=Depends(dependencies.require_role(models.RoleEnum.restaurant_owner)), db: Session = Depends(get_db)):
    return db.query(models.MenuItem).filter(models.MenuItem.restaurant_id == user.restaurant_owner.restaurant_id).all()

@router.post("/menu", response_model=schemas.MenuItemOut)
def add_menu_item(item: schemas.MenuItemCreate, user=Depends(dependencies.require_role(models.RoleEnum.restaurant_owner)), db: Session = Depends(get_db)):
    import uuid
    item_id = str(uuid.uuid4())
    db_item = models.MenuItem(
        item_id=item_id,
        restaurant_id=user.restaurant_owner.restaurant_id,
        name=item.name,
        description=item.description,
        price=item.price,
        category=item.category,
        is_available=item.is_available
    )
    db.add(db_item)
    db.commit()
    db.refresh(db_item)
    return db_item

@router.get("/orders", response_model=List[schemas.OrderOut])
def get_orders(user=Depends(dependencies.require_role(models.RoleEnum.restaurant_owner)), db: Session = Depends(get_db)):
    return db.query(models.Order).filter(models.Order.restaurant_id == user.restaurant_owner.restaurant_id).all()
