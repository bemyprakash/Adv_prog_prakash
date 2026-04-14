import pytest
from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)

def test_register_and_login():
    # Register a new customer
    reg = client.post("/auth/register", json={
        "name": "TestUser",
        "phone": "5555555555",
        "email": "testuser@foodizz.com",
        "password": "testpass",
        "role": "customer"
    })
    assert reg.status_code == 200
    # Login
    login = client.post("/auth/login", json={
        "name": "TestUser",
        "phone": "5555555555",
        "email": "testuser@foodizz.com",
        "password": "testpass",
        "role": "customer"
    })
    assert login.status_code == 200
    data = login.json()
    assert "access_token" in data
    assert data["token_type"] == "bearer"
