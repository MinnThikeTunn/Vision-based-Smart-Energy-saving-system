from pathlib import Path
import yaml
from app.config.schema import SystemConfiguration

DEFAULT_CONFIG_PATH = Path(__file__).parent / "settings.yaml"


def load_settings(path: Path = DEFAULT_CONFIG_PATH) -> SystemConfiguration:
    if not path.exists():
        default_config = SystemConfiguration()
        save_settings(default_config, path)
        return default_config

    with open(path, "r", encoding="utf-8") as f:
        data = yaml.safe_load(f) or {}

    return SystemConfiguration.model_validate(data)


def save_settings(config: SystemConfiguration, path: Path = DEFAULT_CONFIG_PATH) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with open(path, "w", encoding="utf-8") as f:
        yaml.safe_dump(config.model_dump(), f, default_flow_style=False)
