from typing import Dict, List
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


class PrivacyConfig(BaseModel):
    headless_mode: bool = Field(default=False, description="Disable video stream for privacy")
    anonymize_faces: bool = Field(default=False, description="Blur persons/faces in video stream")


class SimulationConfig(BaseModel):
    latency_ms: int = Field(default=300, ge=0, description="Startup/shutdown latency delay in ms")
    power_ramp_sec: float = Field(default=1.5, ge=0.0, description="Duration for non-instant power ramp")


class SpatialZoneConfig(BaseModel):
    name: str = Field(..., description="Zone identifier")
    # Normalized bounding box [x_min, y_min, x_max, y_max] from 0.0 to 1.0
    bbox: List[float] = Field(default_factory=lambda: [0.0, 0.0, 1.0, 1.0])
    assigned_devices: List[str] = Field(default_factory=list)


class OccupancyConfig(BaseModel):
    persistence_window_sec: int = Field(default=2, ge=0)
    empty_timeout_sec: int = Field(default=5, ge=0)


class DeviceRuleConfig(BaseModel):
    enabled: bool = Field(default=True)
    empty_shutdown_timeout_sec: int = Field(default=5, ge=0)
    rated_wattage: float = Field(default=50.0, ge=0.0, description="Power rating in Watts")


class AnalyticsConfig(BaseModel):
    electricity_rate_kwh: float = Field(default=0.15, ge=0.0, description="Cost per kWh in USD")
    co2_per_kwh_kg: float = Field(default=0.42, ge=0.0, description="CO2 emission factor kg/kWh")


class SystemConfiguration(BaseModel):
    camera: CameraConfig = Field(default_factory=CameraConfig)
    detector: DetectorConfig = Field(default_factory=DetectorConfig)
    privacy: PrivacyConfig = Field(default_factory=PrivacyConfig)
    simulation: SimulationConfig = Field(default_factory=SimulationConfig)
    occupancy: OccupancyConfig = Field(default_factory=OccupancyConfig)
    analytics: AnalyticsConfig = Field(default_factory=AnalyticsConfig)
    spatial_zones: List[SpatialZoneConfig] = Field(
        default_factory=lambda: [
            SpatialZoneConfig(
                name="Zone A (Desk)",
                bbox=[0.0, 0.0, 0.5, 1.0],
                assigned_devices=["light", "fan"],
            ),
            SpatialZoneConfig(
                name="Zone B (Transit)",
                bbox=[0.5, 0.0, 1.0, 1.0],
                assigned_devices=["ac"],
            ),
        ]
    )
    devices: Dict[str, DeviceRuleConfig] = Field(
        default_factory=lambda: {
            "light": DeviceRuleConfig(empty_shutdown_timeout_sec=5, rated_wattage=40.0),
            "fan": DeviceRuleConfig(empty_shutdown_timeout_sec=10, rated_wattage=65.0),
            "ac": DeviceRuleConfig(empty_shutdown_timeout_sec=10, rated_wattage=1200.0),
        }
    )
