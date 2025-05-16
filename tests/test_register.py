import pytest
import uuid
from httpx import AsyncClient, ASGITransport
from app.main import app

@pytest.mark.asyncio
async def test_register_success():
    unique_email = f"test_{uuid.uuid4().hex[:8]}@example.com"
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        response = await ac.post("/api/auth/register", json={
            "email": unique_email,
            "password": "Test1234!",
            "username": "TestUserPrueba"
        })
        print("STATUS:", response.status_code)
        print("BODY:", response.json())
    assert response.status_code == 201
    data = response.json()
    assert "auth" in data
    assert "email" in data
    assert data["email"] == unique_email
