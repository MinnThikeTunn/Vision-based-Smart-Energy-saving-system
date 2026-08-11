# Global Subagent Orchestration: Project Judgment & Audit

**Project Target:** Vision-Based Smart Energy Saving System (`D:\cvProject`)  
**Evaluation Date:** August 2026  
**Orchestration System:** Multi-Specialist Industry Legend Roster (8 Autonomous Subagents)  

---

## 🏆 Overall Project Composite Scorecard

| Evaluator & Persona | Domain Evaluated | Score | Key Verdict |
| :--- | :--- | :---: | :--- |
| **1. Ultimate Judge** *(Linus Torvalds & John Carmack)* | Technical Perfection & Performance | **80 / 100** | High code elegance; CPU/RAM buffer churn & model optimization needed. |
| **2. QA Edgecase** *(James Bach)* | Reliability, Concurrency & Failure Modes | **58 / 100** | Multi-threading thread death, state machine deadlock & ID swaps found. |
| **3. Security Architect** *(Troy Hunt)* | Pragmatic Security & OWASP Audit | **45 / 100** | Zero auth on REST/WS endpoints; unauthenticated headless bypass. |
| **4. Frontend Architect** *(Addy Osmani & Dan Abramov)* | Frontend Architecture & Performance | **52 / 100** | Single-file 966-line monolith; layout thrashing & WS desync. |
| **5. Finance Specialist** *(Patrick Campbell & Aswath Damodaran)* | Unit Economics & Financial Modeling | **42 / 100** | Flawed 24/7 Always-ON baseline overestimates savings by 150-250%. |
| **6. UX Designer** *(Don Norman)* | Human-Centered Design & Cognitive Load | **48 / 100** | High cognitive load, split-attention navigation, ML jargon overload. |
| **7. UX Copywriter** *(Torrey Podmajersky & Joanna Wiebe)* | Microcopy, Labels & Trust Writing | **60 / 100** | Raw ML internal names in UI; report headers require humanization. |
| **8. PM Orchestrator** *(Marty Cagan)* | Product Discovery & Customer Outcomes | **40 / 100** | Engineering feature factory optimizing solutions before proving net ROI. |
| **OVERALL COMPOSITE SCORE** | **Master Weighted Score** | **53.1 / 100** | **Technically Impressive Proof-of-Concept / Enterprise Friction High** |

---

## 📌 Executive Summary of Findings

The **Vision-Based Smart Energy Saving System (v2.0)** is an engineering-heavy proof-of-concept demonstrating deep technical initiative—integrating YOLOv8 real-time detection, Centroid tracking, FastAPI REST and WebSocket endpoints, Prometheus telemetry, and dynamic ROI calculations.

However, a thorough evaluation across 8 domain specialists reveals critical gaps when transitioning from a local demo to a production-ready, commercial-grade enterprise system.

---

## 🔍 Key Domain Summary Highlights

### 1. Ultimate Technical Judge (Linus Torvalds & John Carmack) — Score: 80/100
- **Strengths:** Clean math implementations in `OccupancyStateMachine` and `EnergyCalculator` without bloated ORMs or external DAG dependencies. Clear domain separation in `CONTEXT.md`.
- **Flaws:** Memory churn (`frame.copy()` called 4–5 times per frame), static `time.sleep(0.01)` bottlenecks in `_inference_loop`, and reliance on uncompiled PyTorch models instead of ONNX FP16 runtime acceleration.

### 2. QA & Edgecase Testing (James Bach) — Score: 58/100
- **Thread Safety:** Unhandled exceptions in `pipeline.py` thread loop silently kill the worker while leaving `is_running=True`, freezing video feeds without error reporting.
- **State Machine Deadlock:** Macro 180s occupancy timeout locks out per-device micro timeouts (e.g. 5s light shutdown) until the entire macro room timeout expires.
- **Centroid Tracker ID Drops:** Greedy Euclidean distance sorting causes persistent ID swaps during occupant path crossing or fast movement.

### 3. Security Audit & OWASP Top 10 (Troy Hunt) — Score: 45/100
- **Broken Authentication (OWASP API1 & API2):** All API endpoints (`/api/config`, `/api/reports/download`, `/api/video_feed`) and WebSocket streams (`/ws/status`) operate without authentication or origin validation.
- **Headless Mode Security Bypass:** An unauthenticated attacker can send `POST /api/config` with `privacy.headless_mode: false` to remotely expose raw camera streams.
- **Zero Frame Retention:** Confirmed clean; video frames exist purely in volatile NumPy array RAM memory and are never written to disk.

### 4. Frontend Architecture (Addy Osmani & Dan Abramov) — Score: 52/100
- **Monolithic Single File:** `app/static/index.html` is a 966-line file with global variables, inline styles, and unencapsulated JS.
- **Layout Thrashing:** `innerHTML` re-renders wipe and rebuild the DOM on every WebSocket frame tick, losing input focus and causing browser layout recalcs.
- **Coordinate Projection Bug:** Canvas spatial ROI drawing normalizes coordinates against client dimensions rather than intrinsic video element bounds under `object-contain`.

### 5. Finance & Unit Economics (Patrick Campbell & Aswath Damodaran) — Score: 42/100
- **Baseline Fallacy:** Calculating savings against a 24/7/365 Always-ON baseline overstates financial savings by 150%–250% in real commercial spaces with existing schedules or manual habits.
- **Parasitic Edge Compute Load:** A GPU/CPU edge server drawing ~30W continuously consumes 0.72 kWh/day ($0.108/day), which can exceed the energy saved turning off low-wattage LED lights (40W).
- **Payback Realism:** Factoring $335/room installed CapEx and realistic commercial usage extends the simple payback period from 1.17 years to **3.13 years**.

### 6. Human-Centered UX (Don Norman) — Score: 48/100
- **Split-Attention Navigation:** Separating live controls (Page 1) from configuration settings (Page 2) forces users to switch back and forth to observe tuning impact.
- **Jargon Overload:** Terms like `Elapsed Zero Count`, `YOLO Confidence Threshold`, and `Persistence Window` alienate facilities managers.

### 7. Microcopy & Trust Writing (Torrey Podmajersky & Joanna Wiebe) — Score: 60/100
- Replaced ambiguous button microcopy (`Toggle`) with explicit action verbs (`Turn On` / `Turn Off`).
- Humanized CSV report headers from all-caps machine syntax into enterprise executive summaries.

### 8. Product Discovery & Outcomes (Marty Cagan) — Score: 40/100
- **Feature Factory Risk:** 8-phase roadmap optimizes tech features (pose keypoints, synthetic power ramps) before validating privacy compliance and net customer ROI with target buyers.

---

## 🛠️ Prioritized Engineering Action Plan

1. **Security & Authentication (High Priority)**: Add API key / JWT authentication middleware to FastAPI routes and WebSocket handshakes; enforce immutable server-side headless mode overrides.
2. **Net Energy Formula Revision (High Priority)**: Subtract edge computer power consumption ($\text{Net Savings} = \text{Baseline} - \text{Actual} - \text{Edge Compute Overhead}$) and implement scheduled operational window masks.
3. **Threading & Concurrency Resilience (High Priority)**: Add try-except wrapper with health logging inside `pipeline.py` inference loop, and separate micro-device timeouts from macro room occupancy state timeouts.
4. **Frontend Modularization (Medium Priority)**: Split `index.html` into CSS/JS modules, implement keyed DOM diffing updates for WebSockets, and fix Canvas `object-contain` coordinate math.
5. **Usability & Copy Humanization (Medium Priority)**: Replace ML technical jargon in dashboard controls with clear facilities terminology (*Detection Sensitivity*, *Presence Verification Delay*, *Turn Off*).

---

*Full individual specialist review documents are available in the [`notes/`](file:///D:/cvProject/notes/) folder.*
