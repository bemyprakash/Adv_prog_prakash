from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from .. import models, schemas, dependencies
from ..database import get_db
from typing import List

router = APIRouter(prefix="/payment", tags=["payment"])

@router.post("/process", response_model=schemas.PaymentOut)
def process_payment(payment: schemas.PaymentCreate, user=Depends(dependencies.require_any_role([
    models.RoleEnum.customer, models.RoleEnum.restaurant_owner
])), db: Session = Depends(get_db)):
    import uuid
    db_payment = models.Payment(
        payment_id=str(uuid.uuid4()),
        order_id=payment.order_id,
        amount=payment.amount,
        method=payment.method,
        status=models.PaymentStatus.success,
        transaction_ref="TXN-" + str(uuid.uuid4())[:8]
    )
    db.add(db_payment)
    # Update order status
    order = db.query(models.Order).filter(models.Order.order_id == payment.order_id).first()
    if order:
        order.status = models.OrderStatus.confirmed
    db.commit()
    db.refresh(db_payment)
    return db_payment
