import pytest
from httpx import AsyncClient, ASGITransport
from app.main import app

@pytest.mark.asyncio
async def test_validate_commands_incorrect():
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        # login con un usuario existente
        login_resp = await ac.post("/api/auth/login", json={
            "email": "testuser5@example.com",
            "password": "Test1234!"
        })
        assert login_resp.status_code == 200
        token = login_resp.json()["auth"]

        # enviar comandos incorrectos
        commands_payload = {
            "level_id": 1,
            "list_commands": [
                "ESTANTE3",  # no existe
                "WHILE"      # no es esperado
            ]
        }

        response = await ac.post("/api/game/validate-commands", json=commands_payload, headers={
            "Authorization": f"Bearer {token}"
        })

        print("STATUS:", response.status_code)
        print("BODY:", response.json())

        assert response.status_code == 200
        data = response.json()
        assert data["correct"] is False
        assert data["stars"] == 0
        assert "progress" in data
        assert "levels_completed" in data
