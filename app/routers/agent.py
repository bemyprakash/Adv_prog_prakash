from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from .. import models, schemas, dependencies
from ..database import get_db
from typing import List

router = APIRouter(prefix="/agent", tags=["agent"])

@router.get("/orders", response_model=List[schemas.OrderOut])
def get_assigned_orders(user=Depends(dependencies.require_role(models.RoleEnum.delivery_agent)), db: Session = Depends(get_db)):
    return db.query(models.Order).filter(models.Order.agent_id == user.delivery_agent.agent_id).all()

@router.post("/order/{order_id}/update_location")
def update_location(order_id: str, location: str, user=Depends(dependencies.require_role(models.RoleEnum.delivery_agent)), db: Session = Depends(get_db)):
    order = db.query(models.Order).filter(models.Order.order_id == order_id, models.Order.agent_id == user.delivery_agent.agent_id).first()
    if not order:
        raise HTTPException(status_code=404, detail="Order not found or not assigned to you")
    user.delivery_agent.current_location = location
    db.commit()
    return {"msg": "Location updated"}

@router.post("/order/{order_id}/delivered")
def mark_delivered(order_id: str, user=Depends(dependencies.require_role(models.RoleEnum.delivery_agent)), db: Session = Depends(get_db)):
    order = db.query(models.Order).filter(models.Order.order_id == order_id, models.Order.agent_id == user.delivery_agent.agent_id).first()
    if not order:
        raise HTTPException(status_code=404, detail="Order not found or not assigned to you")
    order.status = models.OrderStatus.delivered
    db.commit()
    return {"msg": "Order marked as delivered"}
