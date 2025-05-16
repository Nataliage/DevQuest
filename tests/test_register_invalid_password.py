import pytest
import uuid
from httpx import AsyncClient, ASGITransport
from app.main import app

@pytest.mark.asyncio
async def test_register_invalid_password():
    unique_email = f"test_{uuid.uuid4().hex[:8]}@example.com"
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        response = await ac.post("/api/auth/register", json={
            "email": unique_email,
            "password": "",
            "username": "TestUser"
        })
        print("STATUS:", response.status_code)
        print("BODY:", response.json())

    assert response.status_code == 400  # Se espera error de validación por password vacío
