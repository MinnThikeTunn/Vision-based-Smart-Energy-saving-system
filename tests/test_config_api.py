from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)


def test_get_config_api():
    response = client.get("/api/config")
    assert response.status_code == 200
    data = response.json()
    assert "camera" in data
    assert "detector" in data
    assert "occupancy" in data
    assert "devices" in data


def test_update_config_api():
    get_res = client.get("/api/config")
    assert get_res.status_code == 200
    current_config = get_res.json()

    current_config["occupancy"]["empty_timeout_sec"] = 300
    post_res = client.post("/api/config", json=current_config)
    assert post_res.status_code == 200
    updated = post_res.json()
    assert updated["occupancy"]["empty_timeout_sec"] == 300

    # Verify GET reflects update
    verify_res = client.get("/api/config")
    assert verify_res.json()["occupancy"]["empty_timeout_sec"] == 300
