import pytest
from httpx import AsyncClient, ASGITransport
from app.main import app

@pytest.mark.asyncio
async def test_get_level_with_valid_token():
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        #login con usuario ya registrado
        login_resp = await ac.post("/api/auth/login", json={
            "email": "testuser5@example.com",
            "password": "Test1234!"
        })

        assert login_resp.status_code == 200
        token = login_resp.json()["auth"]

        # usar el token para acceder al endpoint protegido
        response = await ac.get("/api/levels/1", headers={
            "Authorization": f"Bearer {token}"
        })

    print("STATUS:", response.status_code)
    print("BODY:", response.json())

    assert response.status_code == 200
    data = response.json()
    assert "level_id" in data
    assert data["level_id"] == 1
