"""
Production-Grade Prometheus Metrics Registry for Vision Smart Energy System.

This module implements OpenMetrics-standard metrics using the official prometheus_client
library, providing proper metric types (Counter, Gauge, Histogram) with labels for
granular observability and Grafana dashboard integration.

Metrics exposed:
  - Counter: Cumulative values that only increase (energy saved, device toggles)
  - Gauge: Point-in-time values that can go up or down (occupancy, power draw)
  - Histogram: Distribution of values (inference latency, frame processing time)

Reference: https://prometheus.io/docs/instrumenting/exposition_formats/
"""

import time
from typing import Dict, Any, Optional
from prometheus_client import (
    Counter,
    Gauge,
    Histogram,
    Info,
    CollectorRegistry,
    generate_latest,
    CONTENT_TYPE_LATEST,
    REGISTRY,
)
from prometheus_client.utils import INF


class MetricsRegistry:
    """
    Production-grade Prometheus metrics registry for the Vision Smart Energy System.

    Uses prometheus_client for proper OpenMetrics format output with:
    - Counter: For cumulative metrics (energy saved, device events)
    - Gauge: For point-in-time values (occupancy, power)
    - Histogram: For latency distributions (inference time, frame processing)
    - Info: For build/version information
    """

    def __init__(self, registry: Optional[CollectorRegistry] = None) -> None:
        """
        Initialize metrics registry.
        
        Args:
            registry: Optional custom CollectorRegistry. If None, uses the global REGISTRY.
                      Pass a custom registry for testing to avoid duplicate metric errors.
        """
        self.registry = registry if registry is not None else REGISTRY
        self._metrics: Dict[str, Any] = {}
        self._setup_build_info()
        self._setup_occupancy_metrics()
        self._setup_device_metrics()
        self._setup_energy_metrics()
        self._setup_inference_metrics()

    def _setup_build_info(self) -> None:
        """Create build/version info metric for service identification."""
        self.build_info = Info(
            "vision_energy_saver_build",
            "Build and version information for the Vision Smart Energy System",
            registry=self.registry,
        )
        self.build_info.info({
            "version": "2.0.0",
            "service": "vision_smart_energy",
            "detector": "yolov8",
            "architecture": "privacy_first",
        })

    def _setup_occupancy_metrics(self) -> None:
        """Create occupancy-related metrics."""
        # Gauge: Current number of detected occupants
        self.occupant_count = Gauge(
            "occupancy_person_count",
            "Live detected occupant count in camera view",
            registry=self.registry,
        )

        # Gauge: Room occupancy status (1=OCCUPIED, 0=EMPTY)
        self.room_occupied = Gauge(
            "room_occupied_status",
            "Numeric room occupancy status (1 = Occupied, 0 = Empty)",
            registry=self.registry,
        )

        # Gauge: Duration the room has been empty (seconds)
        self.empty_duration = Gauge(
            "room_empty_duration_seconds",
            "Elapsed time in seconds since last occupant detected",
            registry=self.registry,
        )

        # Counter: Total occupancy state transitions
        self.occupancy_transitions_total = Counter(
            "occupancy_transitions_total",
            "Total number of occupancy state transitions",
            ["from_state", "to_state"],
            registry=self.registry,
        )

    def _setup_device_metrics(self) -> None:
        """Create device control and state metrics."""
        # Gauge: Current device state (0=OFF, 1=ON, 2=DIM)
        self.device_state = Gauge(
            "device_state",
            "Current device state (0=OFF, 1=ON, 2=DIM)",
            ["device_id", "zone"],
            registry=self.registry,
        )

        # Gauge: Device power percentage (0-100)
        self.device_power_pct = Gauge(
            "device_power_percentage",
            "Current power percentage for device (0-100)",
            ["device_id"],
            registry=self.registry,
        )

        # Counter: Device toggle events
        self.device_toggles_total = Counter(
            "device_toggles_total",
            "Total number of device state toggle events",
            ["device_id", "action", "reason"],
            registry=self.registry,
        )

        # Gauge: Active devices count
        self.active_devices = Gauge(
            "active_devices_count",
            "Number of currently active appliances (ON/DIM)",
            registry=self.registry,
        )

        # Gauge: Countdown timer per device until shutoff
        self.device_shutdown_countdown = Gauge(
            "device_shutdown_countdown_seconds",
            "Seconds remaining until device auto-shutdown",
            ["device_id"],
            registry=self.registry,
        )

    def _setup_energy_metrics(self) -> None:
        """Create energy and power consumption metrics."""
        # Gauge: Current real-time power draw
        self.current_power_watts = Gauge(
            "current_power_consumption_watts",
            "Total real-time power draw across active appliances in watts",
            registry=self.registry,
        )

        # Gauge: Baseline power for comparison
        self.baseline_power_watts = Gauge(
            "baseline_power_watts",
            "Baseline power consumption if all devices were always ON",
            registry=self.registry,
        )

        # Counter: Cumulative energy saved in kWh
        self.energy_kwh_saved = Counter(
            "energy_kwh_saved_total",
            "Cumulative energy saved in kilowatt-hours vs always-ON baseline",
            registry=self.registry,
        )

        # Counter: Cumulative cost saved in USD
        self.energy_cost_saved_usd = Counter(
            "energy_cost_saved_usd_total",
            "Cumulative energy cost saved in USD vs always-ON baseline",
            registry=self.registry,
        )

        # Counter: Cumulative CO2 emissions prevented
        self.energy_co2_saved_kg = Counter(
            "energy_co2_saved_kg_total",
            "Cumulative CO2 emissions prevented in kilograms",
            registry=self.registry,
        )

        # Gauge: Energy efficiency percentage
        self.energy_efficiency_pct = Gauge(
            "energy_efficiency_percentage",
            "Energy efficiency gain percentage vs baseline",
            registry=self.registry,
        )

    def _setup_inference_metrics(self) -> None:
        """Create inference and performance metrics."""
        # Gauge: Current FPS
        self.fps = Gauge(
            "vision_fps",
            "Current video inference frame rate per second",
            registry=self.registry,
        )

        # Histogram: Inference latency distribution
        self.inference_latency = Histogram(
            "vision_inference_latency_seconds",
            "Time spent on YOLO inference per frame in seconds",
            buckets=(0.01, 0.02, 0.05, 0.1, 0.15, 0.2, 0.3, 0.5, 1.0, INF),
            registry=self.registry,
        )

        # Histogram: Frame processing latency (capture + inference + rendering)
        self.frame_processing_latency = Histogram(
            "vision_frame_processing_seconds",
            "Total frame processing latency in seconds (capture + inference + rendering)",
            buckets=(0.02, 0.05, 0.1, 0.15, 0.2, 0.3, 0.5, 1.0, 2.0, INF),
            registry=self.registry,
        )

        # Counter: Frames processed
        self.frames_processed_total = Counter(
            "vision_frames_processed_total",
            "Total number of video frames processed",
            registry=self.registry,
        )

        # Counter: Person detections
        self.person_detections_total = Counter(
            "vision_person_detections_total",
            "Total number of person detections across all frames",
            registry=self.registry,
        )

        # Histogram: WebSocket message latency
        self.websocket_latency = Histogram(
            "websocket_message_latency_seconds",
            "Time to process and send WebSocket telemetry messages",
            buckets=(0.001, 0.005, 0.01, 0.025, 0.05, 0.1, 0.25, 0.5, INF),
            registry=self.registry,
        )

    def update_telemetry(
        self,
        fps: float,
        occupant_count: int,
        room_status: str,
        device_states: Dict[str, str],
        energy_metrics: Dict[str, Any],
        device_telemetry: Optional[Dict[str, Dict[str, Any]]] = None,
        spatial_zones: Optional[Dict[str, str]] = None,
    ) -> None:
        """
        Update all metrics with current telemetry data.

        Args:
            fps: Current inference frame rate
            occupant_count: Number of detected persons
            room_status: "OCCUPIED" or "EMPTY"
            device_states: Dict of device_id -> state (ON/OFF/DIM)
            energy_metrics: Dict with energy savings data
            device_telemetry: Optional dict of device_id -> {power_pct, ...}
            spatial_zones: Optional dict of device_id -> zone_name
        """
        # Update occupancy metrics
        self.fps.set(fps)
        self.occupant_count.set(occupant_count)
        self.room_occupied.set(1 if room_status == "OCCUPIED" else 0)

        # Update device metrics
        active_count = sum(1 for state in device_states.values() if state.upper() in ["ON", "DIM"])
        self.active_devices.set(active_count)

        for device_id, state in device_states.items():
            state_val = {"OFF": 0, "ON": 1, "DIM": 2}.get(state.upper(), 0)
            zone = spatial_zones.get(device_id, "unknown") if spatial_zones else "unknown"
            self.device_state.labels(device_id=device_id, zone=zone).set(state_val)

            if device_telemetry and device_id in device_telemetry:
                power_pct = device_telemetry[device_id].get("power_pct", 0)
                self.device_power_pct.labels(device_id=device_id).set(power_pct)

        # Update energy metrics
        if energy_metrics:
            current_power = energy_metrics.get("current_power_watts", 0.0)
            baseline_power = energy_metrics.get("baseline_power_watts", 1305.0)
            
            self.current_power_watts.set(current_power)
            self.baseline_power_watts.set(baseline_power)
            self.energy_efficiency_pct.set(energy_metrics.get("energy_efficiency_pct", 0.0))

    def increment_energy_savings(
        self,
        kwh_saved: float,
        cost_saved_usd: float,
        co2_saved_kg: float,
    ) -> None:
        """
        Increment cumulative energy savings counters.

        These should be called with the delta (incremental) values,
        not the cumulative totals.
        """
        if kwh_saved > 0:
            self.energy_kwh_saved.inc(kwh_saved)
        if cost_saved_usd > 0:
            self.energy_cost_saved_usd.inc(cost_saved_usd)
        if co2_saved_kg > 0:
            self.energy_co2_saved_kg.inc(co2_saved_kg)

    def record_device_toggle(
        self,
        device_id: str,
        action: str,
        reason: str,
    ) -> None:
        """Record a device toggle event."""
        self.device_toggles_total.labels(
            device_id=device_id,
            action=action.upper(),
            reason=reason,
        ).inc()

    def record_occupancy_transition(
        self,
        from_state: str,
        to_state: str,
    ) -> None:
        """Record an occupancy state transition."""
        self.occupancy_transitions_total.labels(
            from_state=from_state.upper(),
            to_state=to_state.upper(),
        ).inc()

    def observe_inference_latency(self, latency_seconds: float) -> None:
        """Observe inference latency for histogram."""
        self.inference_latency.observe(latency_seconds)
        self.frames_processed_total.inc()

    def observe_frame_processing(self, latency_seconds: float) -> None:
        """Observe total frame processing latency."""
        self.frame_processing_latency.observe(latency_seconds)

    def observe_person_detection(self, count: int = 1) -> None:
        """Record person detections."""
        self.person_detections_total.inc(count)

    def observe_websocket_latency(self, latency_seconds: float) -> None:
        """Observe WebSocket message processing latency."""
        self.websocket_latency.observe(latency_seconds)

    def set_empty_duration(self, seconds: float) -> None:
        """Set the empty room duration."""
        self.empty_duration.set(seconds)

    def set_device_countdown(self, device_id: str, seconds: float) -> None:
        """Set device shutdown countdown."""
        self.device_shutdown_countdown.labels(device_id=device_id).set(seconds)

    def generate_prometheus_metrics(self) -> bytes:
        """
        Generate Prometheus/OpenMetrics format output.

        Returns bytes for proper content-type handling in FastAPI.
        """
        return generate_latest(self.registry)

    def get_content_type(self) -> str:
        """Return the proper content type for Prometheus metrics."""
        return CONTENT_TYPE_LATEST


# Global singleton registry instance (uses global REGISTRY)
_global_metrics: Optional[MetricsRegistry] = None


def get_metrics_registry() -> MetricsRegistry:
    """
    Get the global metrics registry instance.

    Creates the registry on first call (lazy initialization).
    """
    global _global_metrics
    if _global_metrics is None:
        _global_metrics = MetricsRegistry(registry=CollectorRegistry())
    return _global_metrics



def create_metrics_registry() -> MetricsRegistry:
    """
    Create a new MetricsRegistry with its own CollectorRegistry.
    
    Use this for testing or when you need isolated metrics collection.
    """
    return MetricsRegistry(registry=CollectorRegistry())


def reset_metrics_registry() -> None:
    """
    Reset the global metrics registry (primarily for testing).
    
    Note: This only resets our reference. The prometheus_client global REGISTRY
    still contains the old metrics. For proper test isolation, use
    create_metrics_registry() with a custom CollectorRegistry instead.
    """
    global _global_metrics
    _global_metrics = None
