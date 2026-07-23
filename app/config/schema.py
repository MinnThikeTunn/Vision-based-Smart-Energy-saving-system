from typing import Dict
from pydantic import BaseModel, Field


class CameraConfig(BaseModel):
    index: int = Field(default=0, description="Camera index or device path")
    width: int = Field(default=640, description="Capture width")
    height: int = Field(default=480, description="Capture height")
    fps: int = Field(default=30, description="Target capture FPS")


class DetectorConfig(BaseModel):
    model_name: str = Field(default="yolov8n.pt", description="YOLO model variant")
    confidence_threshold: float = Field(default=0.5, ge=0.0, le=1.0)
    device: str = Field(default="cpu", description="Inference device (cpu, cuda)")


class OccupancyConfig(BaseModel):
    persistence_window_sec: int = Field(default=5, ge=0)
    empty_timeout_sec: int = Field(default=180, ge=0)


class DeviceRuleConfig(BaseModel):
    enabled: bool = Field(default=True)
    empty_shutdown_timeout_sec: int = Field(default=180, ge=0)


class SystemConfiguration(BaseModel):
    camera: CameraConfig = Field(default_factory=CameraConfig)
    detector: DetectorConfig = Field(default_factory=DetectorConfig)
    occupancy: OccupancyConfig = Field(default_factory=OccupancyConfig)
    devices: Dict[str, DeviceRuleConfig] = Field(
        default_factory=lambda: {
            "light": DeviceRuleConfig(empty_shutdown_timeout_sec=180),
            "fan": DeviceRuleConfig(empty_shutdown_timeout_sec=600),
            "ac": DeviceRuleConfig(empty_shutdown_timeout_sec=600),
        }
    )
