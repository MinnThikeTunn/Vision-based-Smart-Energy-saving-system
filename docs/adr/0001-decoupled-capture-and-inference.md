# 1. Decouple Video Capture and Model Inference via Lock-Free Frame Queue

* Status: Accepted
* Date: 2026-07-23

## Context and Problem Statement

Running real-time YOLOv8 object detection on a live webcam feed synchronously on the main thread causes frame lag and UI/API unresponsiveness when inference frame rates drop below camera input rate.

## Decision Drivers

* Need smooth live video streaming (15-30 FPS) without buffer buildup.
* Keep detection pipeline decoupleable and replaceable.
* Prevent backend API latency from blocking on model inference times.

## Considered Options

1. Synchronous single-threaded loop (Capture -> Infer -> Render -> Stream).
2. Multi-threaded pipeline with decoupled lock-free frame queue.

## Decision Outcome

Chosen Option: Option 2 (Multi-threaded pipeline with decoupled lock-free frame queue).

### Positive Consequences

* Camera capture never blocks on model inference speed.
* Inference drops stale frames automatically by always consuming the latest frame.
* Backend API stays responsive.

### Negative Consequences

* Minor threading complexity and synchronization overhead.
