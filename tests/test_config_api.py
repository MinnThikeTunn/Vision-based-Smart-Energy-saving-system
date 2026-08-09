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


def test_delete_device_via_config_api():
    # Fetch current config
    get_res = client.get("/api/config")
    config = get_res.json()

    # Remove device 'aa' if present
    if "aa" in config.get("devices", {}):
        del config["devices"]["aa"]

    post_res = client.post("/api/config", json=config)
    assert post_res.status_code == 200
    assert "aa" not in post_res.json().get("devices", {})


def test_create_and_delete_custom_device_full_cycle():
    get_res = client.get("/api/config")
    config = get_res.json()

    # Add custom device 'test_lamp'
    config["devices"]["test_lamp"] = {
        "enabled": True,
        "name": "Test Lamp",
        "category": "light",
        "empty_shutdown_timeout_sec": 5,
        "rated_wattage": 40.0,
        "power_ramp_sec": 1.0,
        "assigned_zone": "Zone: Test Lamp"
    }
    config["spatial_zones"].append({
        "name": "Zone: Test Lamp",
        "bbox": [0.1, 0.1, 0.5, 0.5],
        "assigned_devices": ["test_lamp"]
    })

    # Save created device
    post_res = client.post("/api/config", json=config)
    assert post_res.status_code == 200
    assert "test_lamp" in post_res.json()["devices"]

    # Delete custom device 'test_lamp' and its paired zone
    updated_config = post_res.json()
    del updated_config["devices"]["test_lamp"]
    updated_config["spatial_zones"] = [z for z in updated_config["spatial_zones"] if z["name"] != "Zone: Test Lamp"]

    delete_res = client.post("/api/config", json=updated_config)
    assert delete_res.status_code == 200
    assert "test_lamp" not in delete_res.json()["devices"]
    assert not any(z["name"] == "Zone: Test Lamp" for z in delete_res.json()["spatial_zones"])


