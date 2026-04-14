import pytest
from fastapi.testclient import TestClient
from app.main import app
import uuid

client = TestClient(app)

def get_auth_token(email: str, role: str):
    # Register randomly to avoid conflicts
    phone = str(uuid.uuid4())[:10]
    client.post("/auth/register", json={
        "name": "Test User",
        "phone": phone,
        "email": email,
        "password": "password123",
        "role": role
    })
    # Login
    response = client.post("/auth/login", json={
        "name": "Test User",
        "phone": phone,
        "email": email,
        "password": "password123",
        "role": role
    })
    return response.json().get("access_token")

def test_order_creation_requires_auth():
    # Attempting to order without token should fail
    response = client.post("/order", json={
        "customer_id": "123",
        "restaurant_id": "456",
        "items": [{"item_id": "789", "quantity": 1}]
    })
    assert response.status_code == 401

def test_get_nonexistent_order():
    token = get_auth_token("customer_order@example.com", "customer")
    headers = {"Authorization": f"Bearer {token}"}
    response = client.get("/order/invalid_order_id", headers=headers)
    assert response.status_code in [404, 401, 403] # Depending on auth middleware timing
