from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)


def test_dashboard_index_route():
    response = client.get("/")
    assert response.status_code == 200
    assert "Vision Smart Energy Saver" in response.text
