from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from .. import models, schemas, dependencies
from ..database import get_db
from typing import List

router = APIRouter(prefix="/customer", tags=["customer"])

@router.get("/orders", response_model=List[schemas.OrderOut])
def get_orders(user=Depends(dependencies.require_role(models.RoleEnum.customer)), db: Session = Depends(get_db)):
    return db.query(models.Order).filter(models.Order.customer_id == user.user_id).all()

@router.post("/order", response_model=schemas.OrderOut)
def place_order(order: schemas.OrderCreate, user=Depends(dependencies.require_role(models.RoleEnum.customer)), db: Session = Depends(get_db)):
    # Create order
    import uuid, datetime
    order_id = str(uuid.uuid4())
    db_order = models.Order(
        order_id=order_id,
        customer_id=user.user_id,
        restaurant_id=order.restaurant_id,
        status=models.OrderStatus.pending,
        total_amount=0.0,
        placed_at=datetime.datetime.utcnow()
    )
    db.add(db_order)
    # Add items
    for item in order.items:
        db.add(models.OrderMenuItem(order_id=order_id, item_id=item["item_id"], quantity=item["quantity"]))
    db.commit()
    db.refresh(db_order)
    return db_order

@router.post("/ticket", response_model=schemas.SupportTicketOut)
def raise_ticket(ticket: schemas.SupportTicketCreate, user=Depends(dependencies.require_role(models.RoleEnum.customer)), db: Session = Depends(get_db)):
    import uuid, datetime
    ticket_id = str(uuid.uuid4())
    db_ticket = models.SupportTicket(
        ticket_id=ticket_id,
        customer_id=user.user_id,
        order_id=ticket.order_id,
        issue_type=ticket.issue_type,
        description=ticket.description,
        status=models.TicketStatus.open,
        created_at=datetime.datetime.utcnow()
    )
    db.add(db_ticket)
    db.commit()
    db.refresh(db_ticket)
    return db_ticket
