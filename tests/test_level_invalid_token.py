import pytest
from httpx import AsyncClient, ASGITransport
from app.main import app

@pytest.mark.asyncio
async def test_get_level_unauthorized():
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        response = await ac.get("/api/levels/1", headers={
            "Authorization": "Bearer invalid_token"
        })

    print("STATUS:", response.status_code)
    print("BODY:", response.json())

    assert response.status_code == 401
    data = response.json()
    assert "detail" in data
    assert data["detail"].startswith("Token inválido")
