from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from . import models, seed
from .database import engine


# Create all tables
models.Base.metadata.create_all(bind=engine)

app = FastAPI(title="Food Delivery System", description="OOP-based food delivery backend with customer support.")

# Mount static files
app.mount("/static", StaticFiles(directory="app/static"), name="static")
# Import and include routers
from .routers import auth, customer, restaurant, agent, support, admin, order, payment, ticket

app.include_router(auth.router)
app.include_router(customer.router)
app.include_router(restaurant.router)
app.include_router(agent.router)
app.include_router(support.router)
app.include_router(admin.router)
app.include_router(order.router)
app.include_router(payment.router)
app.include_router(ticket.router)

from .routers import webui
app.include_router(webui.router)

@app.on_event("startup")
def startup_event():
    seed.seed_data()

@app.get("/")
def root():
    return {"message": "Food Delivery System API is running."}
