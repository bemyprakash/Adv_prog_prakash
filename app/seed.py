from app.database import engine, get_db
from app import models

models.Base.metadata.create_all(bind=engine)

def seed_data():
    db = next(get_db())
    if db.query(models.UserAccount).first():
        print("Database already seeded.")
        return

    # Create Users
    users = [
        models.UserAccount(user_id="cust-001", name="Rahul Sharma", phone="9876543210", email="rahul@foodizz.com", password="password", role="customer"),
        models.UserAccount(user_id="rest-001", name="Priya Desai", phone="9876543211", email="priya@foodizz.com", password="password", role="restaurant_owner"),
        models.UserAccount(user_id="rest-002", name="Sameer Kapoor", phone="9876543212", email="sameer@foodizz.com", password="password", role="restaurant_owner"),
        models.UserAccount(user_id="agent-001", name="Vikram Singh", phone="9876543213", email="vikram@foodizz.com", password="password", role="delivery_agent"),
        models.UserAccount(user_id="supp-001", name="Anjali Verma", phone="9876543214", email="anjali@foodizz.com", password="password", role="customer_support"),
    ]
    db.add_all(users)
    db.commit()

    # Create Customer Profile
    db.add(models.Customer(user_id="cust-001", wallet_balance=500.0, loyalty_points=50))

    # Create Restaurant Profiles
    db.add(models.RestaurantOwner(user_id="rest-001", restaurant_id="r-001", restaurant_name="Spice Route", opening_hours="10:00-23:00", is_verified=True))
    db.add(models.RestaurantOwner(user_id="rest-002", restaurant_id="r-002", restaurant_name="Bombay Street Treats", opening_hours="09:00-22:00", is_verified=False))
    db.commit()

    # Create Delivery Agent Profile
    db.add(models.DeliveryAgent(user_id="agent-001", agent_id="d-001", vehicle_type="Motorcycle - Splendor", current_location="Connaught Place", is_available=True))

    # Create Support Profile
    db.add(models.CustomerSupport(user_id="supp-001", support_id="s-001", department="General Queries", availability_status="AVAILABLE"))
    db.commit()

    # Add Authentic Indian Menu Items
    menu_items = [
        models.MenuItem(item_id="m-001", restaurant_id="r-001", name="Paneer Butter Masala", description="Rich and creamy paneer curry in a tomato gravy.", price=280.0, category="Main Course", is_available=True),
        models.MenuItem(item_id="m-002", restaurant_id="r-001", name="Garlic Naan", description="Soft traditional flatbread infused with fresh garlic.", price=60.0, category="Breads", is_available=True),
        models.MenuItem(item_id="m-003", restaurant_id="r-001", name="Chicken Tikka Biryani", description="Aromatic basmati rice cooked with marinated chicken tikka chunks.", price=350.0, category="Main Course", is_available=True),
        
        models.MenuItem(item_id="m-004", restaurant_id="r-002", name="Vada Pav", description="Mumbai's iconic street food: fried potato dumpling inside a bread bun.", price=45.0, category="Snacks", is_available=True),
        models.MenuItem(item_id="m-005", restaurant_id="r-002", name="Pav Bhaji", description="Thick vegetable curry served with soft buttered buns.", price=120.0, category="Main Course", is_available=True),
    ]
    db.add_all(menu_items)
    db.commit()

    print("DB Seeded perfectly with rich Indian localization data!")

if __name__ == "__main__":
    seed_data()
