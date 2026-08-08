# Privacy & Trust Architecture

The **Vision-Based Smart Energy Saving System** is engineered with a strict **Privacy-First Architecture**.

## 1. Zero Frame Retention Policy
* **No Raw Video Storage**: Raw video frames captured from the local camera are processed strictly in volatile RAM memory.
* **Transient Memory Queue**: Frames pass through a short-lived in-memory frame buffer and are immediately discarded after YOLO object detection. No raw video bytes or images are ever saved to disk or transmitted to remote servers.

## 2. Derived Vector Telemetry
* The system extracts and broadcasts only non-sensitive, high-level vector metadata:
  - Total occupant count (integer)
  - Anonymized bounding box coordinates `[x, y, w, h]`
  - Room state (`Occupied` or `Empty`)
  - Device states and automated countdown timers

## 3. Headless Automation Mode
* For privacy-sensitive environments (e.g. private offices, bedrooms, healthcare facilities), the system provides a runtime configuration flag:
  ```yaml
  privacy:
    headless_mode: true
  ```
* When `headless_mode` is enabled:
  - MJPEG video streaming endpoints (`/api/video_feed`) are disabled.
  - Occupancy detection and automated energy-saving controls operate at 100% functionality without exposing any video feed.

## 4. Real-Time Canvas Anonymization
* When live streaming is enabled, optional face blurring / redaction can be activated:
  ```yaml
  privacy:
    anonymize_faces: true
  ```
* Person bounding regions are blurred in real-time before stream output generation.
