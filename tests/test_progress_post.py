import pytest
from httpx import AsyncClient, ASGITransport
from app.main import app

@pytest.mark.asyncio
async def test_record_progress_with_token():
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        # login
        login_resp = await ac.post("/api/auth/login", json={
            "email": "testuser5@example.com",
            "password": "Test1234!"
        })

        assert login_resp.status_code == 200
        token = login_resp.json()["auth"]

        # registrar progreso
        progress_payload = {
            "level_id": 1,
            "score": 80
        }

        response = await ac.post("/api/progress/", json=progress_payload, headers={
            "Authorization": f"Bearer {token}"
        })

    print("STATUS:", response.status_code)
    print("BODY:", response.json())

    assert response.status_code == 201
    data = response.json()
    assert data["level_id"] == 1
    assert data["score"] == 80
    assert "progress_id" in data
