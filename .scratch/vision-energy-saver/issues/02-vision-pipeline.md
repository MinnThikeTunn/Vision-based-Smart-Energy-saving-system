# 02 — Vision Pipeline & Decoupled Inference Worker

**What to build:** Implement multi-threaded video processing architecture with webcam capture reading frames into a lock-free queue, YOLOv8 person detection worker, and MJPEG video streaming API endpoint.

**Blocked by:** 01 — Project Scaffold & System Configuration

**Status:** ready-for-agent

- [ ] Camera capture thread continuously pulls frames from laptop webcam (index 0) into lock-free single-item `Frame Queue`.
- [ ] `Inference Worker` thread consumes latest frame, runs YOLOv8 person detection, and updates occupant counts and bounding boxes.
- [ ] Rendered frames with bounding box overlays are accessible via `/api/video_feed` MJPEG stream.
- [ ] Performance meets real-time targets (15-30 FPS camera feed without frame lag/buffer buildup).
- [ ] Integration test verifies video capture queue, frame processing, and MJPEG stream response headers.
