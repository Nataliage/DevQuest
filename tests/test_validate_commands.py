import pytest
from httpx import AsyncClient, ASGITransport
from app.main import app

@pytest.mark.asyncio
async def test_validate_commands_with_token():
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        # login
        login_resp = await ac.post("/api/auth/login", json={
            "email": "testuser5@example.com",
            "password": "Test1234!"
        })

        assert login_resp.status_code == 200
        token = login_resp.json()["auth"]

        # enviar comandos para validación
        commands_payload = {
            "level_id": 1,
            "list_commands": ["ESTANTE1", "ESTANTE2", "IF"]
        }

        response = await ac.post("/api/game/validate-commands", json=commands_payload, headers={
            "Authorization": f"Bearer {token}"
        })

    print("STATUS:", response.status_code)
    print("BODY:", response.json())

    assert response.status_code == 200
    data = response.json()
    assert "stars" in data
    assert isinstance(data["stars"], int)
