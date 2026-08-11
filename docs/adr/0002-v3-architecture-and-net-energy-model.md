# 2. Version 3 Architecture: Net Energy Formula, Decoupled Timers & Modular Engine

* Status: Accepted
* Date: 2026-08-09

## Context and Problem Statement

The multi-specialist audit of Version 2.0 (`notes/`) identified critical architectural and financial flaws:
1. ROI formulas accumulated savings continuous 24/7/365 against an Always-ON baseline while ignoring 30W edge compute server power draw.
2. Individual device shutdown timers (e.g. 5s light timeout) deadlocked behind the macro room state machine timeout (300s).
3. The frontend was a 966-line single-file monolith wiping `.innerHTML` on every 30Hz WebSocket tick, causing layout thrashing.
4. YOLO inference created memory bandwidth thrashing via repeated `frame.copy()` allocations.

## Decision Drivers

* Audit-ready IPMVP financial and CO2e energy accounting.
* Fast, independent device shutdown responsiveness for vacant spatial zones.
* 60 FPS smooth dashboard rendering with zero DOM layout thrashing.
* Minimal RAM/CPU memory bandwidth overhead and ONNX model acceleration.

## Decision Outcome

Chosen Decisions:
1. **Net Energy Formula & Schedule Mask**: Implement $\text{Net Saved kWh} = \text{Baseline} - \text{Actual} - \text{Edge Compute Overhead}$, and add configurable business operating schedule masks (`settings.yaml`).
2. **Decoupled Per-Device Control Matrix**: Allow devices in unoccupied spatial zones to start independent countdown timers immediately after the `Presence Verification Delay` (2s).
3. **Modular Frontend Architecture**: Extract `index.html` into CSS/JS modules, implement keyed DOM diffing, and fix canvas `object-contain` aspect-ratio coordinate projection.
4. **Engine Optimization**: Implement zero-copy double-buffered frame pools, dynamic delta sleeping, Hungarian IoU centroid tracking, $O(1)$ deque event logging, and ONNX FP16 auto-loading with PyTorch fallback.

### Positive Consequences

* Enterprise financial credibility with true net ROI modeling.
* Low-latency device shutoffs when specific zones become vacant.
* Smooth 60 FPS frontend telemetry rendering without memory leaks.
* Reduced YOLO inference latency from ~30ms to <5ms.

### Negative Consequences

* Higher modularity requirement across frontend files (`js/` directory).
* ONNX Runtime dependency requirement (handled with PyTorch fallback).
