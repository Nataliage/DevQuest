import pytest
import uuid
from httpx import AsyncClient, ASGITransport
from app.main import app

@pytest.mark.asyncio
async def test_login_invalid_credentials():
    # Generamos un email aleatorio que seguramente no existe
    unique_email = f"invalid_{uuid.uuid4().hex[:8]}@example.com"

    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        response = await ac.post("/api/auth/login", json={
            "email": unique_email,
            "password": "ContraseñaFalsa123!"
        })

    print("STATUS:", response.status_code)
    print("BODY:", response.json())

    assert response.status_code == 401
    data = response.json()
    assert "detail" in data
    assert data["detail"] == "Credenciales inválidas"
