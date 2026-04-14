from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from .. import models, schemas, dependencies
from ..database import get_db
from typing import List

router = APIRouter(prefix="/order", tags=["order"])

@router.get("/{order_id}", response_model=schemas.OrderOut)
def get_order(order_id: str, user=Depends(dependencies.require_any_role([
    models.RoleEnum.customer, models.RoleEnum.restaurant_owner, models.RoleEnum.delivery_agent, models.RoleEnum.admin
])), db: Session = Depends(get_db)):
    order = db.query(models.Order).filter(models.Order.order_id == order_id).first()
    if not order:
        raise HTTPException(status_code=404, detail="Order not found")
    return order

@router.post("/{order_id}/cancel")
def cancel_order(order_id: str, user=Depends(dependencies.require_role(models.RoleEnum.customer)), db: Session = Depends(get_db)):
    order = db.query(models.Order).filter(models.Order.order_id == order_id, models.Order.customer_id == user.user_id).first()
    if not order:
        raise HTTPException(status_code=404, detail="Order not found or not yours")
    order.status = models.OrderStatus.cancelled
    db.commit()
    return {"msg": "Order cancelled"}
