from fastapi import APIRouter, Request, Form, Depends, status
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session
from ..database import get_db
from .. import models
import uuid

router = APIRouter()
templates = Jinja2Templates(directory="app/templates")

def get_current_user(request: Request, db: Session):
    user_id = request.cookies.get("user_id")
    role = request.cookies.get("role")
    if not user_id or not role:
        return None, None
    user = db.query(models.UserAccount).filter(models.UserAccount.user_id == user_id).first()
    return user, role

@router.get("/web/login", response_class=HTMLResponse)
def login_form(request: Request):
    return templates.TemplateResponse(request=request, name="login.html", context={"request": request})

@router.post("/web/login", response_class=HTMLResponse)
def login_post(request: Request, email: str = Form(...), password: str = Form(...), role: str = Form(...), db: Session = Depends(get_db)):
    user = db.query(models.UserAccount).filter(models.UserAccount.email == email, models.UserAccount.role == role).first()
    if not user:
        return templates.TemplateResponse(request=request, name="login.html", context={"request": request, "error": "Invalid credentials or role mismatch."})
    response = RedirectResponse(url="/web/dashboard", status_code=status.HTTP_302_FOUND)
    response.set_cookie(key="user_id", value=user.user_id)
    response.set_cookie(key="role", value=role)
    return response

@router.get("/web/register", response_class=HTMLResponse)
def register_form(request: Request):
    return templates.TemplateResponse(request=request, name="register.html", context={"request": request})

@router.post("/web/register", response_class=HTMLResponse)
def register_post(request: Request, name: str = Form(...), phone: str = Form(...), email: str = Form(...), password: str = Form(...), role: str = Form(...), db: Session = Depends(get_db)):
    from .. import auth, schemas
    try:
        user_create = schemas.UserAccountCreate(name=name, phone=phone, email=email, password=password, role=role)
        from .auth import register
        register(user_create, db)
        return RedirectResponse(url="/web/login", status_code=status.HTTP_302_FOUND)
    except Exception as e:
        return templates.TemplateResponse(request=request, name="register.html", context={"request": request, "error": str(e)})

@router.get("/web/logout")
def logout():
    response = RedirectResponse(url="/web/login")
    response.delete_cookie("user_id")
    response.delete_cookie("role")
    return response

@router.get("/web/dashboard", response_class=HTMLResponse)
def dashboard(request: Request, db: Session = Depends(get_db)):
    user, role = get_current_user(request, db)
    if not user:
        return RedirectResponse(url="/web/login")
    
    if role == "customer":
        customer = db.query(models.Customer).filter(models.Customer.user_id == user.user_id).first()
        query_str = request.query_params.get("q", "")
        restaurants_query = db.query(models.RestaurantOwner).filter(models.RestaurantOwner.is_verified == True)
        if query_str:
            restaurants_query = restaurants_query.join(models.MenuItem).filter(
                (models.RestaurantOwner.restaurant_name.ilike(f"%{query_str}%")) |
                (models.MenuItem.name.ilike(f"%{query_str}%"))
            ).distinct()
        restaurants = restaurants_query.all()
        orders = db.query(models.Order).filter(models.Order.customer_id == customer.user_id).order_by(models.Order.placed_at.desc()).all()
        tickets = db.query(models.SupportTicket).filter(models.SupportTicket.customer_id == customer.user_id).order_by(models.SupportTicket.created_at.desc()).all()
        chats = db.query(models.ChatMessage).order_by(models.ChatMessage.timestamp.asc()).all()
        return templates.TemplateResponse(request=request, name="customer.html", context={"request": request, "role": role, "customer": customer, "restaurants": restaurants, "orders": orders, "tickets": tickets, "chats": chats})
    
    elif role == "restaurant_owner":
        restaurant = db.query(models.RestaurantOwner).filter(models.RestaurantOwner.user_id == user.user_id).first()
        orders = db.query(models.Order).filter(models.Order.restaurant_id == restaurant.restaurant_id).order_by(models.Order.placed_at.desc()).all()
        chats = db.query(models.ChatMessage).order_by(models.ChatMessage.timestamp.asc()).all()
        agents = db.query(models.DeliveryAgent).filter(models.DeliveryAgent.is_available == True).all()
        return templates.TemplateResponse(request=request, name="restaurant.html", context={"request": request, "role": role, "restaurant": restaurant, "orders": orders, "chats": chats, "agents": agents})
        
    elif role == "delivery_agent":
        agent = db.query(models.DeliveryAgent).filter(models.DeliveryAgent.user_id == user.user_id).first()
        orders = db.query(models.Order).filter(models.Order.agent_id == agent.agent_id).order_by(models.Order.placed_at.desc()).all()
        chats = db.query(models.ChatMessage).order_by(models.ChatMessage.timestamp.asc()).all()
        return templates.TemplateResponse(request=request, name="agent.html", context={"request": request, "role": role, "agent": agent, "orders": orders, "chats": chats})
        
    elif role == "customer_support":
        support = db.query(models.CustomerSupport).filter(models.CustomerSupport.user_id == user.user_id).first()
        tickets = db.query(models.SupportTicket).order_by(models.SupportTicket.created_at.desc()).all()
        unverified_restaurants = db.query(models.RestaurantOwner).filter(models.RestaurantOwner.is_verified == False).all()
        chats = db.query(models.ChatMessage).order_by(models.ChatMessage.timestamp.asc()).all()
        return templates.TemplateResponse(request=request, name="support.html", context={"request": request, "role": role, "support": support, "tickets": tickets, "unverified_restaurants": unverified_restaurants, "chats": chats})
        
    return RedirectResponse(url="/web/login")

@router.post("/web/profile/update")
def profile_update(request: Request, name: str = Form(...), phone: str = Form(...), db: Session = Depends(get_db)):
    user, _ = get_current_user(request, db)
    if user:
        user.name = name
        user.phone = phone
        db.commit()
        return RedirectResponse(url="/web/dashboard?success=profile_updated", status_code=status.HTTP_302_FOUND)
    return RedirectResponse(url="/web/login")

# --- CUSTOMER ACTIONS ---
@router.post("/web/customer/order")
def customer_order(request: Request, item_id: str = Form(...), delivery_address: str = Form(...), special_instructions: str = Form(None), db: Session = Depends(get_db)):
    user, _ = get_current_user(request, db)
    if not user: return RedirectResponse(url="/web/login")
    
    menu_item = db.query(models.MenuItem).filter(models.MenuItem.item_id == item_id).first()
    
    new_order = models.Order(
        order_id=str(uuid.uuid4())[:8],
        customer_id=user.user_id,
        restaurant_id=menu_item.restaurant_id,
        status="PENDING",
        total_amount=menu_item.price,
        special_instructions=special_instructions,
        delivery_address=delivery_address
    )
    db.add(new_order)
    db.commit()
    
    order_item = models.OrderMenuItem(order_id=new_order.order_id, item_id=item_id, quantity=1)
    db.add(order_item)
    db.commit()
    
    return RedirectResponse(url="/web/dashboard", status_code=status.HTTP_302_FOUND)

@router.post("/web/customer/pay")
def customer_pay(request: Request, order_id: str = Form(...), db: Session = Depends(get_db)):
    user, _ = get_current_user(request, db)
    customer = db.query(models.Customer).filter(models.Customer.user_id == user.user_id).first()
    order = db.query(models.Order).filter(models.Order.order_id == order_id).first()
    if order and customer:
        if customer.wallet_balance >= order.total_amount:
            customer.wallet_balance -= order.total_amount
            order.status = "CONFIRMED"
            payment = models.Payment(
                payment_id=str(uuid.uuid4())[:8],
                order_id=order_id,
                amount=order.total_amount,
                method="WALLET",
                status="SUCCESS"
            )
            db.add(payment)
            db.commit()
            return RedirectResponse(url="/web/dashboard?success=payment_successful", status_code=status.HTTP_302_FOUND)
        else:
            return RedirectResponse(url="/web/dashboard?error=insufficient_funds", status_code=status.HTTP_302_FOUND)
    return RedirectResponse(url="/web/dashboard", status_code=status.HTTP_302_FOUND)

@router.post("/web/customer/ticket")
def customer_ticket(request: Request, order_id: str = Form(...), db: Session = Depends(get_db)):
    user, _ = get_current_user(request, db)
    ticket = models.SupportTicket(
        ticket_id=str(uuid.uuid4())[:8],
        customer_id=user.user_id,
        order_id=order_id,
        issue_type="ORDER",
        description="Customer raised an issue via the OOP Web UI module concerning state mismatch.",
        status="OPEN"
    )
    db.add(ticket)
    db.commit()
    return RedirectResponse(url="/web/dashboard", status_code=status.HTTP_302_FOUND)

# --- RESTAURANT ACTIONS ---
@router.post("/web/restaurant/accept")
def restaurant_accept(order_id: str = Form(...), db: Session = Depends(get_db)):
    order = db.query(models.Order).filter(models.Order.order_id == order_id).first()
    if order:
        order.status = "ACCEPTED"
        db.commit()
    return RedirectResponse(url="/web/dashboard", status_code=status.HTTP_302_FOUND)

@router.post("/web/restaurant/prepare")
def restaurant_prepare(order_id: str = Form(...), agent_id: str = Form(...), db: Session = Depends(get_db)):
    order = db.query(models.Order).filter(models.Order.order_id == order_id).first()
    if order:
        order.status = "PREPARING"
        order.agent_id = agent_id
        db.commit()
    return RedirectResponse(url="/web/dashboard", status_code=status.HTTP_302_FOUND)

# --- AGENT ACTIONS ---
@router.post("/web/agent/pickup")
def agent_pickup(order_id: str = Form(...), db: Session = Depends(get_db)):
    order = db.query(models.Order).filter(models.Order.order_id == order_id).first()
    if order:
        order.status = "OUT_FOR_DELIVERY"
        db.commit()
    return RedirectResponse(url="/web/dashboard", status_code=status.HTTP_302_FOUND)

@router.post("/web/agent/deliver")
def agent_deliver(order_id: str = Form(...), db: Session = Depends(get_db)):
    order = db.query(models.Order).filter(models.Order.order_id == order_id).first()
    if order:
        order.status = "DELIVERED"
        db.commit()
    return RedirectResponse(url="/web/dashboard", status_code=status.HTTP_302_FOUND)

# --- SUPPORT ACTIONS ---
@router.post("/web/support/resolve")
def support_resolve(ticket_id: str = Form(...), db: Session = Depends(get_db)):
    ticket = db.query(models.SupportTicket).filter(models.SupportTicket.ticket_id == ticket_id).first()
    if ticket:
        ticket.resolve_ticket()
        
        # OOP flow: Refund payment if linked to order
        if ticket.order_id:
            payment = db.query(models.Payment).filter(models.Payment.order_id == ticket.order_id).first()
            if payment:
                payment.refund()
        db.commit()
    return RedirectResponse(url="/web/dashboard", status_code=status.HTTP_302_FOUND)

@router.post("/web/support/verify")
def support_verify(restaurant_id: str = Form(...), db: Session = Depends(get_db)):
    restaurant = db.query(models.RestaurantOwner).filter(models.RestaurantOwner.restaurant_id == restaurant_id).first()
    if restaurant:
        restaurant.verify_restaurant()
        db.commit()
    return RedirectResponse(url="/web/dashboard", status_code=status.HTTP_302_FOUND)

@router.post("/web/restaurant/add_menu")
def restaurant_add_menu(request: Request, name: str = Form(...), description: str = Form(...), price: float = Form(...), db: Session = Depends(get_db)):
    user, _ = get_current_user(request, db)
    restaurant = db.query(models.RestaurantOwner).filter(models.RestaurantOwner.user_id == user.user_id).first()
    if restaurant and restaurant.is_verified:
        new_item = models.MenuItem(
            item_id=str(uuid.uuid4())[:8],
            restaurant_id=restaurant.restaurant_id,
            name=name,
            description=description,
            price=price,
            category="General",
            is_available=True
        )
        db.add(new_item)
        db.commit()
    return RedirectResponse(url="/web/dashboard", status_code=status.HTTP_302_FOUND)

@router.post("/web/customer/recharge")
def customer_recharge(request: Request, amount: float = Form(...), db: Session = Depends(get_db)):
    user, _ = get_current_user(request, db)
    customer = db.query(models.Customer).filter(models.Customer.user_id == user.user_id).first()
    if customer:
        customer.wallet_balance += amount
        db.commit()
    return RedirectResponse(url="/web/dashboard", status_code=status.HTTP_302_FOUND)

@router.post("/web/chat/send")
def send_chat(request: Request, context_type: str = Form(...), context_id: str = Form(...), content: str = Form(...), db: Session = Depends(get_db)):
    user, _ = get_current_user(request, db)
    msg = models.ChatMessage(
        msg_id=str(uuid.uuid4())[:8],
        sender_id=user.user_id,
        context_type=context_type,
        context_id=context_id,
        content=content
    )
    db.add(msg)
    db.commit()
    return RedirectResponse(url="/web/dashboard", status_code=status.HTTP_302_FOUND)

@router.post("/web/customer/rate")
def customer_rate(request: Request, order_id: str = Form(...), restaurant_stars: int = Form(...), agent_stars: int = Form(...), db: Session = Depends(get_db)):
    user, _ = get_current_user(request, db)
    order = db.query(models.Order).filter(models.Order.order_id == order_id).first()
    if order:
        db.add(models.Rating(
            rating_id=str(uuid.uuid4())[:8],
            order_id=order_id,
            customer_id=user.user_id,
            target_type="RESTAURANT",
            target_id=order.restaurant_id,
            stars=restaurant_stars,
            comment="Rated via OOP UI"
        ))
        if order.agent_id:
            db.add(models.Rating(
                rating_id=str(uuid.uuid4())[:8],
                order_id=order_id,
                customer_id=user.user_id,
                target_type="AGENT",
                target_id=order.agent_id,
                stars=agent_stars,
                comment="Rated via OOP UI"
            ))
        db.commit()
    return RedirectResponse(url="/web/dashboard", status_code=status.HTTP_302_FOUND)