from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from .. import models, schemas, dependencies
from ..database import get_db
from typing import List

router = APIRouter(prefix="/ticket", tags=["ticket"])

@router.get("/{ticket_id}", response_model=schemas.SupportTicketOut)
def get_ticket(ticket_id: str, user=Depends(dependencies.require_any_role([
    models.RoleEnum.customer, models.RoleEnum.customer_support, models.RoleEnum.admin
])), db: Session = Depends(get_db)):
    ticket = db.query(models.SupportTicket).filter(models.SupportTicket.ticket_id == ticket_id).first()
    if not ticket:
        raise HTTPException(status_code=404, detail="Ticket not found")
    return ticket
