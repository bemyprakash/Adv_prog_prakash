from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from .. import models, schemas, dependencies
from ..database import get_db
from typing import List

router = APIRouter(prefix="/support", tags=["support"])

@router.get("/tickets", response_model=List[schemas.SupportTicketOut])
def get_assigned_tickets(user=Depends(dependencies.require_role(models.RoleEnum.customer_support)), db: Session = Depends(get_db)):
    return db.query(models.SupportTicket).filter(models.SupportTicket.support_id == user.customer_support.support_id).all()

@router.post("/ticket/{ticket_id}/resolve")
def resolve_ticket(ticket_id: str, user=Depends(dependencies.require_role(models.RoleEnum.customer_support)), db: Session = Depends(get_db)):
    ticket = db.query(models.SupportTicket).filter(models.SupportTicket.ticket_id == ticket_id, models.SupportTicket.support_id == user.customer_support.support_id).first()
    if not ticket:
        raise HTTPException(status_code=404, detail="Ticket not found or not assigned to you")
    ticket.status = models.TicketStatus.resolved
    db.commit()
    return {"msg": "Ticket resolved"}

@router.post("/ticket/{ticket_id}/escalate")
def escalate_ticket(ticket_id: str, user=Depends(dependencies.require_role(models.RoleEnum.customer_support)), db: Session = Depends(get_db)):
    ticket = db.query(models.SupportTicket).filter(models.SupportTicket.ticket_id == ticket_id, models.SupportTicket.support_id == user.customer_support.support_id).first()
    if not ticket:
        raise HTTPException(status_code=404, detail="Ticket not found or not assigned to you")
    ticket.status = models.TicketStatus.escalated
    db.commit()
    return {"msg": "Ticket escalated to admin"}
