import pytest
from httpx import AsyncClient, ASGITransport
from app.main import app

@pytest.mark.asyncio
async def test_login_empty_fields():
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        response = await ac.post("/api/auth/login", json={
            "email": "",
            "password": ""
        })
        print("STATUS:", response.status_code)
        print("BODY:", response.json())

    assert response.status_code == 422  # Error de validación esperado por campos vacíos

