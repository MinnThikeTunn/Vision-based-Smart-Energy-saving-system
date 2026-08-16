# 4. ONNX Inference Cascade, Dynamic TOU Tariffs, Camera Resilience & Zero-Copy Buffers

* Status: Accepted
* Date: 2026-08-17

## Context and Problem Statement

Following the multi-specialist audit and grilling session on the system architecture, several technical and domain gaps were addressed:
1. **Model Runtime Portability & Speed**: Running edge models with PyTorch creates significant CPU latency on low-power devices. A unified cascade is needed to prioritize ONNX Runtime acceleration with seamless fallback to PyTorch and synthetic testing stubs.
2. **Commercial Utility Tariffs**: Commercial facilities are billed under tiered Time-of-Use (TOU) tariffs (Peak, Mid-Peak, Off-Peak) rather than flat 24-hour electricity rates.
3. **Camera Hardware Resilience**: Transient USB disconnects or RTSP network jitter caused capture loops to freeze or crash without self-healing.
4. **Frame Memory Overhead**: Unconstrained frame cloning during capture and MJPEG generation created high heap allocation pressure at 30 FPS.

## Decision Drivers

* Real-time edge latency (<10ms inference per frame).
* Realistic commercial utility tariff modeling matching industrial billing standards.
* Non-stop autonomous operation resilient to hardware drops.
* Zero memory allocations per frame tick in steady-state operation.

## Decision Outcome

Chosen Decisions:
1. **Inference Backend Cascade**: Implement a cascading model loader (`ONNX Runtime -> PyTorch -> DummyDetector`) in `app/detector/person_detector.py` with support for explicit and automatic backend selection.
2. **Dynamic Time-of-Use (TOU) Tariff Engine**: Enhance `app/analytics/energy_calculator.py` with multi-tier hourly pricing schedules, computing dynamic cost savings against current time-of-day tariffs.
3. **Camera Resilience Watchdog**: Implement exponential backoff auto-reconnection in `app/detector/pipeline.py` with synthetic reconnecting frames.
4. **Pre-Allocated Zero-Copy Buffer Pool**: Maintain reusable static frame arrays in `VisionPipeline` utilizing `np.copyto()` instead of dynamic heap `.copy()` allocations.

### Positive Consequences

* Edge hardware achieves maximum FPS throughput with minimal CPU/RAM footprint.
* Energy ROI calculations accurately reflect real-world tiered utility billing structures.
* Physical camera unplug/replug events recover automatically without restarting the application daemon.
* Frame rendering and streaming operate with zero Garbage Collection thrashing.

### Negative Consequences

* Added configuration complexity in `settings.yaml` for TOU tiers (mitigated with sensible defaults).
