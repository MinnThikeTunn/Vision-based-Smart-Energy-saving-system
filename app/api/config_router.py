from fastapi import APIRouter, HTTPException
from app.config.loader import load_settings, save_settings
from app.config.schema import SystemConfiguration

router = APIRouter(prefix="/api/config", tags=["config"])


@router.get("", response_model=SystemConfiguration)
def get_config() -> SystemConfiguration:
    return load_settings()


@router.post("", response_model=SystemConfiguration)
def update_config(new_config: SystemConfiguration) -> SystemConfiguration:
    try:
        save_settings(new_config)
        return new_config
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))
