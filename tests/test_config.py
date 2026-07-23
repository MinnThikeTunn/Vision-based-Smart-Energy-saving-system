import pytest
from app.config.loader import load_settings, save_settings
from app.config.schema import SystemConfiguration


def test_default_config_loading(tmp_path):
    config_file = tmp_path / "settings.yaml"
    config = load_settings(config_file)

    assert isinstance(config, SystemConfiguration)
    assert config.camera.index == 0
    assert config.camera.fps == 30
    assert config.detector.confidence_threshold == 0.5
    assert config.occupancy.persistence_window_sec == 5
    assert config.occupancy.empty_timeout_sec == 180
    assert config.devices["light"].empty_shutdown_timeout_sec == 180
    assert config.devices["fan"].empty_shutdown_timeout_sec == 600
    assert config.devices["ac"].empty_shutdown_timeout_sec == 600


def test_config_save_and_reload(tmp_path):
    config_file = tmp_path / "settings.yaml"
    config = load_settings(config_file)
    
    config.occupancy.empty_timeout_sec = 240
    save_settings(config, config_file)

    reloaded = load_settings(config_file)
    assert reloaded.occupancy.empty_timeout_sec == 240
