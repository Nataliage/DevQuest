import pytest
from httpx import AsyncClient, ASGITransport
from app.main import app

@pytest.mark.asyncio
async def test_validate_commands_invalid_token():
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        response = await ac.post("/api/game/validate-commands", json={
            "level_id": 1,
            "list_commands": ["ESTANTE1", "ESTANTE2", "IF"]
        }, headers={"Authorization": "Bearer INVALIDTOKEN"})

        print("STATUS:", response.status_code)
        print("BODY:", response.json())

    assert response.status_code == 401
