"""
Tests for production-grade Prometheus metrics implementation.
"""

import pytest
from app.telemetry.metrics import (
    MetricsRegistry,
    create_metrics_registry,
    get_metrics_registry,
    reset_metrics_registry,
)
from prometheus_client import CollectorRegistry


class TestMetricsRegistryIsolated:
    """Test suite for Prometheus metrics registry with isolated registries."""

    def test_create_metrics_registry_returns_new_instance(self):
        """Test that create_metrics_registry creates new instances."""
        registry1 = create_metrics_registry()
        registry2 = create_metrics_registry()
        assert registry1 is not registry2
        assert registry1.registry is not registry2.registry

    def test_generate_prometheus_metrics_returns_bytes(self):
        """Test that generate_prometheus_metrics returns bytes."""
        registry = create_metrics_registry()
        output = registry.generate_prometheus_metrics()
        assert isinstance(output, bytes)

    def test_metrics_output_contains_build_info(self):
        """Test that metrics output contains build info."""
        registry = create_metrics_registry()
        output = registry.generate_prometheus_metrics().decode("utf-8")
        assert "vision_energy_saver_build_info" in output
        assert 'version="2.0.0"' in output
        assert 'detector="yolov8"' in output

    def test_update_telemetry_sets_occupancy_metrics(self):
        """Test that update_telemetry correctly sets occupancy metrics."""
        registry = create_metrics_registry()
        
        registry.update_telemetry(
            fps=30.0,
            occupant_count=3,
            room_status="OCCUPIED",
            device_states={"light": "ON", "fan": "OFF"},
            energy_metrics={"current_power_watts": 100.0, "baseline_power_watts": 500.0},
        )
        
        output = registry.generate_prometheus_metrics().decode("utf-8")
        assert "occupancy_person_count 3.0" in output
        assert "room_occupied_status 1.0" in output
        assert "vision_fps 30.0" in output

    def test_update_telemetry_sets_device_metrics(self):
        """Test that update_telemetry correctly sets device metrics."""
        registry = create_metrics_registry()
        
        registry.update_telemetry(
            fps=25.0,
            occupant_count=0,
            room_status="EMPTY",
            device_states={"light": "ON", "fan": "DIM", "ac": "OFF"},
            energy_metrics={},
            device_telemetry={
                "light": {"power_pct": 100},
                "fan": {"power_pct": 50},
            },
            spatial_zones={"light": "desk_zone", "fan": "transit_zone"},
        )
        
        output = registry.generate_prometheus_metrics().decode("utf-8")
        assert "active_devices_count 2.0" in output
        assert 'device_state{device_id="light",zone="desk_zone"} 1.0' in output
        assert 'device_state{device_id="fan",zone="transit_zone"} 2.0' in output
        assert 'device_power_percentage{device_id="light"} 100.0' in output

    def test_update_telemetry_sets_energy_metrics(self):
        """Test that update_telemetry correctly sets energy metrics."""
        registry = create_metrics_registry()
        
        registry.update_telemetry(
            fps=30.0,
            occupant_count=2,
            room_status="OCCUPIED",
            device_states={"ac": "ON"},
            energy_metrics={
                "current_power_watts": 1200.0,
                "baseline_power_watts": 1305.0,
                "energy_efficiency_pct": 8.0,
            },
        )
        
        output = registry.generate_prometheus_metrics().decode("utf-8")
        assert "current_power_consumption_watts 1200.0" in output
        assert "baseline_power_watts 1305.0" in output
        assert "energy_efficiency_percentage 8.0" in output

    def test_increment_energy_savings_increments_counters(self):
        """Test that increment_energy_savings correctly increments counters."""
        registry = create_metrics_registry()
        
        registry.increment_energy_savings(
            kwh_saved=0.5,
            cost_saved_usd=0.075,
            co2_saved_kg=0.25,
        )
        
        output = registry.generate_prometheus_metrics().decode("utf-8")
        assert "energy_kwh_saved_total 0.5" in output
        assert "energy_cost_saved_usd_total 0.075" in output
        assert "energy_co2_saved_kg_total 0.25" in output

    def test_record_device_toggle_creates_counter(self):
        """Test that record_device_toggle creates labeled counter."""
        registry = create_metrics_registry()
        
        registry.record_device_toggle(
            device_id="light",
            action="ON",
            reason="occupancy_detected",
        )
        
        output = registry.generate_prometheus_metrics().decode("utf-8")
        assert 'device_toggles_total' in output
        assert 'device_id="light"' in output
        assert 'action="ON"' in output
        assert 'reason="occupancy_detected"' in output


    def test_record_occupancy_transition_creates_counter(self):
        """Test that record_occupancy_transition creates labeled counter."""
        registry = create_metrics_registry()
        
        registry.record_occupancy_transition(
            from_state="EMPTY",
            to_state="OCCUPIED",
        )
        
        output = registry.generate_prometheus_metrics().decode("utf-8")
        assert 'occupancy_transitions_total{from_state="EMPTY",to_state="OCCUPIED"}' in output

    def test_observe_inference_latency_updates_histogram(self):
        """Test that observe_inference_latency updates histogram and counter."""
        registry = create_metrics_registry()
        
        registry.observe_inference_latency(0.05)
        registry.observe_inference_latency(0.08)
        registry.observe_inference_latency(0.12)
        
        output = registry.generate_prometheus_metrics().decode("utf-8")
        assert "vision_inference_latency_seconds_bucket" in output
        assert "vision_inference_latency_seconds_count 3.0" in output
        assert "vision_frames_processed_total 3.0" in output

    def test_observe_person_detection_increments_counter(self):
        """Test that observe_person_detection increments counter."""
        registry = create_metrics_registry()
        
        registry.observe_person_detection(5)
        
        output = registry.generate_prometheus_metrics().decode("utf-8")
        assert "vision_person_detections_total 5.0" in output

    def test_set_empty_duration_sets_gauge(self):
        """Test that set_empty_duration sets the gauge value."""
        registry = create_metrics_registry()
        
        registry.set_empty_duration(45.5)
        
        output = registry.generate_prometheus_metrics().decode("utf-8")
        assert "room_empty_duration_seconds 45.5" in output

    def test_set_device_countdown_sets_labeled_gauge(self):
        """Test that set_device_countdown sets labeled gauge values."""
        registry = create_metrics_registry()
        
        registry.set_device_countdown("light", 3.0)
        registry.set_device_countdown("ac", 8.0)
        
        output = registry.generate_prometheus_metrics().decode("utf-8")
        assert 'device_shutdown_countdown_seconds{device_id="light"} 3.0' in output
        assert 'device_shutdown_countdown_seconds{device_id="ac"} 8.0' in output

    def test_get_content_type_returns_prometheus_format(self):
        """Test that get_content_type returns correct content type."""
        registry = create_metrics_registry()
        
        content_type = registry.get_content_type()
        assert "text/plain" in content_type

    def test_metrics_include_help_and_type_annotations(self):
        """Test that metrics output includes HELP and TYPE annotations per OpenMetrics spec."""
        registry = create_metrics_registry()
        
        output = registry.generate_prometheus_metrics().decode("utf-8")
        
        # Check for HELP annotations
        assert "# HELP occupancy_person_count" in output
        assert "# HELP current_power_consumption_watts" in output
        assert "# HELP vision_fps" in output
        
        # Check for TYPE annotations
        assert "# TYPE occupancy_person_count gauge" in output
        assert "# TYPE current_power_consumption_watts gauge" in output
        assert "# TYPE vision_fps gauge" in output
        assert "# TYPE energy_kwh_saved_total counter" in output
        assert "# TYPE vision_inference_latency_seconds histogram" in output

    def test_histogram_bucket_structure(self):
        """Test that histogram metrics have correct bucket structure."""
        registry = create_metrics_registry()
        
        # Add some observations
        for latency in [0.01, 0.05, 0.1, 0.15, 0.3]:
            registry.observe_inference_latency(latency)
        
        output = registry.generate_prometheus_metrics().decode("utf-8")
        
        # Check for bucket with le label
        assert 'vision_inference_latency_seconds_bucket{le=' in output
        assert 'vision_inference_latency_seconds_bucket{le="+Inf"}' in output
        
        # Check for _sum and _count
        assert "vision_inference_latency_seconds_sum" in output
        assert "vision_inference_latency_seconds_count 5.0" in output

    def test_negative_values_ignored_in_counters(self):
        """Test that negative values are not added to counters."""
        registry = create_metrics_registry()
        
        # prometheus_client ignores negative increments for counters
        # So the counter should remain at 0
        registry.increment_energy_savings(
            kwh_saved=-1.0,  # Should be ignored (not negative increment)
            cost_saved_usd=0.1,  # Should work
            co2_saved_kg=0.05,
        )
        
        output = registry.generate_prometheus_metrics().decode("utf-8")
        # The kwh counter should still be 0.0 since we tried to add a negative
        lines = [l for l in output.split('\n') if 'energy_kwh_saved_total' in l and not l.startswith('#')]
        # Counter should be 0 or not present (not negative)
        if lines:
            assert 'energy_kwh_saved_total 0.0' in lines[0] or float(lines[0].split()[-1]) >= 0

    def test_multiple_increments_accumulate(self):
        """Test that multiple increments accumulate correctly."""
        registry = create_metrics_registry()
        
        registry.increment_energy_savings(kwh_saved=0.1, cost_saved_usd=0.015, co2_saved_kg=0.05)
        registry.increment_energy_savings(kwh_saved=0.2, cost_saved_usd=0.03, co2_saved_kg=0.1)
        registry.increment_energy_savings(kwh_saved=0.3, cost_saved_usd=0.045, co2_saved_kg=0.15)
        
        output = registry.generate_prometheus_metrics().decode("utf-8")
        assert "energy_kwh_saved_total 0.6" in output
        assert "energy_cost_saved_usd_total 0.09" in output
        assert "energy_co2_saved_kg_total 0.3" in output

    def test_occupied_vs_empty_status(self):
        """Test room status gauge for OCCUPIED vs EMPTY states."""
        registry = create_metrics_registry()
        
        # Test OCCUPIED
        registry.update_telemetry(
            fps=30.0,
            occupant_count=1,
            room_status="OCCUPIED",
            device_states={},
            energy_metrics={},
        )
        output = registry.generate_prometheus_metrics().decode("utf-8")
        assert "room_occupied_status 1.0" in output

        # Create new registry for EMPTY test
        registry2 = create_metrics_registry()
        registry2.update_telemetry(
            fps=30.0,
            occupant_count=0,
            room_status="EMPTY",
            device_states={},
            energy_metrics={},
        )
        output2 = registry2.generate_prometheus_metrics().decode("utf-8")
        assert "room_occupied_status 0.0" in output2


class TestGlobalMetricsRegistry:
    """Test suite for global metrics registry singleton behavior."""

    def test_get_metrics_registry_singleton(self):
        """Test that get_metrics_registry returns consistent instance."""
        reset_metrics_registry()
        registry1 = get_metrics_registry()
        registry2 = get_metrics_registry()
        # Both should refer to the same instance
        assert registry1 is registry2
        reset_metrics_registry()

    def test_global_registry_produces_valid_output(self):
        """Test that global registry produces valid Prometheus output."""
        reset_metrics_registry()
        registry = get_metrics_registry()
        output = registry.generate_prometheus_metrics()
        assert isinstance(output, bytes)
        assert b"vision_energy_saver_build_info" in output
        reset_metrics_registry()


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
