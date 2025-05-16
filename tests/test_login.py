import pytest
from httpx import AsyncClient, ASGITransport
from fastapi import FastAPI
from app.main import app

@pytest.mark.asyncio
async def test_login_success():
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        response = await ac.post("/api/auth/login", json={
            "email": "testuser5@example.com",
            "password": "Test1234!"
        })
    assert response.status_code == 200
    data = response.json()
    assert "auth" in data
    assert "email" in data
    assert data["email"] == "testuser5@example.com"