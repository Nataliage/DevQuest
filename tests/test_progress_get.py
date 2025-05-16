import pytest
from httpx import AsyncClient, ASGITransport
from app.main import app

@pytest.mark.asyncio
async def test_get_progress_with_token():
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        # Paso 1: login
        login_resp = await ac.post("/api/auth/login", json={
            "email": "testuser5@example.com",
            "password": "Test1234!"
        })

        assert login_resp.status_code == 200
        token = login_resp.json()["auth"]

        # Paso 2: obtener progreso
        response = await ac.get("/api/progress/", headers={
            "Authorization": f"Bearer {token}"
        })

    print("STATUS:", response.status_code)
    print("BODY:", response.json())

    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)
    assert any(p["level_id"] == 1 for p in data)
