# Security & OWASP Audit Report: Vision-Based Smart Energy Saving System

**Auditor:** Troy Hunt (Security & OWASP Audit Persona)  
**Target Repository:** `D:\cvProject`  
**Date:** August 9, 2026  

---

## Executive Summary

A pragmatic zero-trust and OWASP audit of the **Vision-Based Smart Energy Saving System** reveals that while the project succeeds in maintaining a **Zero Frame Retention** architecture in RAM memory, it suffers from critical security gaps in authentication, access control, WebSocket input validation, and privacy enforcement.

The fundamental design flaw is the **complete absence of authentication and access control** across all REST and WebSocket interfaces. As a result, privacy features such as "Headless Mode" act merely as client UI toggles rather than secure boundaries, because any unauthenticated client on the network can mutate system settings, re-enable raw video streaming, issue arbitrary manual device overrides, or extract operational telemetry logs.

---

## 1. API Security Audit

### 1.1 Broken Authentication & Authorization (OWASP API1:2023 & OWASP API2:2023)
* **Location:** [`config_router.py`](file:///D:/cvProject/app/api/config_router.py), [`video_router.py`](file:///D:/cvProject/app/api/video_router.py)
* **Finding:** All REST routes (`GET /api/config`, `POST /api/config`, `GET /api/config/audit_logs`, `GET /api/reports/download`, `GET /api/reports/iot_handoff`, `GET /api/video_feed`) lack authentication middleware, API key checks, or role-based access controls.
* **Risk:** Any anonymous user on the network can view or modify core system parameters (such as YOLO detection confidence thresholds, device timeouts, or privacy flags).

### 1.2 Unsanitized Exception & Information Disclosure (OWASP API3:2023)
* **Location:** [`config_router.py:L34-L35`](file:///D:/cvProject/app/api/config_router.py#L34-L35)
* **Code Snippet:**
  ```python
  except Exception as e:
      raise HTTPException(status_code=400, detail=str(e))
  ```
* **Finding:** Catching generic `Exception` and passing `str(e)` directly into `HTTPException(status_code=400, ...)` leaks raw internal backend stack traces and error details to unauthenticated HTTP clients.

### 1.3 Path Traversal & Report Downloads Analysis
* **Location:** [`config_router.py:L43-L76`](file:///D:/cvProject/app/api/config_router.py#L43-L76)
* **Finding:** The `/api/reports/download` and `/api/reports/iot_handoff` routes generate content dynamically in memory or return predefined markdown text using static, server-generated filenames (`facilities_report_<timestamp>.csv` and `iot_hardware_handoff_report.md`).
* **Verdict:** **No Path Traversal vulnerability exists** in report generation because no user-controlled file paths are accepted. However, because these endpoints lack authentication, proprietary facilities telemetry and energy metrics are exposed publicly.

---

## 2. WebSocket Security Audit

### 2.1 Unauthenticated WebSocket Connection Handshake (OWASP API2:2023)
* **Location:** [`ws_router.py:L152-L176`](file:///D:/cvProject/app/api/ws_router.py#L152-L176)
* **Finding:** The `/ws/status` endpoint accepts connections (`await manager.connect(websocket)`) without verifying authorization tokens, cookies, or origin headers.

### 2.2 Lack of Rate Limiting & Denial of Service (DoS) Risks (OWASP API4:2023)
* **Location:** [`ws_router.py:L28-L46`](file:///D:/cvProject/app/api/ws_router.py#L28-L46), [`ws_router.py:L157-L175`](file:///D:/cvProject/app/api/ws_router.py#L157-L175)
* **Finding:**
  - `ConnectionManager` has no ceiling on total active connections.
  - The telemetry broadcast loop runs continuously without backpressure or per-client message throttling.
  - A malicious actor can initiate hundreds of simultaneous WebSocket connections to exhaust server resources and CPU capacity.

### 2.3 Unvalidated Inbound Control Messages & Arbitrary Override (OWASP API8:2023)
* **Location:** [`ws_router.py:L160-L169`](file:///D:/cvProject/app/api/ws_router.py#L160-L169)
* **Finding:** Incoming WebSocket messages bypass schema validation. `device_id` and `target_state` are injected directly into `set_device_state` without whitelist validation against configured devices or valid device states (`ON`, `OFF`, `DIM`). An attacker can send arbitrary string parameters to tamper with device states.

---

## 3. Camera Feed & Privacy Architecture Audit

### 3.1 Unauthenticated MJPEG Video Feed Exposure
* **Location:** [`video_router.py:L62-L95`](file:///D:/cvProject/app/api/video_router.py#L62-L95)
* **Finding:** `/api/video_feed` streams live video frames over HTTP (`multipart/x-mixed-replace`) without authentication or encryption.

### 3.2 Headless Mode Security Bypass
* **Location:** [`video_router.py:L68-L89`](file:///D:/cvProject/app/api/video_router.py#L68-L89), [`config_router.py:L18-L35`](file:///D:/cvProject/app/api/config_router.py#L18-L35)
* **Finding:** While `headless_mode = true` replaces live camera feeds with a placeholder static image, an unauthenticated attacker can send a `POST /api/config` request with `privacy.headless_mode = false`, immediately turning off Headless Mode and gaining full access to live video streaming.

### 3.3 Privacy Blurring Efficacy & Detection Failure Vulnerability
* **Location:** [`pipeline.py:L92-L106`](file:///D:/cvProject/app/detector/pipeline.py#L92-L106), [`pipeline.py:L118-L119`](file:///D:/cvProject/app/detector/pipeline.py#L118-L119)
* **Finding:**
  1. Anonymization relies 100% on object detector bounding boxes (`if self.anonymize_faces and len(boxes) > 0`). If YOLO fails to detect an occupant (e.g. low confidence, partial occlusion, poor lighting), the un-anonymized raw frame is broadcast in the MJPEG stream.
  2. Blur is applied to the entire person bounding box using Gaussian blur. If bounding box coordinates are misaligned or detection skips the head area, personal identifiers remain visible.

### 3.4 Zero Frame Retention Verification
* **Location:** [`pipeline.py:L26-L37`](file:///D:/cvProject/app/detector/pipeline.py#L26-L37), [`docs/privacy.md`](file:///D:/cvProject/docs/privacy.md)
* **Verification Results:**
  - **Confirmed:** Video frames exist exclusively in transient volatile memory (`self._raw_frame` and `self._processed_frame` NumPy arrays in RAM).
  - No frame writing operations (`cv2.imwrite`, filesystem logging, or external storage uploads) exist in `VisionPipeline`.

---

## 4. System Hardening & Operational Vulnerabilities

### 4.1 Missing CORS Middleware & Security Headers
* **Location:** [`main.py:L10-L13`](file:///D:/cvProject/app/main.py#L10-L13)
* **Finding:** The FastAPI instance does not declare `CORSMiddleware` or HTTP security headers (`Content-Security-Policy`, `X-Content-Type-Options`, `X-Frame-Options`, `Strict-Transport-Security`).

### 4.2 Concurrency & Audit Log Mutation Race Conditions
* **Location:** [`config_router.py:L10`](file:///D:/cvProject/app/api/config_router.py#L10), [`config_router.py:L24-L31`](file:///D:/cvProject/app/api/config_router.py#L24-L31)
* **Finding:** `_config_audit_logs` is a plain global Python list modified in `update_config` without thread locking.

---

## Pragmatic Remediation Checklist

| Priority | Vulnerability / Area | Mandatory Action |
| :--- | :--- | :--- |
| **CRITICAL** | Broken Authentication | Add JWT / API Key authentication middleware across all REST endpoints and WebSockets. |
| **HIGH** | Unvalidated WS Messages | Validate incoming `TOGGLE_DEVICE` payloads with Pydantic schemas and strict whitelist checking. |
| **HIGH** | Headless Mode Bypass | Protect `POST /api/config` with admin authentication so privacy toggles cannot be overridden. |
| **MEDIUM** | Error Leakage | Sanitize exception handling in `config_router.py` to prevent stack trace disclosure. |
| **MEDIUM** | System Hardening | Configure CORS middleware with restricted origins and add standard HTTP security headers. |
